"""Error standards for the platform.

A single error root plus the canonical infra/application error shapes every
component reuses, so the platform speaks one error vocabulary.
"""

import traceback
from dataclasses import dataclass


@dataclass
class PlatformError(Exception):
    """Root of all platform-level (infrastructure) errors."""

    msg: str
    service: str


class WorkerDown(PlatformError): ...


class ServiceDown(PlatformError): ...


class NetworkError(PlatformError):
    """A failure talking to an external service or resource."""

    def format_traceback(self) -> str:
        return "".join(traceback.format_exception(type(self), self, self.__traceback__))


@dataclass
class ApplicationError(Exception):
    """Root of business/application errors that map onto an HTTP status.

    Subclasses set ``status_code`` (or override ``to_http_status_code``) to
    surface the right response code; the base maps to 500.
    """

    status_code: int = 500

    def to_http_status_code(self) -> int:
        return self.status_code


"""default_exception_handlers: (exc: Exception) -> ()"""
