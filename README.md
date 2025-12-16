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

```console
usage: main.py [-h] [-v VEHICLE_COUNT] [-s VEHICLE_SCALE] [-l LATENCY] [-p PACKET_LOSS]

Simulates a highway scenario where fully autonomous vehicles communicate with each other to avoid collisions

options:
  -h, --help            show this help message and exit
  -v, --vehicle-count VEHICLE_COUNT
  -s, --vehicle-scale VEHICLE_SCALE
  -l, --latency LATENCY
                        packet latency in ms
  -p, --packet-loss PACKET_LOSS
                        percentage of packets lost
```

## Scenarios
- Default: python3 src/v2v/main.py
- Chaotic, 50% packet loss: python3 src/v2v/main.py -v 20 -s 0.5 -p 0.5
  - Demonstrates that the network protocol can handle a large amount of BSM packet loss without causing collisions.
- Broken, 300ms latency: python3 src/v2v/main.py -v 20 -s 0.5 -l 300
  - Demonstrates that the network protocol relies on low latency, less than 300ms, in order to effectively avoid collisions.
