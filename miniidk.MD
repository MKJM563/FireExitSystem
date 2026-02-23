# Prototype Software Requirements Specification (SRS)

## SmartExit™ Fire Evacuation System - Python Simulation Prototype
**Advanced Programming MK6004-25-A25**

---

## Document Information

**Project Name:** SmartExit™ Prototype (Simulation)  
**Document Version:** 1.0  
**Date:** 2026-02-03  
**Author:** MKJM563  
**Status:** Active  
**Development Timeline:** 3-4 weeks

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Prototype Scope](#2-prototype-scope)
3. [System Architecture](#3-system-architecture)
4. [Functional Requirements](#4-functional-requirements)
5. [Technical Specifications](#5-technical-specifications)
6. [Implementation Priorities](#6-implementation-priorities)

---

## 1. Introduction

### 1.1 Purpose

This document defines the requirements for a **basic simulation prototype** of the SmartExit™ Fire Evacuation System. The prototype demonstrates core concepts from the full SRS through a Python-based simulation with no physical hardware requirements.

### 1.2 Prototype Objectives

1. **Demonstrate dynamic routing algorithms** that adapt to fire/smoke hazards
2. **Simulate decentralized node communication** using pub/sub messaging
3. **Visualize system behavior** through a web-based dashboard
4. **Validate floorplan parsing and node placement** mechanisms
5. **Provide foundation** for future hardware integration

### 1.3 Out of Scope

The following features from the full SRS are **NOT included** in this prototype:
- Physical hardware integration
- Battery backup systems
- Multi-floor buildings
- External system integration (BMS, fire alarms, access control)
- User authentication/security
- Persistent data storage/logging
- Mobile applications
- Firmware update mechanisms
- Real-time performance constraints (<2s routing is best-effort, not guaranteed)

---

## 2. Prototype Scope

### 2.1 What This Prototype IS

- ✅ **Fully simulated in Python** - All devices (exit signs, smoke alarms) are software objects
- ✅ **Decentralized architecture** - Nodes communicate via pub/sub, no central coordinator required
- ✅ **Single-floor buildings only** - Simplified topology
- ✅ **Two device types**: Exit signs and smoke alarms
- ✅ **Web-based visualization** - HTML dashboard on localhost
- ✅ **Algorithm-focused** - Emphasis on routing logic and graph-based pathfinding
- ✅ **Manual hazard injection** - User triggers simulated fires for testing

### 2.2 Key Demonstrations

| Capability | Demo Scenario |
|------------|---------------|
| Dynamic routing | Fire blocks primary exit → system recalculates alternate routes |
| Decentralized coordination | Nodes share hazard info via messages → local route decisions |
| Confidence scoring | Failed nodes → reduced confidence on affected routes |
| Load balancing | Multiple exits → system distributes evacuees evenly |
| Floorplan parsing | Load JSON floorplan → auto-generate graph + place devices |

---

## 3. System Architecture

### 3.1 Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Web Dashboard                        │
│              (Flask Server + HTML/JS)                   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP API
┌────────────────────▼────────────────────────────────────┐
│              Simulation Engine                          │
│  - Event loop                                           │
│  - Hazard injection                                     │
│  - Timestep coordination                                │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼────────┐       ┌────────▼────────┐
│  Message Bus   │◄──────┤ Building Graph  │
│   (Pub/Sub)    │       │   (NetworkX)    │
└───────┬────────┘       └────────┬────────┘
        │                         │
        │         ┌───────────────┘
        │         │
┌───────▼─────────▼────────────────────────┐
│          Simulated Devices               │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Exit Signs  │  │  Smoke Alarms   │  │
│  └──────────────┘  └─────────────────┘  │
└──────────────────────────────────────────┘
```

### 3.2 Data Flow

1. **Initialization:**
   - Load floorplan JSON → Build graph → Create device instances → Setup pub/sub subscriptions

2. **Normal Operation:**
   - Devices publish periodic status messages → Neighbors update local state

3. **Emergency Event:**
   - User injects hazard via dashboard → Smoke alarm detects → Publishes alert
   - Exit signs receive alert → Update graph weights → Recalculate routes
   - Display states update → Dashboard refreshes visualization

---

## 4. Functional Requirements

### 4.1 Building Representation

**PR-FR-4.1.1** The system SHALL represent buildings as weighted directed graphs where:
- Vertices = rooms, corridors, exits
- Edges = navigable paths with attributes (distance, safety_score, accessibility)

**PR-FR-4.1.2** Graph SHALL be created from JSON floorplan files containing:
- Node definitions (id, type, coordinates, name)
- Edge definitions (from, to, distance, bidirectional flag)
- Device placement (exit_signs, smoke_alarms)

**PR-FR-4.1.3** The system SHALL support the following node types:
- `room`: Interior spaces
- `corridor`: Connecting passages
- `exit`: Building exits (graph termination points)

### 4.2 Simulated Devices

#### 4.2.1 Exit Signs

**PR-FR-4.2.1** Each simulated ExitSign SHALL have:
- Unique node ID
- Physical location (graph node reference)
- Display state: `normal`, `evacuation`, `hazard_warning`, `blocked`
- Current direction arrow (null, "N", "S", "E", "W", or pointing to next node)
- Distance to nearest safe exit
- Route confidence score (0-100%)

**PR-FR-4.2.2** Exit signs SHALL display the following information:
- **Normal mode:** "EXIT" symbol (static)
- **Evacuation mode:** Arrow + distance (e.g., "→ 15m")
- **Hazard mode:** Warning + alternate direction
- **Blocked mode:** "DO NOT ENTER" + alternate direction

**PR-FR-4.2.3** Exit signs SHALL update displays when:
- Evacuation triggered
- Hazard detected on current route
- Route confidence drops below 60%
- Neighboring node fails

#### 4.2.2 Smoke Alarms

**PR-FR-4.2.4** Each simulated SmokeAlarm SHALL have:
- Unique node ID
- Physical location (graph node reference)
- Smoke level (0-100)
- Temperature (°C)
- Hazard classification (0-4)

**PR-FR-4.2.5** Hazard levels SHALL be classified as:
- **Level 0 (Normal):** Smoke < 10, Temp < 30°C
- **Level 1 (Monitoring):** Smoke 10-30, Temp 30-45°C
- **Level 2 (Caution):** Smoke 30-60, Temp 45-60°C
- **Level 3 (Danger):** Smoke 60-90, Temp 60-80°C
- **Level 4 (Impassable):** Smoke > 90, Temp > 80°C

**PR-FR-4.2.6** Smoke alarms SHALL publish hazard alerts when:
- Hazard level increases
- Level reaches 2 or higher
- Temperature increases by >10°C in one timestep

### 4.3 Routing Algorithm

**PR-FR-4.3.1** The system SHALL implement a safety-aware pathfinding algorithm based on Dijkstra's or A* with modified edge weights.

**PR-FR-4.3.2** Edge weights SHALL be calculated as:
```
weight = base_distance × safety_multiplier

where safety_multiplier:
- Hazard Level 0-1: 1.0 (normal)
- Hazard Level 2: 5.0 (avoid if possible)
- Hazard Level 3+: ∞ (impassable)
```

**PR-FR-4.3.3** Routes SHALL prioritize (in order):
1. Safety (avoid hazards)
2. Confidence (prefer routes with operational nodes)
3. Distance (shorter is better)

**PR-FR-4.3.4** The system SHALL calculate route confidence as:
```
confidence = 100 × (operational_nodes_on_route / total_nodes_on_route)
               × (1 - max_hazard_level_on_route / 4)
```

**PR-FR-4.3.5** If all routes to exits have confidence < 30%, the system SHALL:
- Display "NO SAFE ROUTE - SEEK REFUGE"
- Log event for post-simulation analysis

**PR-FR-4.3.6** When multiple safe routes exist to different exits, the system SHALL distribute evacuees by:
- Alternating recommendations (simple round-robin)
- OR prioritizing least-recently-used exit (optional enhancement)

### 4.4 Decentralized Communication

**PR-FR-4.4.1** The system SHALL implement a pub/sub message bus for node communication.

**PR-FR-4.4.2** Message types SHALL include:
- `hazard_alert`: Smoke alarm reports fire/smoke (contains: node_id, hazard_level, timestamp)
- `route_update`: Exit sign shares calculated route (contains: node_id, next_hop, confidence)
- `node_status`: Periodic heartbeat (contains: node_id, operational_status, battery_level)
- `evacuation_trigger`: System-wide evacuation activation

**PR-FR-4.4.3** Nodes SHALL subscribe to messages from:
- Direct neighbors (1-hop connectivity)
- Broadcast channel (system-wide events)

**PR-FR-4.4.4** Upon receiving a hazard alert, exit signs SHALL:
1. Update local graph representation
2. Recalculate route to nearest exit
3. Publish route_update to neighbors
4. Update display state

**PR-FR-4.4.5** The message bus SHALL support:
- Topic-based subscriptions
- Broadcast to all nodes
- Direct node-to-node messaging (optional)

### 4.5 Simulation Control

**PR-FR-4.5.1** Users SHALL be able to:
- Load floorplan from JSON file
- Start/pause/reset simulation
- Trigger evacuation mode
- Inject hazards at specific locations
- Simulate node failures

**PR-FR-4.5.2** Hazard injection SHALL allow specification of:
- Target node ID
- Hazard type (fire, smoke)
- Initial intensity (0-100)
- Spread rate (optional: intensity increase per timestep)

**PR-FR-4.5.3** The simulation SHALL progress in discrete timesteps where each step:
1. Updates sensor readings (hazard spread)
2. Processes message queue
3. Triggers route recalculations (if needed)
4. Updates device display states
5. Logs events

**PR-FR-4.5.4** Timestep duration SHALL be configurable (default: 1 second simulated time per step).

### 4.6 Visualization Dashboard

**PR-FR-4.6.1** The web dashboard SHALL display:
- 2D floorplan with nodes positioned by coordinates
- Device icons (different colors for exit signs vs smoke alarms)
- Hazard indicators (red overlay on affected nodes)
- Active evacuation routes (arrows between nodes)
- Per-node status panel (selected node details)

**PR-FR-4.6.2** The dashboard SHALL provide controls for:
- Loading floorplan files
- Starting evacuation
- Injecting hazards (click-on-node interface)
- Simulating node failures
- Adjusting simulation speed

**PR-FR-4.6.3** The dashboard SHALL update in real-time by:
- Polling `/api/status` endpoint every 1 second, OR
- Using WebSocket for live updates (optional enhancement)

**PR-FR-4.6.4** Node status panel SHALL show (for selected node):
- Node ID and type
- Device type (if equipped)
- Current display state (for exit signs)
- Sensor readings (for smoke alarms)
- Route confidence (for exit signs)
- Next hop in evacuation route

---

## 5. Technical Specifications

### 5.1 Programming Language & Libraries

**Language:** Python 3.9+

**Required Libraries:**
```python
networkx>=3.0      # Graph operations and pathfinding
flask>=3.0         # Web server for dashboard
```

**Optional Libraries:**
```python
matplotlib>=3.5    # Static graph visualization (debugging)
pytest>=7.0        # Unit testing
```

### 5.2 Project Structure

```
FireExitSystem/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── graph.py          # BuildingGraph class
│   │   ├── node.py           # BaseNode, LocationNode classes
│   │   ├── routing.py        # RouteCalculator
│   │   └── floorplan.py      # FloorplanParser
│   ├── devices/
│   │   ├── __init__.py
│   │   ├── base_device.py    # BaseDevice class
│   │   ├── exit_sign.py      # ExitSign
│   │   └── smoke_alarm.py    # SmokeAlarm
│   ├── messaging/
│   │   ├── __init__.py
│   │   └── pubsub.py         # MessageBus, Message classes
│   ├── simulation/
│   │   ├── __init__.py
│   │   └── engine.py         # SimulationEngine
│   └── web/
│       ├── __init__.py
│       ├── server.py         # Flask app
│       ├── static/
│       │   ├── style.css
│       │   └── dashboard.js
│       └── templates/
│           └── index.html
├── data/
│   └── floorplans/
│       ├── simple_corridor.json
│       ├── office_building.json
│       └── schema.json       # JSON schema definition
├── tests/
│   ├── test_routing.py
│   ├── test_devices.py
│   └── test_simulation.py
├── requirements.txt
├── README.md
├── SRS.MD                    # Full system SRS
└── PROTOTYPE_SRS.md          # This document
```

### 5.3 Floorplan JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["building", "nodes", "edges", "devices"],
  "properties": {
    "building": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"}
      }
    },
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "type", "x", "y"],
        "properties": {
          "id": {"type": "string"},
          "type": {"enum": ["room", "corridor", "exit"]},
          "x": {"type": "number"},
          "y": {"type": "number"},
          "name": {"type": "string"}
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "distance"],
        "properties": {
          "from": {"type": "string"},
          "to": {"type": "string"},
          "distance": {"type": "number"},
          "bidirectional": {"type": "boolean", "default": true}
        }
      }
    },
    "devices": {
      "type": "object",
      "properties": {
        "exit_signs": {"type": "array", "items": {"type": "string"}},
        "smoke_alarms": {"type": "array", "items": {"type": "string"}}
      }
    }
  }
}
```

### 5.4 API Endpoints

**GET `/`**
- Returns: HTML dashboard

**GET `/api/status`**
- Returns: JSON with current simulation state
```json
{
  "simulation_time": 45.2,
  "evacuation_active": true,
  "nodes": [
    {
      "id": "room_a",
      "type": "room",
      "x": 0,
      "y": 0,
      "devices": ["exit_sign_1", "smoke_alarm_1"]
    }
  ],
  "devices": [
    {
      "id": "exit_sign_1",
      "type": "exit_sign",
      "location": "room_a",
      "display_mode": "evacuation",
      "direction": "E",
      "distance_to_exit": 15,
      "confidence": 85
    },
    {
      "id": "smoke_alarm_1",
      "type": "smoke_alarm",
      "location": "room_a",
      "smoke_level": 25,
      "temperature": 35,
      "hazard_level": 1
    }
  ],
  "hazards": [
    {"node_id": "room_b", "level": 3, "type": "fire"}
  ],
  "routes": [
    {
      "from": "room_a",
      "to": "exit_main",
      "path": ["room_a", "corridor_1", "exit_main"],
      "confidence": 85
    }
  ]
}
```

**POST `/api/evacuation/start`**
- Triggers system-wide evacuation mode
- Returns: `{ "status": "ok" }`

**POST `/api/hazard/inject`**
- Body: `{ "node_id": "room_b", "type": "fire", "intensity": 80 }`
- Returns: `{ "status": "ok" }`

**POST `/api/node/fail`**
- Body: `{ "node_id": "exit_sign_3" }`
- Simulates device failure
- Returns: `{ "status": "ok" }`

**POST `/api/simulation/reset`**
- Resets simulation to initial state
- Returns: `{ "status": "ok" }`

### 5.5 Class Design

#### 5.5.1 Core Classes

**`BuildingGraph`** (from Full SRS FR-3.1.1)
```python
class BuildingGraph:
    def __init__(self):
        self.graph: nx.DiGraph
        self.exits: List[str]  # Node IDs of exits
        
    def add_node(self, node_id: str, node_type: str, x: float, y: float, **attrs)
    def add_edge(self, from_id: str, to_id: str, distance: float, **attrs)
    def get_neighbors(self, node_id: str) -> List[str]
    def update_edge_weight(self, from_id: str, to_id: str, hazard_level: int)
    def get_shortest_path(self, start: str, goal: str) -> Tuple[List[str], float]
```

**`RouteCalculator`** (from Full SRS FR-3.1.5)
```python
class RouteCalculator:
    def __init__(self, building_graph: BuildingGraph):
        self.graph = building_graph
        
    def calculate_route(self, start: str, mode: str = 'safety') -> Dict:
        """
        Returns: {
            'path': List[str],
            'distance': float,
            'confidence': float,
            'next_hop': str
        }
        """
        
    def calculate_confidence(self, path: List[str], hazards: Dict) -> float
    def distribute_routes(self, start: str, exits: List[str]) -> str
```

#### 5.5.2 Device Classes

**`BaseDevice`**
```python
class BaseDevice:
    def __init__(self, device_id: str, node_id: str, message_bus: MessageBus):
        self.device_id = device_id
        self.node_id = node_id
        self.bus = message_bus
        self.operational = True
        
    def receive_message(self, message: Message) -> None
    def send_message(self, topic: str, payload: Dict) -> None
    def update(self) -> None  # Called each simulation timestep
    def to_dict(self) -> Dict  # For API serialization
```

**`ExitSign(BaseDevice)`** (from Full SRS FR-3.3.1)
```python
class ExitSign(BaseDevice):
    def __init__(self, device_id: str, node_id: str, message_bus: MessageBus,
                 building_graph: BuildingGraph):
        super().__init__(device_id, node_id, message_bus)
        self.graph = building_graph
        self.display_mode: str = 'normal'
        self.direction: Optional[str] = None
        self.distance_to_exit: Optional[float] = None
        self.confidence: float = 100.0
        self.current_route: List[str] = []
        
    def recalculate_route(self) -> None
    def update_display(self) -> None
    def handle_hazard_alert(self, message: Message) -> None
```

**`SmokeAlarm(BaseDevice)`** (from Full SRS FR-3.2.1)
```python
class SmokeAlarm(BaseDevice):
    def __init__(self, device_id: str, node_id: str, message_bus: MessageBus):
        super().__init__(device_id, node_id, message_bus)
        self.smoke_level: float = 0.0
        self.temperature: float = 20.0
        self.hazard_level: int = 0
        
    def update_readings(self, smoke: float, temp: float) -> None
    def classify_hazard(self) -> int
    def publish_alert(self) -> None
```

#### 5.5.3 Messaging Classes

**`Message`**
```python
@dataclass
class Message:
    topic: str
    sender_id: str
    timestamp: float
    payload: Dict
```

**`MessageBus`** (from Full SRS FR-3.4.1)
```python
class MessageBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]]
        self.message_queue: Queue[Message]
        
    def subscribe(self, topic: str, callback: Callable[[Message], None])
    def publish(self, message: Message)
    def process_queue(self)  # Process all pending messages
```

#### 5.5.4 Simulation Classes

**`SimulationEngine`**
```python
class SimulationEngine:
    def __init__(self, floorplan_path: str):
        self.graph: BuildingGraph
        self.devices: Dict[str, BaseDevice]
        self.message_bus: MessageBus
        self.hazards: Dict[str, Dict]  # node_id -> hazard_info
        self.evacuation_active: bool = False
        self.simulation_time: float = 0.0
        
    def load_floorplan(self, path: str)
    def step(self)  # Advance one timestep
    def inject_hazard(self, node_id: str, hazard_type: str, intensity: float)
    def trigger_evacuation(self)
    def get_state(self) -> Dict  # For API endpoint
    def reset(self)
```

---

## 6. Implementation Priorities

### 6.1 Phase 1: Core Infrastructure (Week 1)
**Goal:** Build foundation - graph model, devices, basic messaging

**Tasks:**
- [x] Create project structure
- [ ] Implement `BuildingGraph` class
  - [ ] Node/edge management
  - [ ] NetworkX integration
- [ ] Implement `FloorplanParser`
  - [ ] JSON schema validation
  - [ ] Graph construction from JSON
- [ ] Implement `MessageBus`
  - [ ] Topic subscriptions
  - [ ] Message queue processing
- [ ] Create `BaseDevice` class
- [ ] Implement `ExitSign` (basic version)
  - [ ] Display states
  - [ ] Subscribe to hazard alerts
- [ ] Implement `SmokeAlarm` (basic version)
  - [ ] Hazard classification
  - [ ] Alert publishing

**Deliverable:** Can load a simple floorplan and instantiate devices

---

### 6.2 Phase 2: Routing & Algorithms (Week 2)
**Goal:** Implement core routing logic with hazard avoidance

**Tasks:**
- [ ] Implement `RouteCalculator`
  - [ ] Dijkstra's algorithm with custom weights
  - [ ] Hazard-based weight adjustments
  - [ ] Confidence calculation
- [ ] Integrate routing with `ExitSign`
  - [ ] Automatic recalculation on hazard alerts
  - [ ] Display state updates based on routes
- [ ] Implement hazard propagation
  - [ ] Graph edge weight updates
  - [ ] Message cascading to neighbors
- [ ] Add route distribution (multiple exits)
- [ ] Handle "no safe route" scenario

**Deliverable:** Signs recalculate routes when fires are injected

---

### 6.3 Phase 3: Simulation & Visualization (Week 3)
**Goal:** Create interactive demo with web dashboard

**Tasks:**
- [ ] Implement `SimulationEngine`
  - [ ] Timestep loop
  - [ ] Hazard injection interface
  - [ ] State serialization for API
- [ ] Create Flask web server
  - [ ] API endpoints (status, inject_hazard, etc.)
  - [ ] Static file serving
- [ ] Build HTML dashboard
  - [ ] 2D floorplan rendering (Canvas or SVG)
  - [ ] Device icon placement
  - [ ] Real-time updates (polling)
  - [ ] Control panel (inject hazard, start evacuation)
- [ ] Implement hazard visualization
  - [ ] Color-coded node overlays
  - [ ] Route arrows between nodes

**Deliverable:** Interactive web demo showing dynamic routing

---

### 6.4 Phase 4: Testing & Documentation (Week 4)
**Goal:** Create test scenarios, document system, prepare demo

**Tasks:**
- [ ] Create test floorplans
  - [ ] Simple corridor (3 rooms, 1 exit)
  - [ ] Office with multiple exits
  - [ ] Complex layout (test load balancing)
- [ ] Write unit tests
  - [ ] Route calculation correctness
  - [ ] Hazard classification
  - [ ] Message bus functionality
- [ ] Write integration tests
  - [ ] End-to-end evacuation scenarios
  - [ ] Node failure handling
- [ ] Create demo script
  - [ ] Scenario walkthroughs
  - [ ] Narration notes
- [ ] Document system
  - [ ] Code comments
  - [ ] README with setup instructions
  - [ ] SRS requirement traceability matrix

**Deliverable:** Polished demo ready for presentation

---

## 7. Test Scenarios

### 7.1 Scenario 1: Simple Corridor Evacuation

**Floorplan:** 
```
[Room A] ←→ [Corridor] ←→ [Room B] ←→ [Exit]
```

**Test Steps:**
1. Load floorplan
2. Verify all exit signs point toward exit
3. Inject fire in Corridor
4. Verify Room B sign changes to "DO NOT ENTER"
5. Verify Room A sign shows alternate route (if exists) or "NO SAFE ROUTE"

**Expected Results:**
- Exit signs recalculate within 1 simulation timestep
- Confidence scores drop appropriately
- Dashboard shows hazard overlay

---

### 7.2 Scenario 2: Multiple Exits

**Floorplan:**
```
        [Exit North]
              ↑
[Room 1] → [Hub] ← [Room 2]
              ↓
        [Exit South]
```

**Test Steps:**
1. Load floorplan
2. Verify signs in Room 1 and Room 2 point to different exits (load balancing)
3. Inject fire at Exit North
4. Verify all signs redirect to Exit South

**Expected Results:**
- Initial state: 50/50 distribution to exits
- After hazard: 100% route to safe exit
- Confidence remains high for unaffected routes

---

### 7.3 Scenario 3: Node Failure

**Floorplan:**
```
[Room] → [Corridor] → [Exit]
           ↑
      [Exit Sign]
```

**Test Steps:**
1. Load floorplan
2. Trigger evacuation
3. Simulate exit sign failure in Corridor
4. Verify Room's exit sign shows reduced confidence

**Expected Results:**
- Confidence drops below 100% (missing intermediate node)
- Route still provided (if direct path available)
- Dashboard shows failed node in different color

---

### 7.4 Scenario 4: No Safe Route

**Floorplan:**
```
[Room] → [Corridor 1] → [Exit 1]
   ↓
[Corridor 2] → [Exit 2]
```

**Test Steps:**
1. Load floorplan
2. Inject fire in Corridor 1
3. Inject fire in Corridor 2
4. Verify exit sign in Room shows "NO SAFE ROUTE"

**Expected Results:**
- Display mode changes to "blocked"
- Message logged to simulation console
- Dashboard shows critical alert

---

## 8. Success Criteria

The prototype will be considered successful if it demonstrates:

1. ✅ **Dynamic routing:** Routes change in response to hazards (Scenario 1)
2. ✅ **Decentralized communication:** Devices coordinate via messages without central controller
3. ✅ **Algorithm correctness:** Routes avoid high-hazard areas and prefer safe paths
4. ✅ **Visualization clarity:** Dashboard clearly shows building state, hazards, and routes
5. ✅ **Floorplan flexibility:** Can load and visualize different building layouts
6. ✅ **Interactive simulation:** Users can inject hazards and see real-time responses

---

## 9. Requirements Traceability

Mapping prototype requirements to full SRS sections:

| Prototype Req | Full SRS Ref | Description |
|---------------|--------------|-------------|
| PR-FR-4.1.1 | FR-3.1.1 | Building graph representation |
| PR-FR-4.2.1 | FR-3.3.1-3.3.3 | Exit sign specifications |
| PR-FR-4.2.4 | FR-3.2.1-3.2.2 | Smoke alarm sensors |
| PR-FR-4.2.5 | FR-3.2.8 | Hazard level classification |
| PR-FR-4.3.1 | FR-3.1.5 | Dijkstra/A* routing |
| PR-FR-4.3.2 | FR-3.1.2 | Edge weight calculation |
| PR-FR-4.3.3 | FR-3.1.3 | Route prioritization |
| PR-FR-4.3.4 | FR-3.1.7 | Confidence scoring |
| PR-FR-4.3.5 | FR-3.1.11 | No safe route handling |
| PR-FR-4.4.1 | FR-3.4.1 | Decentralized messaging |
| PR-FR-4.4.4 | FR-3.3.10 | Response to hazard alerts |

---

## 10. Future Extensions (Post-Prototype)

After completing the prototype, possible enhancements:

- **Multi-floor buildings:** 3D visualization, stairwell modeling
- **Real hardware integration:** Raspberry Pi nodes, LED matrices
- **Advanced algorithms:** A* with better heuristics, machine learning for hazard prediction
- **Persistent logging:** SQLite database for event history
- **Authentication:** User roles (facility manager, first responder)
- **Mobile interface:** Responsive design for tablets
- **WebSocket updates:** Replace polling with real-time push
- **Hazard spread simulation:** Fire growth models, smoke propagation
- **Occupancy tracking:** Simulate evacuee movement through building

---

## Document End

**Next Action:** Begin Phase 1 implementation with `BuildingGraph` class and floorplan parser.
