import inspect

from sunbot.core.llm import (
    StructuredOutputGeneration,
    TextGeneration,
    TextStreaming,
)


def test_text_generation_is_abstract() -> None:
    assert inspect.isabstract(TextGeneration)
    assert {"generate_text"} <= TextGeneration.__abstractmethods__  # type: ignore[missing-attribute]


def test_text_streaming_is_abstract() -> None:
    assert inspect.isabstract(TextStreaming)
    assert {"stream_text"} <= TextStreaming.__abstractmethods__  # type: ignore[missing-attribute]


def test_structured_output_generation_is_abstract() -> None:
    assert inspect.isabstract(StructuredOutputGeneration)
    assert {"generate_output"} <= StructuredOutputGeneration.__abstractmethods__  # type: ignore[missing-attribute]
