from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class Serializable(Protocol):
    @abstractmethod
    def serialize(self) -> bytes: ...


@runtime_checkable
class Deserializable[T](Protocol):
    @classmethod
    @abstractmethod
    def deserialize(cls, data: bytes) -> T: ...
