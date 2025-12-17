# v2v-simulator
## Team Members and contributions
- Nic Ball: Built the arrow, line, sprite, and emission effects renderers. Built the original vehicle physics behavior. Added command line argument parsing to parameterize variables.
- Rhys Brooks: Worked on highway.py (spawning logic), messages.py (CWM and BSM).
- Rene Hermosillo: Worked on ui_statistics.py and display panel to the screen in main.py.
- William Ostrum: Worked on collision avoidance and braking for the vehicles in main.py as well as trying to get vehicle speeds to function more fluidly in both vehicle.py and main.py.

## Features
- Configurable number of vehicles in a highway scenario
- Configurable packet loss and latency
- Vehicle physics with acceleration, velocity, and position
- Collosion avoidance
- OpenGL renderer for visualizing the highway scenario

## Communication Protocol
- Basic Safety Messages (BSM): Position/velocity broadcasts every 100ms 
- Collision Warning Messages (CWM): High-priority emergency alerts
- Message prioritization: CWM messages transmit within 5ms, and never dropped

## Usage
- -h flag it will give usage information in terminal

```console
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ python3 src/v2v/main.py -h
```

## Scenarios
- Default: `python3 src/v2v/main.py`
- High packet loss: `python3 src/v2v/main.py -s 0.5 -p 0.7`
- High BSM packet latency: `python3 src/v2v/main.py -s 0.5 -l 300`

## Known Problem
The most significant problem with the project is that vehicles near the edges of the screen do not communicate with each other. Specifically, a vehicle at the top of the screen can not see if a vehicle at the bottom of the screen is stopped. As the number of vehicles increases, the gap between vehicles decreases, meaning that the duration that a vehicle has to react to a stopped vehicle immediately after it moves from the top to the bottom of the screen is smaller. As a result, at around ~20-25 cars you will start to observe vehicles racing over the top of one another. This isn't necessarily a problem with the network protocol and instead a limitation in the engine. As such, we are not concerned about fixing it.
