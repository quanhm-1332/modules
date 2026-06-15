from sunbot.std import Deserializable, Serializable


class TestSerde:
    def test_serializable_runtime_checkable(self) -> None:
        class Doc:
            def serialize(self) -> bytes:
                return b"x"

        assert isinstance(Doc(), Serializable)
        assert not isinstance(object(), Serializable)

    def test_deserializable_runtime_checkable(self) -> None:
        class Doc:
            @classmethod
            def deserialize(cls, data: bytes) -> "Doc":
                return cls()

        assert isinstance(Doc(), Deserializable)
        assert not isinstance(object(), Deserializable)
