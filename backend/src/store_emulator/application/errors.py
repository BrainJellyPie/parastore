from typing import overload


class AppError(Exception):
    """Business-rule violation. Supports two call shapes:

    - Legacy: ``AppError(message, status_code=400)`` — code/reason default.
    - spec rev 4 §4.1: ``AppError(status_code, code, reason, message, details=None)``.

    Attributes:
        status_code: HTTP status code.
        code: stable identifier (e.g. "setup_not_found", "racks_locked").
        reason: category (e.g. "not_found", "items_exist").
        message: user-facing message.
        details: structured context.
    """

    status_code: int
    code: str
    reason: str
    message: str
    details: dict[str, object]

    @overload
    def __init__(self, message: str, status_code: int = 400, /) -> None: ...

    @overload
    def __init__(
        self,
        status_code: int,
        code: str,
        reason: str,
        message: str,
        details: dict[str, object] | None = None,
        /,
    ) -> None: ...

    def __init__(  # type: ignore[misc]
        self,
        first: int | str,
        second: str | int = 400,
        reason: str | None = None,
        message: str = "",
        details: dict[str, object] | None = None,
    ) -> None:
        if isinstance(first, str):
            self.message = first
            self.status_code = second if isinstance(second, int) else 400
            self.code = "app_error"
            self.reason = "error"
            self.details = {}
        else:
            if not isinstance(second, str):
                raise TypeError("code must be str when status_code is int")
            if reason is None:
                raise TypeError("reason required for 5-arg form")
            self.status_code = first
            self.code = second
            self.reason = reason
            self.message = message
            self.details = details if details is not None else {}
        super().__init__(self.message)
