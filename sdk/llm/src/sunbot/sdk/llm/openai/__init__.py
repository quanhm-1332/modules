"""sunbot.sdk.llm.openai — backend implementation.

Implement the org.core.<feature> protocol(s): stateless + injected
client; stateful parts as a resource (initialize/cleanup). When you
add the third-party SDK: declare it as the named extra in pyproject
and wrap the SDK import in a lazy-import guard. See final-proposal C1.
"""


class OpenAI: ...


__all__: list[str] = []
