from dataclasses import dataclass

@dataclass
class BSM:
    sender: int
    x: float
    y: float
    speed: float


@dataclass
class CWM:
    sender: int
    x: float
    y: float
    ttc: float
