# v2v-simulator
Project Overview:
This simulator models V2V communication networks for vehicles broadcasting Basic Safety Messages (BSM) and Collision Warning Messages (CWM) to prevent accidents. 
THe system includes realistic vehicle dynamics, network protocol simulation and a real-time visualization.
Core Question: How do mobile ad-hoc networks (MANETs) handle ultra-low latency requirements when network topology changes every second at highway speeds?

Core Simuulation:
10 vehicles in highway scenarios
Realistic vehicle dynamics with accelerations and deceleration
Collosion detection and avoidance using calculations

Communication Protocol:
Basic Safety Messages (BSM): Position/speed/ broadcasts every 100ms 
Collision Warning Messages (CWM): High-priority emergency alerts
Message prioritization: CWM messages trasnmit within 5ms, and never dropped

3D VIsualization:
Sprite renderer using PyOpenGL

Prerequisites:
PyOpenGL

# Clone repository
git clone https://github.com/<USERNAME>/v2v-simulator.git
cd v2v-simulator

# Simulation parameters
VEHICLE_COUNT = 10-15
TRANSMISSION_RANGE = 300       # meters
BSM_FREQUENCY = 10             # Hz
SAFE_GAP = 15                  # meters
TTC_COLLISION_THRESHOLD = 3.0  # seconds
