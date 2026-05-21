import hashlib
import logging
import threading

import instructor
import litellm
from pydantic import BaseModel

from store_emulator.domain.config import LLMConfig
from store_emulator.domain.types import TokenUsage

logger = logging.getLogger(__name__)


def _hash6(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:4]


class LiteLLMClient:

    def __init__(self, config: LLMConfig):
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self._client = instructor.from_litellm(litellm.completion, mode=instructor.Mode.JSON)  # type: ignore[reportUnknownMemberType]
        self._async_client = instructor.from_litellm(litellm.acompletion, mode=instructor.Mode.JSON)  # type: ignore[reportUnknownMemberType]
        self._usage_lock = threading.Lock()
        self._usage = TokenUsage()

    def _messages(self, system_prompt: str, user_prompt: str) -> tuple[list[dict[str, str]], str]:
        rid = _hash6(system_prompt + user_prompt)
        logger.info(f"{self.model} [{rid}] req {len(system_prompt) + len(user_prompt):,}chars")
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], rid

    def _messages_with_image(
        self,
        system_prompt: str,
        user_prompt: str,
        image_url: str,
    ) -> tuple[list[dict[str, object]], str]:
        rid = _hash6(system_prompt + user_prompt)
        logger.info(f"{self.model} [{rid}] req {len(system_prompt) + len(user_prompt):,}chars +image")
        return [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ], rid

    def _accumulate_usage(self, raw_response: object, rid: str) -> None:
        usage = getattr(raw_response, "usage", None)
        if usage is None:
            return
        prompt = getattr(usage, "prompt_tokens", 0) or 0
        completion = getattr(usage, "completion_tokens", 0) or 0
        total = getattr(usage, "total_tokens", 0) or 0
        logger.info(f"{self.model} [{rid}] in={prompt} out={completion}")

        with self._usage_lock:
            self._usage.prompt_tokens += prompt
            self._usage.completion_tokens += completion
            self._usage.total_tokens += total

    def get_usage(self) -> TokenUsage:
        with self._usage_lock:
            return self._usage.model_copy()

    def reset_usage(self) -> None:
        with self._usage_lock:
            self._usage = TokenUsage()

    def generate_structured[T: BaseModel](
        self,
        response_model: type[T],
        system_prompt: str,
        user_prompt: str,
        *,
        max_retries: int = 1,
    ) -> T:
        msgs, rid = self._messages(system_prompt, user_prompt)
        model, raw = self._client.chat.completions.create_with_completion(  # type: ignore[reportUnknownMemberType]
            model=self.model,
            response_model=response_model,
            messages=msgs,  # type: ignore[reportArgumentType]
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_retries=max_retries,
        )
        self._accumulate_usage(raw, rid)
        return model  # type: ignore[reportReturnType]

    async def generate_structured_async[T: BaseModel](
        self,
        response_model: type[T],
        system_prompt: str,
        user_prompt: str,
        *,
        max_retries: int = 1,
    ) -> T:
        msgs, rid = self._messages(system_prompt, user_prompt)
        model, raw = await self._async_client.chat.completions.create_with_completion(  # type: ignore[reportUnknownMemberType]
            model=self.model,
            response_model=response_model,
            messages=msgs,  # type: ignore[reportArgumentType]
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            max_retries=max_retries,
        )
        self._accumulate_usage(raw, rid)
        return model  # type: ignore[reportReturnType]

    def generate_structured_with_image[T: BaseModel](
        self,
        response_model: type[T],
        system_prompt: str,
        user_prompt: str,
        image_url: str,
    ) -> T:
        msgs, rid = self._messages_with_image(system_prompt, user_prompt, image_url)
        model, raw = self._client.chat.completions.create_with_completion(  # type: ignore[reportUnknownMemberType]
            model=self.model,
            response_model=response_model,
            messages=msgs,  # type: ignore[reportArgumentType]
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        self._accumulate_usage(raw, rid)
        return model  # type: ignore[reportReturnType]

    async def generate_structured_with_image_async[T: BaseModel](
        self,
        response_model: type[T],
        system_prompt: str,
        user_prompt: str,
        image_url: str,
    ) -> T:
        msgs, rid = self._messages_with_image(system_prompt, user_prompt, image_url)
        model, raw = await self._async_client.chat.completions.create_with_completion(  # type: ignore[reportUnknownMemberType]
            model=self.model,
            response_model=response_model,
            messages=msgs,  # type: ignore[reportArgumentType]
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        self._accumulate_usage(raw, rid)
        return model  # type: ignore[reportReturnType]

    async def generate_text_async(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        enable_search: bool = False,
    ) -> str:
        """Bypass Instructor — raw text completion. Use when the schema varies by
        category and we need ad-hoc JSON output.

        enable_search=True enables the Gemini Search Grounding tool
        (Phase 0 spike confirmed `tools=[{"google_search": {}}]` works).
        Non-Gemini models may ignore it or raise BadRequest — caller must branch.
        """
        msgs, rid = self._messages(system_prompt, user_prompt)
        kwargs: dict[str, object] = {
            "model": self.model,
            "messages": msgs,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if enable_search:
            kwargs["tools"] = [{"google_search": {}}]
        raw = await litellm.acompletion(**kwargs)  # type: ignore[reportUnknownMemberType]
        self._accumulate_usage(raw, rid)
        choices: list[object] = list(getattr(raw, "choices", None) or [])
        if not choices:
            return ""
        first: object = choices[0]
        msg: object = getattr(first, "message", None)
        return str(getattr(msg, "content", "") or "")
