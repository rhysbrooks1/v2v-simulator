from dataclasses import dataclass, field 

@dataclass(order=True)
class Message:
    priority: int = field(init=False) 
    timestamp: float
    sender_id: int

@dataclass(order=True)
class BSM(Message):
    """Basic Safety Message"""
    position: float
    velocity: float
    acceleration: float
    
    def __post_init__(self):

        # Second most important
        self.priority = 1

@dataclass(order=True)
class CWM(Message):
    """Collision Warning Message"""
    ttc: float
    target_id: int
    
    def __post_init__(self):

        # 0 means most important
        self.priority = 0