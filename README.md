# v2v-simulator

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
