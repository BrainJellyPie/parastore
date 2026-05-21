from dotenv import load_dotenv

from store_emulator.domain.config import LLMConfig, SimulationConfig

load_dotenv()


def local_config() -> SimulationConfig:
    return SimulationConfig(
        llm=LLMConfig(model="gemini/gemini-3.1-pro-preview"),
    )
