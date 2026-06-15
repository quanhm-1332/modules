def test_import() -> None:
    import sunbot.sdk.llm.openai as module

    assert module is not None
