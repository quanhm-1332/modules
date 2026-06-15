from dataclasses import dataclass


@dataclass
class RunOutput[OutputDataT = str]:
    output: OutputDataT


@dataclass
class StreamOutput:
    delta: str
    output: str
