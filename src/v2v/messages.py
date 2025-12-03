from dataclasses import dataclass, field
import numpy as np


@dataclass(order=True)
class Message:
    priority: int = field(init=False)
    timestamp: float
    sender_id: int


@dataclass(order=True)
class BSM(Message):
    """Basic Safety Message"""

    acceleration: np.float32
    velocity: np.float32
    position: np.array

    def __post_init__(self):
        # Second most important
        self.priority = 1


@dataclass(order=True)
class CWM(Message):
    """Collision Warning Message"""

    target_id: int
    ttc: float

    def __post_init__(self):
        # 0 means most important
        self.priority = 0

