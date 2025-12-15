# v2v-simulator
Project Overview:
This simulator models V2V communication networks for vehicles broadcasting Basic Safety Messages (BSM) and Collision Warning Messages (CWM) to prevent accidents. 
THe system includes realistic vehicle dynamics, network protocol simulation and a real-time visualization.
Core Question: How do mobile ad-hoc networks (MANETs) handle ultra-low latency requirements when network topology changes every second at highway speeds?

Dependencies are listed in requirements.txt.

Core Simulation:
10 vehicles in highway scenarios
Realistic vehicle dynamics with accelerations and deceleration
Collosion detection and avoidance using calculations

Communication Protocol:
Basic Safety Messages (BSM): Position/speed/ broadcasts every 100ms 
Collision Warning Messages (CWM): High-priority emergency alerts
Message prioritization: CWM messages transmit within 5ms, and never dropped
