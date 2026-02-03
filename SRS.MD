# Software Requirements Specification (SRS)

## Fire Evacuation System & Algorithm
**Advanced Programming MK6004-25-A25**

---

## Document Information

**Project Name:** SmartExit™ Fire Evacuation System  
**Document Version:** 1.0  
**Date:** 2026-02-03  
**Author:** MKJM563  
**Status:** Draft

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Overall Description](#2-overall-description)
3. [System Features and Requirements](#3-system-features-and-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [External Interface Requirements](#5-external-interface-requirements)
6. [System Constraints](#6-system-constraints)
7. [Appendices](#7-appendices)

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional and non-functional requirements for the SmartExit™ Fire Evacuation System powered by SmartRoute™ software. The system aims to modernize emergency exit infrastructure through intelligent, dynamic signage that adapts in real-time to building conditions, fire spread, congestion, and physical obstructions.

### 1.2 Scope

The SmartExit™ system comprises:
- **Hardware Components:** Distributed intelligent exit sign nodes (SmartExit™ units) with integrated LED panels, sensors, and networking capabilities
- **Software Components:** SmartRoute™ software for centralized monitoring, route calculation, data aggregation, and visualization
- **Network Infrastructure:** Communication protocols enabling coordination between nodes

The system is designed for deployment in non-residential buildings including hospitals, hotels, educational facilities, offices, retail premises, and other complex commercial and public infrastructure.

### 1.3 Problem Statement & Justification

**Current State:**  
Fire exit signage in the UK operates under BS 5499 Pt 4:2000 compliance standards, requiring static signage on all emergency exit routes [[1]](https://www.lhcfp.co.uk/safetysignsguidance.pdf)[[2]](https://www.fireprotectiononline.co.uk/info/the-uk-fire-exit-signs-regulations/). However, the Grenfell Tower incident exposed systemic weaknesses in fire safety standards, including inadequate signage [[3]](https://www.ibtimes.co.uk/fire-safety-after-grenfell-why-emergency-signage-still-falls-short-1733205).

**Key Problems:**
- Static signage cannot adapt to dynamic emergencies (fire spread, blocked routes, congestion)
- Common degradation issues: blocked signs, faded text, poor lighting, missing directional arrows
- Periodic audits fail to capture real-time sign degradation or layout changes
- Decision-making burden falls on evacuees during high-stress emergencies
- "Compliance" often represents minimum legal requirements rather than optimal safety

**Impact:**  
In the year ending June 2025, UK fire services attended 13,983 fires in non-dwelling buildings [[4]](https://www.gov.uk/government/statistical-data-sets/fire0102-previous-data-tables). Complex buildings (hospitals, hotels, large offices) amplify the limitations of static signage.

**Organizational Context:**  
Under the Building Safety Act 2022 (Section 156), businesses must conduct fire risk assessments. Poor evacuation systems pose:
- **Ethical risks:** Employee and visitor safety
- **Legal risks:** Non-compliance and liability
- **Reputational risks:** Public perception following evacuation failures

### 1.4 Document Conventions

- **SHALL/MUST:** Mandatory requirement
- **SHOULD:** Recommended requirement
- **MAY:** Optional requirement
- **Functional Requirement (FR-XXX):** Specific system capability
- **Non-Functional Requirement (NFR-XXX):** Quality attribute or constraint

### 1.5 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| SmartExit™ | Intelligent fire exit sign node hardware unit |
| SmartRoute™ | Proprietary software system for route calculation and monitoring |
| Node | Individual SmartExit™ unit within the network |
| Assembly Point | Designated safe gathering location outside building |
| Edge | Connection between two nodes representing a navigable path |
| Vertex/Node | Graph representation of physical location or decision point |
| Mesh Network | Decentralized network topology where nodes communicate peer-to-peer |
| Degradation | Gradual decline in sign functionality (LED dimming, sensor drift) |

---

## 2. Overall Description

### 2.1 Product Perspective

The SmartExit™ system represents a paradigm shift from static, compliance-focused signage to dynamic, safety-optimized evacuation guidance. It operates as:

1. **Distributed Intelligent Network:** Self-contained nodes coordinate autonomously
2. **Real-Time Monitoring System:** Continuous environmental sensing and status tracking
3. **Adaptive Routing Engine:** Dynamic path calculation based on multiple safety factors
4. **Compliance & Audit Platform:** Automated logging and evidence generation

**Related Question:** [What extensible benefits are there for the data? Not only for in house teams but first responders etc.](#extensibility-requirements)

### 2.2 Product Functions

**Core Capabilities:**
- Real-time fire detection and spread tracking
- Dynamic route calculation avoiding hazards, obstructions, and congestion
- Visual guidance via integrated LED display panels
- Continuous system health monitoring and self-diagnostics
- Comprehensive event logging and audit trail generation
- Building layout modeling and automatic change detection
- Multi-floor and interconnected building support

**Related Questions:** 
- [What elements of the system introduce the versatility to being deployable across differing categories of businesses?](#deployment-versatility)
- [What behaviours are different for buildings with multiple floors, multiple tenants, or interconnected with others outside of the systems jurisdiction?](#multi-building-coordination)

### 2.3 User Classes and Characteristics

| User Class | Characteristics | Technical Expertise | Primary Needs |
|------------|----------------|---------------------|---------------|
| **Evacuees** | Building occupants during emergency | None required | Clear, unambiguous guidance; minimal cognitive load |
| **Facility Managers** | Responsible for building safety systems | Low to moderate | Easy monitoring; compliance reporting; maintenance alerts |
| **Safety Officers** | Conduct fire drills and risk assessments | Moderate | System testing; drill simulation; audit evidence |
| **First Responders** | Firefighters and emergency personnel | Moderate | Real-time building status; hazard locations; occupant tracking |
| **System Administrators** | IT/technical staff managing deployment | High | Configuration; firmware updates; network management |
| **Regulators/Auditors** | Verify compliance with safety standards | Moderate | Historical data; compliance reports; incident reconstruction |

**Related Question:** [How much technical expertise can we reasonably require those in charge of the current systems to possess upon migration?](#usability-requirements)

### 2.4 Operating Environment

**Physical Environment:**
- Non-residential buildings (hospitals, hotels, offices, retail, educational facilities)
- Ambient temperatures: -10°C to +50°C (operational); -20°C to +60°C (survival)
- Humidity: 10% to 90% non-condensing
- Exposure to smoke, heat, and potential physical impact during emergencies

**Technical Environment:**
- Node-to-node mesh networking (primary)
- Optional centralized server infrastructure
- Integration with existing building management systems (BMS)
- Compatibility with fire alarm panels and sensor networks
- Cloud connectivity for remote monitoring (optional)

**Related Question:** [How do the smoke, heat and power failure affect the operation and what failsafe's might be built in?](#environmental-resilience)

### 2.5 Design and Implementation Constraints

**Regulatory Constraints:**
- BS 5499 Pt 4:2000 (fire safety signage standards)
- Building Safety Act 2022 (Section 156)
- UK GDPR (data protection for occupant tracking)
- Equality Act 2010 (accessibility requirements)

**Technical Constraints:**
- Real-time computation requirements (<2 second route recalculation)
- Battery backup duration (minimum 3 hours)
- Network latency tolerance (<500ms for critical updates)
- Limited display surface area on exit signs

**Business Constraints:**
- Retrofit compatibility with existing building infrastructure
- Minimal installation disruption to operational buildings
- Cost-effectiveness compared to static signage lifecycle

**Related Questions:**
- [How will the system support its legislative obligations, and in fact supersede them?](#compliance-requirements)
- [What is the recalculation rate, what layer of obfuscation is required to do so in a valid time complexity?](#algorithmic-complexity)

### 2.6 Assumptions and Dependencies

**Assumptions:**
1. Buildings have basic digital building plans available for initial configuration
2. Power infrastructure supports network-connected devices
3. Organizations commit to periodic system maintenance
4. Evacuees will follow displayed guidance during emergencies

**Dependencies:**
1. Availability of compatible sensor hardware (smoke, heat, motion)
2. Network infrastructure (wired or wireless mesh)
3. Initial building survey and mapping process
4. Integration APIs for third-party fire alarm systems

---

## 3. System Features and Requirements

### 3.1 Dynamic Route Calculation

**Priority:** Critical  
**Risk:** High

#### 3.1.1 Description

The system SHALL calculate optimal evacuation routes in real-time based on multiple dynamic factors including fire location, smoke spread, physical obstructions, route congestion, and evacuee-specific needs.

**Related Questions:**
- [Will the system optimise for the shortest route? The safest? The least congested?](#route-optimization)
- [Is this a shortest-path problem, a multi-objective optimisation problem or some sort of real-time control system?](#problem-classification)

#### 3.1.2 Functional Requirements

**FR-3.1.1** The system SHALL represent building topology as a weighted directed graph where:
- Vertices represent physical locations (rooms, corridor intersections, exits)
- Edges represent navigable paths with multiple weight attributes

**Related Question:** [What graphing models best represent a building, with what degree of granularity?](#graph-modeling)

**FR-3.1.2** Edge weights SHALL incorporate:
- Physical distance (meters)
- Safety score (0-100, based on fire/smoke proximity)
- Congestion factor (estimated evacuee density)
- Accessibility rating (wheelchair, stretcher compatibility)
- Historical evacuation speed

**Related Question:** [Are edges weighted by distance, safety, congestion, visibility etc](#edge-weighting)

**FR-3.1.3** The system SHALL support multi-objective route optimization with configurable priority:
- **Safety-first mode** (default): Prioritize routes furthest from hazards
- **Speed mode:** Balance safety with shortest evacuation time
- **Accessibility mode:** Prioritize wheelchair/stretcher-accessible routes

**Related Question:** [What sort of considerations were currently made to ensure that the evacuation routes were optimum for different user groups? Children, the physically disabled, patients strapped to beds etc.](#user-group-optimization)

**FR-3.1.4** Route recalculation SHALL occur within 2 seconds of:
- New fire/smoke detection
- Obstruction identified on current evacuation route
- Significant congestion detected (>threshold evacuees in corridor)
- Node failure blocking a primary route

**Related Question:** [What is the recalculation rate, what layer of obfuscation is required to do so in a valid time complexity and not stumble to a pitfall of super polynomial or intractable complexities?](#computational-performance)

**FR-3.1.5** The system SHALL implement a modified Dijkstra's or A* algorithm with:
- Heuristic functions incorporating safety and congestion
- Pre-computed route caching for common scenarios
- Incremental recalculation (not full graph recomputation)

**FR-3.1.6** When multiple safe routes exist, the system SHALL distribute evacuees to prevent congestion bottlenecks

**FR-3.1.7** The system SHALL maintain a "route confidence score" (0-100%) based on:
- Data freshness from relevant sensors
- Number of operational nodes along route
- Time since last verification

**Related Question:** [What confidence level is required before a route is deemed unsafe?](#confidence-thresholds)

**FR-3.1.8** Routes with confidence <60% SHALL be marked as "use with caution" and displayed differently

**FR-3.1.9** Routes with confidence <30% SHALL only be suggested if no better alternatives exist

**FR-3.1.10** The system SHALL NOT suggest routes through areas with confirmed fire presence (sensor data + visual confirmation)

**FR-3.1.11** If ALL routes to external assembly points are blocked, the system SHALL:
- Direct evacuees to designated refuge areas (if available)
- Display "SEEK REFUGE" messaging
- Alert emergency services of trapped occupants

**Related Question:** [What behaviours will the system exhibit if evacuees move against the suggested routes? A demonstrable viable exit is better than none](#contradictory-movement)

### 3.2 Real-Time Hazard Detection & Tracking

**Priority:** Critical  
**Risk:** High

#### 3.2.1 Description

The system SHALL continuously monitor environmental conditions through integrated and external sensors to detect fires, smoke spread, and other hazards.

**Related Questions:**
- [How are obstructions detected and factored in?](#obstruction-detection)
- [What sensors are integral vs "optional"? Which of their data is of most importance?](#sensor-hierarchy)

#### 3.2.2 Functional Requirements

**FR-3.2.1** Each SmartExit™ node SHALL include integrated sensors:
- Smoke detector (photoelectric and ionization)
- Temperature sensor (±1°C accuracy)
- Ambient light sensor
- Motion detector (PIR)

**FR-3.2.2** The system SHALL integrate with external building sensors via standard protocols:
- BACnet (Building Automation and Control Networks)
- Modbus
- MQTT
- Fire alarm panel integration (proprietary protocols)

**Related Question:** [What external systems should be permissible to integrate? Does more input data necessarily equate to better decision making?](#external-integration)

**FR-3.2.3** Sensor data prioritization SHALL follow this hierarchy:
1. **Critical (immediate route impact):** Smoke detection, high temperature (>60°C), fire alarm activation
2. **High (route adjustment):** Moderate temperature increase, door closure detection, obstruction sensors
3. **Medium (congestion management):** Motion/occupancy data, evacuee flow rates
4. **Low (optimization):** Ambient conditions, historical patterns

**FR-3.2.4** The system SHALL implement sensor fusion algorithms combining multiple data sources to:
- Reduce false positives (e.g., steam vs. smoke)
- Triangulate fire location from multiple temperature readings
- Predict fire spread direction and speed

**FR-3.2.5** Fire spread prediction SHALL use:
- Temperature gradient analysis
- Smoke density progression
- Building material properties (if configured)
- HVAC airflow patterns (if available)

**FR-3.2.6** Obstruction detection SHALL incorporate:
- Manual input (facility staff can mark routes blocked)
- Automatic detection via motion sensor patterns (expected vs. actual evacuee flow)
- Integration with access control systems (door status)
- Camera-based AI detection (optional module)

**FR-3.2.7** The system SHALL classify obstructions as:
- **Permanent:** Detected for >5 minutes OR manually confirmed → triggers layout update review
- **Temporary:** Cleared within 5 minutes → route adjustment only
- **Unknown:** Insufficient data → increased caution on route confidence

**FR-3.2.8** Environmental hazard levels SHALL be categorized:
- **Level 0 (Normal):** No detected hazards
- **Level 1 (Monitoring):** Elevated temperature or minor smoke (localized)
- **Level 2 (Caution):** Moderate smoke or temperature >45°C
- **Level 3 (Danger):** Heavy smoke or temperature >60°C
- **Level 4 (Impassable):** Confirmed fire or extreme conditions

**FR-3.2.9** Routes SHALL NOT pass through Level 3+ hazard zones

**FR-3.2.10** Routes through Level 2 zones SHALL only be suggested if:
- No Level 0-1 alternatives exist, AND
- Route confidence remains >50%, AND
- Evacuees receive explicit warning on display

### 3.3 Intelligent Display & Guidance

**Priority:** Critical  
**Risk:** Medium

#### 3.3.1 Description

Each SmartExit™ node SHALL provide clear, adaptive visual guidance via integrated LED display panels designed for high-stress emergency conditions.

**Related Questions:**
- [Do current methods of signage and routing account for human error in their interpretation under duress (smoke, noise, panic etc)?](#human-factors)
- [How much information is too much during an emergency?](#information-overload)
- [Should signage use symbols, arrows, colours, animations, or text?](#display-language)

#### 3.3.2 Functional Requirements

**FR-3.3.1** Display specifications:
- Minimum luminance: 200 cd/m² (normal), 400 cd/m² (emergency mode)
- Viewing angle: ±70° horizontal, ±60° vertical
- Contrast ratio: minimum 10:1 in smoke conditions
- LED lifetime: minimum 50,000 hours

**FR-3.3.2** Display SHALL use internationally recognized symbols and colors:
- ISO 7010 emergency exit symbols (running person)
- Green for safe directions/routes
- Red for danger/do not enter
- Amber for caution/alternative route

**FR-3.3.3** Information hierarchy (displayed in order of priority):
1. **Primary directive:** Directional arrow + distance to nearest exit
2. **Hazard warning:** Symbol + location (if relevant)
3. **Secondary information:** Alternative route (if applicable)

**FR-3.3.4** Display content SHALL adapt to emergency phase:
- **Normal operation:** Static "EXIT" with green running person symbol
- **Alarm activated:** Animated arrow indicating direction + flashing border
- **Hazard detected:** Warning symbol + alternative route indication
- **Route blocked:** "DO NOT USE" + alternative direction

**FR-3.3.5** Text SHALL be limited to:
- Maximum 3 words per instruction
- Minimum 50mm character height for critical information
- High-contrast font (sans-serif, bold)

**Related Question:** [What is considered a reasonable universal design language for rich information conveyed over a rather minimal surface area?](#minimal-ui-design)

**FR-3.3.6** Animation SHALL be used sparingly:
- Directional arrows: smooth sliding motion (1 second cycle)
- Warning indicators: pulsing (2Hz frequency)
- No distracting or complex animations that impede comprehension

**FR-3.3.7** The system SHALL support accessibility features:
- Audio cues via integrated speaker (optional)
- Tactile indicator on unit housing (raised arrow)
- Enhanced contrast mode for visually impaired

**FR-3.3.8** Display SHALL automatically increase brightness when:
- Ambient light decreases (smoke conditions)
- Emergency mode activated
- Route confidence drops below 70%

**FR-3.3.9** In case of contradictory guidance potential, the system SHALL:
- Ensure adjacent nodes display consistent directions
- Implement a "consensus protocol" where conflicting routes trigger recalculation
- Display "WAIT FOR INSTRUCTION" if system cannot resolve conflict within 5 seconds

**Related Question:** [How do we prevent oscillation or contradictory guidance across signs?](#guidance-consistency)

**FR-3.3.10** If an evacuee appears to ignore guidance (detected via motion sensors), the display SHALL:
- Continue showing optimal route (not change to match wrong direction)
- Increase urgency visual indicators (faster flashing)
- Log deviation event for post-incident analysis

**Related Question:** [What happens if a dynamic sign is ignored or misinterpreted?](#guidance-non-compliance)

### 3.4 Network Architecture & Node Coordination

**Priority:** Critical  
**Risk:** High

#### 3.4.1 Description

SmartExit™ nodes SHALL form a resilient distributed network capable of coordinated decision-making with or without centralized control.

**Related Questions:**
- [Is there a central coordinator or a fully decentralised mesh?](#network-topology)
- [How do nodes discover each other?](#node-discovery)
- [What happens if network partitions occur mid-evacuation?](#partition-tolerance)

#### 3.4.2 Functional Requirements

**FR-3.4.1** The system SHALL support hybrid network architecture:
- **Primary mode:** Mesh network with peer-to-peer node communication
- **Enhanced mode:** Centralized coordinator (SmartRoute™ server) for optimization
- **Degraded mode:** Autonomous operation with local decision-making

**FR-3.4.2** Each node SHALL implement:
- **Wired connection:** Ethernet (PoE preferred) as primary
- **Wireless connection:** 802.11ac/ax WiFi as backup
- **Emergency wireless mesh:** Proprietary low-latency protocol for node-to-node communication

**FR-3.4.3** Node discovery SHALL occur via:
- Automatic broadcast discovery on initial deployment
- Configuration file pre-loading topology
- Manual assignment via management interface
- Runtime neighbor detection via signal strength

**FR-3.4.4** Each node SHALL maintain:
- **Neighbor table:** Directly connected nodes (1-hop)
- **Topology map:** Full building graph (if available from coordinator)
- **Local state:** Own sensor data, display status, battery level

**FR-3.4.5** Consensus protocol for route decisions SHALL use:
- Quorum-based voting when coordinator unavailable
- Priority weighting (nodes closer to hazards have higher vote weight)
- Timeout mechanism (5 seconds max) before defaulting to safest known route

**Related Question:** [How is consensus reached on route safety?](#consensus-mechanism)

**FR-3.4.6** Network partition handling:
- Nodes SHALL continue operating with last known topology
- Partitioned segments SHALL calculate routes independently to nearest known exits
- Upon reconnection, systems SHALL synchronize state and recalculate if needed

**FR-3.4.7** The system SHALL detect network partitions via:
- Heartbeat messages (1 second intervals)
- Missing coordinator responses (>3 seconds)
- Unexpected neighbor loss (>2 adjacent nodes)

**FR-3.4.8** Cascading failure prevention:
- Nodes SHALL NOT propagate unverified hazard data (requires sensor confirmation)
- Maximum propagation rate limits (prevent false alarm storms)
- Exponential backoff for repeated conflicting updates

**Related Question:** [How do you prevent cascading failures or misinformation?](#failure-propagation)

**FR-3.4.9** Network bandwidth allocation:
- Critical messages (hazard detection): <100ms latency, highest priority
- Route updates: <500ms latency, high priority
- Status updates: <2s latency, medium priority
- Log synchronization: best effort, low priority

**FR-3.4.10** Security protocols:
- Encrypted communication (TLS 1.3 or equivalent)
- Node authentication via certificates
- Message signing to prevent tampering
- Isolated network segment (no direct internet access from nodes)

**Related Question:** [How do you prevent malicious interference or false signals?](#security-threats)

### 3.5 System Health Monitoring & Self-Diagnostics

**Priority:** High  
**Risk:** Medium

#### 3.5.1 Description

The system SHALL continuously monitor its own operational health and proactively alert facility managers to degradation, failures, or maintenance needs.

**Related Questions:**
- [How does the system detect gradual degradation (LED dimming, sensor drift)?](#degradation-detection)
- [Can the system flag layout changes automatically?](#layout-change-detection)
- [How often should self-tests be run?](#testing-frequency)

#### 3.5.2 Functional Requirements

**FR-3.5.1** Each node SHALL perform continuous self-monitoring:
- LED panel functionality (pixel test)
- Sensor calibration status
- Battery charge level
- Network connectivity
- Internal temperature
- Memory/CPU utilization

**FR-3.5.2** Automated testing schedule:
- **Continuous:** Sensor readings, network heartbeat
- **Every 60 seconds:** Display pixel test (brief flash pattern)
- **Every 10 minutes:** Battery health check, neighbor connectivity
- **Daily (03:00):** Full diagnostic cycle including LED color calibration
- **Weekly:** Sensor calibration verification
- **Monthly:** Simulated emergency mode activation

**FR-3.5.3** LED degradation detection:
- Baseline luminance measured at installation
- Continuous monitoring of light output
- Alert triggered when luminance drops below 80% of baseline
- Warning issued when below 70% (imminent replacement needed)

**FR-3.5.4** Sensor drift detection:
- Regular comparison with neighboring nodes (temperature correlation)
- Statistical outlier detection (values outside expected range)
- Calibration reminders based on manufacturer specifications

**FR-3.5.5** Layout change detection SHALL use:
- Unexpected motion patterns (people consistently accessing "non-existent" routes)
- New RF signal sources (indicating new equipment/walls)
- Manual reporting interface for facility staff
- Integration with BIM (Building Information Modeling) systems for planned changes

**FR-3.5.6** Obstruction detection (non-emergency):
- Persistent motion sensor blockage (>1 hour)
- Ambient light sensor showing unexpected darkness
- Manual flag from facility staff

**Related Question:** [What are the current systems for discovering signage degradation or significant enough changes in layout to warrant issuing new signage and routeing?](#current-degradation-systems)

**FR-3.5.7** Physical damage detection:
- Accelerometer detecting impact
- Sudden sensor failures
- Power supply irregularities
- Manual damage reporting

**FR-3.5.8** Node health status SHALL be classified:
- **Operational (Green):** All systems functioning within normal parameters
- **Degraded (Amber):** Minor issues detected, functionality maintained, maintenance recommended
- **Warning (Orange):** Significant issues, reduced functionality, maintenance required soon
- **Failed (Red):** Critical failure, node non-operational or dangerous

**FR-3.5.9** The system SHALL generate maintenance alerts via:
- Dashboard notifications (facility manager interface)
- Email alerts (configurable)
- Integration with computerized maintenance management systems (CMMS)
- Mobile app push notifications (optional)

**FR-3.5.10** Alert escalation SHALL occur:
- **Degraded status:** Alert within 24 hours
- **Warning status:** Alert within 1 hour
- **Failed status:** Immediate alert + redundancy activation

### 3.6 Building Model & Configuration Management

**Priority:** High  
**Risk:** Medium

#### 3.6.1 Description

The system SHALL maintain an accurate digital representation of building topology, updating as physical environments change.

**Related Questions:**
- [To what degree of accuracy is the building modelled within the system?](#model-accuracy)
- [How is said model kept up to date?](#model-maintenance)

#### 3.6.2 Functional Requirements

**FR-3.6.1** Initial building model SHALL be created from:
- Uploaded architectural floor plans (PDF, DWG, IFC formats)
- Assisted manual mapping tool (drag-and-drop interface)
- Site survey data (node placement coordinates)
- Integration with existing BIM systems

**FR-3.6.2** Building model SHALL include:
- **Spatial data:** Rooms, corridors, staircases, exits, assembly points
- **Connectivity data:** Doors, openings, navigable paths
- **Semantic data:** Room types, occupancy limits, fire ratings
- **Accessibility data:** Wheelchair routes, refuge areas, lift locations

**FR-3.6.3** Model accuracy requirements:
- Spatial accuracy: ±0.5 meters for critical paths
- Topology accuracy: 100% (all actual routes must be represented)
- Update latency: <24 hours for non-emergency changes

**FR-3.6.4** Model updates SHALL be triggered by:
- Manual edits via management interface
- Automated layout change detection (see FR-3.5.5)
- Integration with building permit systems (planned renovations)
- Post-incident reviews identifying model inaccuracies

**FR-3.6.5** The system SHALL support versioning:
- All model changes logged with timestamp and author
- Ability to rollback to previous versions
- Comparison view showing differences between versions

**FR-3.6.6** Multi-floor building support:
- Vertical connections (stairs, lifts, ramps) explicitly modeled
- Per-floor graph representation with inter-floor edges
- Lift exclusion from evacuation routes (configurable for accessibility exceptions)

**Related Question:** [What behaviours are different for buildings with multiple floors, multiple tenants, or interconnected with others outside of the systems jurisdiction?](#multi-floor-handling)

**FR-3.6.7** Multi-tenant building support:
- Logical separation of tenant zones (access control integration)
- Shared evacuation routes marked explicitly
- Per-tenant evacuation coordination (optional)

**FR-3.6.8** Interconnected building support:
- External exits to adjacent buildings marked as "transitional"
- Coordination protocol for evacuation across building boundaries
- Ability to hand off evacuees to adjacent system (if available)
- Fallback to treating adjacent building as external assembly point

**FR-3.6.9** Configuration SHALL include:
- Assembly point locations (GPS coordinates + descriptive names)
- Refuge area definitions (location, capacity, communication equipment)
- Hazardous material storage locations (avoid in routing)
- Critical infrastructure (server rooms, medical equipment) requiring special evacuation protocols

### 3.7 Event Logging & Audit Trail

**Priority:** High  
**Risk:** Medium

#### 3.7.1 Description

The system SHALL maintain comprehensive logs of all operations, decisions, and events for compliance, post-incident analysis, and continuous improvement.

**Related Questions:**
- [What evidence is required currently to demonstrate baseline 'due diligence' of compliance?](#compliance-evidence)
- [Upon failure to evacuate, what should the system look like to remain robust under investigative scrutiny?](#investigative-robustness)
- [Does logging the systems decisions invite a higher likelihood of being picked apart and liable in court?](#liability-concerns)
- [What are the retention policies regarding this data? Who is the owner?](#data-governance)

#### 3.7.2 Functional Requirements

**FR-3.7.1** The system SHALL log the following event categories:
- **System events:** Node startup/shutdown, configuration changes, firmware updates
- **Environmental events:** Sensor readings (aggregated), hazard detections, threshold crossings
- **Routing events:** Route calculations, route changes, guidance provided
- **User interaction events:** Manual overrides, staff inputs, reported issues
- **Network events:** Connection status changes, partitions, consensus failures
- **Maintenance events:** Self-test results, alerts generated, maintenance performed

**FR-3.7.2** Each log entry SHALL include:
- Timestamp (UTC, microsecond precision)
- Event type and severity
- Source (node ID, user ID, or system component)
- Detailed event data (structured JSON format)
- Contextual information (building state snapshot)

**FR-3.7.3** Emergency event logging SHALL capture:
- Complete evacuation timeline (alarm → all-clear)
- All route calculations and changes with reasoning
- Sensor data at 1-second intervals during active emergency
- Estimated evacuee positions (anonymized, based on motion sensors)
- Manual interventions by staff or emergency services
- Node failures or degradations during event

**FR-3.7.4** Log storage SHALL implement:
- **Local buffering:** Minimum 7 days on each node (resilient to network loss)
- **Centralized storage:** Minimum 7 years (as per UK fire safety guidance)
- **Encrypted storage:** AES-256 encryption at rest
- **Tamper-evident:** Cryptographic log signing to detect modifications

**FR-3.7.5** Data retention policy:
- **System/maintenance logs:** 2 years
- **Routine sensor data:** 90 days (aggregated), 7 days (raw)
- **Emergency event logs:** 7 years minimum (legal requirement)
- **Configuration changes:** Indefinite (version control)

**Related Question:** [What are the retention policies regarding this data? Who is the owner?](#data-ownership)

**FR-3.7.6** Data ownership and access:
- Building owner is primary data controller (GDPR)
- Facility managers have operational access
- Emergency services have read-only access during incidents (time-limited)
- Regulators/auditors have read-only access upon legitimate request
- System vendor has no access without explicit authorization

**FR-3.7.7** Privacy protection:
- No personal identification of evacuees
- Anonymized occupancy data (counts, not individuals)
- Camera data (if used) processed locally, not stored
- Staff actions logged by role, not individual (unless override)

**FR-3.7.8** Audit report generation:
- Compliance reports (BS 5499, Building Safety Act adherence)
- System uptime and health reports
- Evacuation drill analysis (time, issues, recommendations)
- Maintenance history reports
- Incident reconstruction reports (detailed timeline)

**FR-3.7.9** Post-incident analysis tools:
- Timeline visualization
- 3D playback of evacuee flow and route changes
- "What-if" scenario replay (e.g., what if exit X was blocked?)
- Automated recommendations for system improvement

**FR-3.7.10** Legal protection considerations:
- Logs SHALL document the reasoning for routing decisions (not just outcomes)
- Clear indication when system operates in degraded mode or with incomplete data
- Transparent confidence scores prevent appearance of false certainty
- Manual override logging shows human decision-making when system overridden

**Related Question:** [Does logging the systems decisions invite a higher likelihood of being picked apart and liable in court?](#legal-vulnerability)

### 3.8 Firmware & Software Update Management

**Priority:** Medium  
**Risk:** High

#### 3.8.1 Description

The system SHALL support safe, reliable updates to firmware and software without compromising operational integrity.

**Related Question:** [How are firmware and software updates safely deployed? If automatic, should there be overrides and fallbacks were they to occur at inopportune times?](#update-safety)

#### 3.8.2 Functional Requirements

**FR-3.8.1** Update deployment modes:
- **Manual:** Administrator initiates update at chosen time
- **Scheduled:** Automatic deployment during maintenance windows (configurable, default 02:00-05:00)
- **Emergency patch:** Critical security/safety updates deployed immediately with notification

**FR-3.8.2** Pre-update validation:
- Cryptographic signature verification (prevent malicious updates)
- Version compatibility check
- Available storage verification
- Battery level check (>50% required for wireless nodes)
- No active emergency in building

**FR-3.8.3** Staged rollout:
- **Phase 1:** 5% of nodes (test group)
- **Phase 2:** 25% of nodes (if Phase 1 successful after 24 hours)
- **Phase 3:** Remaining nodes (if Phase 2 successful after 24 hours)
- Automatic rollback if >10% of phase nodes report issues

**FR-3.8.4** Update process SHALL:
- Download update to temporary storage
- Verify integrity (checksum)
- Create backup of current firmware
- Apply update during low-activity period
- Reboot and self-test
- Confirm successful operation or auto-rollback

**FR-3.8.5** Emergency override:
- Updates SHALL be suspended immediately if fire alarm activates
- Updates SHALL NOT commence if building in emergency mode
- In-progress updates SHALL be paused and rolled back if emergency declared
- Resume capability after emergency resolved

**FR-3.8.6** Fallback mechanisms:
- Dual firmware partitions (current + backup)
- Automatic rollback if self-test fails after update
- Manual rollback capability via management interface
- Recovery mode accessible via physical button on node

**FR-3.8.7** Update notifications:
- Pre-notification to facility managers (72 hours advance for scheduled)
- Progress monitoring via dashboard
- Success/failure reporting
- Detailed logs of update process

### 3.9 Integration & Interoperability

**Priority:** Medium  
**Risk:** Medium

#### 3.9.1 Description

The system SHALL integrate with existing building systems and provide extensibility for future enhancements.

**Related Questions:**
- [What external systems should be permissible to integrate?](#integration-targets)
- [What extensible benefits are there for the data? Not only for in house teams but first responders etc.](#data-extensibility)
- [Should external influences (firefighters) have sway over routing?](#external-control)

#### 3.9.2 Functional Requirements

**FR-3.9.1** The system SHALL integrate with:
- **Fire alarm panels:** Receive alarm signals, zone activation data
- **Building Management Systems (BMS):** HVAC status, door positions, access control
- **Security systems:** Camera feeds (optional), access logs, intrusion detection
- **Public Address (PA) systems:** Audio announcements coordinated with visual guidance
- **Emergency lighting systems:** Synchronize activation
- **Lift control systems:** Disable during evacuation (with accessibility exceptions)

**FR-3.9.2** First responder integration:
- **Real-time dashboard:** Web-based interface showing current building status
- **Mobile application:** iOS/Android app for incident commanders
- **Standard protocols:** CAP (Common Alerting Protocol) for emergency services integration
- **Optional override:** Allow fire service to manually control routing (with authentication)

**Related Question:** [Should external influences (firefighters) have sway over routing?](#firefighter-override)

**FR-3.9.3** Override authority hierarchy:
1. **Emergency services (fire/rescue):** Full control during active incident (requires authentication)
2. **Building safety officer:** Manual route blocking, assembly point changes
3. **Facility manager:** Configuration changes, maintenance mode
4. **System administrator:** Technical configuration, but cannot override emergency decisions

**FR-3.9.4** API availability:
- RESTful API for external system integration
- WebSocket API for real-time event streaming
- MQTT broker for IoT device integration
- GraphQL API for flexible data queries

**FR-3.9.5** Data export formats:
- JSON (real-time API)
- CSV (historical data)
- IFC (building model)
- PDF (reports)

**FR-3.9.6** Third-party extensibility:
- Plugin architecture for custom sensors
- Webhook support for external notifications
- Custom dashboard widgets (iFrame embedding)
- Integration with CMMS systems (ServiceNow, Maximo, etc.)

**FR-3.9.7** Standards compliance:
- BACnet (building automation)
- Modbus (industrial sensors)
- ONVIF (camera integration)
- MQTT (IoT messaging)
- ISO 16484 (building automation protocols)

### 3.10 Evacuation Simulation & Drill Management

**Priority:** Medium  
**Risk:** Low

#### 3.10.1 Description

The system SHALL support simulated emergencies for training, testing, and system validation.

**Related Question:** [How do you simulate emergencies?](#emergency-simulation)

#### 3.10.2 Functional Requirements

**FR-3.10.1** Simulation mode SHALL allow:
- Simulated fire/hazard placement at any location
- Simulated door blockages/route obstructions
- Simulated node failures
- Simulated congestion (varying evacuee densities)
- Simulated environmental conditions (smoke, heat)

**FR-3.10.2** Drill coordination:
- Schedule drills in advance with notifications
- Activate system in "drill mode" (clear indication this is not real emergency)
- Track evacuee progress via motion sensors (anonymized)
- Measure evacuation completion time
- Identify bottlenecks and inefficiencies

**FR-3.10.3** Drill displays SHALL show:
- Standard evacuation guidance (as in real emergency)
- Clear "DRILL" indicator (prevents confusion)
- Optional training messages

**FR-3.10.4** Post-drill reporting:
- Evacuation time analysis (total, per zone, per floor)
- Comparison with previous drills (trend analysis)
- Identified issues (slow areas, confusion points)
- Recommended improvements (layout changes, additional signage)
- Compliance documentation (frequency, participation)

**FR-3.10.5** Scenario testing:
- "What-if" analysis (simulate blocking different exits)
- Worst-case scenario testing (multiple simultaneous hazards)
- Accessibility testing (wheelchair user evacuation times)
- Load testing (system performance under peak conditions)

**FR-3.10.6** Training mode:
- Interactive tutorials for facility staff
- Guided tours of system functionality
- Best practice documentation

### 3.11 Failure Mode Handling

**Priority:** Critical  
**Risk:** High

#### 3.11.1 Description

The system SHALL maintain safe operation even under partial failure conditions.

**Related Questions:**
- [What happens if a sign experiences software failure, physical failure or is damaged/blocked/destroyed?](#node-failure)
- [How do the smoke, heat and power failure affect the operation and what failsafe's might be built in?](#environmental-failure)

#### 3.11.2 Functional Requirements

**FR-3.11.1** Node failure modes:
- **Software crash:** Automatic restart within 30 seconds, load backup configuration
- **Sensor failure:** Continue operation with remaining functional sensors, increased caution in routing
- **Display failure:** Emergency fallback to basic "EXIT" symbol (static LED backup)
- **Network loss:** Autonomous operation mode using last known topology
- **Power loss:** Battery backup activates, minimum 3 hours operation
- **Physical damage:** Neighboring nodes detect failure and route around

**FR-3.11.2** Graceful degradation:
- System SHALL remain partially operational even if up to 30% of nodes fail
- Critical path nodes (primary exits) SHALL have automatic failover (adjacent node takes over display)
- Routes SHALL automatically recalculate to avoid failed nodes

**FR-3.11.3** Power failure handling:
- Instant switchover to battery backup (<100ms interruption)
- Reduced functionality mode (essential features only) to extend battery life
- Low-power mode when battery <20% (basic directional guidance only)
- Persistent storage of critical state before full power loss

**FR-3.11.4** Environmental stress:
- **High temperature (>45°C):** Thermal throttling, reduced computation, increased alert frequency
- **Smoke exposure:** Increased display brightness, simplified guidance (basic arrows only)
- **Physical vibration/impact:** Accelerometer triggers integrity check, alert if damage suspected

**FR-3.11.5** Network partition:
- Isolated segments SHALL continue autonomous operation
- Each segment calculates routes to exits within its partition
- Clear messaging if external assembly points unreachable

**FR-3.11.6** Coordinator failure:
- Mesh network SHALL elect temporary coordinator using priority algorithm
- Nodes SHALL continue peer-to-peer coordination without central server
- Functionality maintained with slightly increased route calculation time

**FR-3.11.7** Cascading failure prevention:
- Circuit breaker pattern (stop propagating failures after threshold)
- Rate limiting (prevent message storms from crashing nodes)
- Watchdog timers (detect and recover from infinite loops)

**FR-3.11.8** Failsafe defaults:
- When confidence drops to 0%, display "SEEK NEAREST EXIT"
- Never display "SAFE" if system cannot confirm safety
- Default to most recent confirmed safe route if recalculation fails
- Static emergency exit signage remains visible if electronics fail completely

**Related Question:** [What happens if a sign experiences software failure, physical failure or is damaged/blocked/destroyed?](#specific-failure-scenarios)

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

**NFR-4.1.1** Route calculation latency:
- Normal operation: <500ms for full building recalculation
- Emergency operation: <2 seconds maximum
- Local route update: <200ms

**NFR-4.1.2** Network latency:
- Critical messages (hazard detection): <100ms node-to-node
- Route updates: <500ms propagation across entire network
- Status updates: <2 seconds

**NFR-4.1.3** Display update latency:
- New guidance visible within 1 second of route change
- Hazard warnings displayed within 500ms of detection

**NFR-4.1.4** System scalability:
- Support for buildings with up to 10,000 nodes
- Handle up to 50 simultaneous route calculations (distributed processing)
- Event throughput: minimum 10,000 events/second (centralized logging)

**Related Question:** [How many concurrent events must the system handle during peak evacuation?](#concurrency-requirements)

**NFR-4.1.5** Sensor sampling rates:
- Smoke: 1 Hz (continuous monitoring)
- Temperature: 0.5 Hz (normal), 2 Hz (elevated conditions)
- Motion: 10 Hz (occupancy detection)
- Ambient light: 0.1 Hz (normal), 1 Hz (emergency)

**NFR-4.1.6** Computational constraints:
- Embedded processor: ARM Cortex-A series or equivalent
- Memory: Minimum 1GB RAM per node
- Storage: Minimum 16GB flash storage per node
- Algorithm complexity: O(E log V) or better for route calculation (E=edges, V=vertices)

**Related Question:** [What is the recalculation rate, what layer of obfuscation is required to do so in a valid time complexity?](#complexity-requirements)

**NFR-4.1.7** Event processing priorities:
- High priority (fire/smoke): Process within 100ms, maximum queue size 100
- Medium priority (congestion): Process within 1s, maximum queue size 1000
- Low priority (status): Best effort, queue size 10000

**Related Question:** [How do you prioritise events (fire spread vs congestion vs sensor failure)?](#event-prioritization)

**NFR-4.1.8** Lag tolerance:
- System SHALL remain safe if computation lags up to 5 seconds behind real-world
- Routes SHALL include safety margins to account for potential delays
- "Stale data" warnings triggered if sensor data >10 seconds old

**Related Question:** [What happens if computation lags behind real-world change?](#computational-lag)

### 4.2 Reliability Requirements

**NFR-4.2.1** System availability:
- 99.9% uptime for non-emergency monitoring functions (8.76 hours downtime/year acceptable)
- 99.99% uptime for emergency evacuation functions (52.6 minutes downtime/year)

**NFR-4.2.2** Mean Time Between Failures (MTBF):
- Individual node: >50,000 hours (5.7 years)
- Overall system (with redundancy): >100,000 hours (11.4 years)

**NFR-4.2.3** Mean Time To Repair (MTTR):
- Node replacement: <2 hours
- Software issue resolution: <4 hours
- Network connectivity: <1 hour

**NFR-4.2.4** Data integrity:
- 99.999% accuracy for logged data
- Zero tolerance for lost emergency event data
- Cryptographic verification of critical system messages

**NFR-4.2.5** Fault tolerance:
- System SHALL continue operation with up to 30% node failures
- Critical path redundancy: minimum 2 independent nodes per primary exit route
- Automatic failover: <5 seconds to activate backup routes

### 4.3 Usability Requirements

**NFR-4.3.1** Evacuee usability:
- Comprehension time: <2 seconds to understand displayed guidance (tested with diverse user groups)
- Cognitive load: Minimal (single clear action, no complex decisions)
- Accessibility: Compliant with Equality Act 2010 and WCAG 2.1 AA

**Related Question:** [Do current methods of signage and routing account for human error in their interpretation under duress?](#comprehension-stress)

**NFR-4.3.2** Facility manager usability:
- Learning curve: <4 hours training for basic operations
- Dashboard intuitiveness: System Usability Scale (SUS) score >75
- Mobile interface: Responsive design, operable on 5" screens minimum

**Related Question:** [How much technical expertise can we reasonably require those in charge of the current systems to possess upon migration?](#expertise-requirements)

**NFR-4.3.3** Emergency responder usability:
- No training required for basic status viewing
- Critical information accessible within 3 clicks from dashboard
- Intuitive visual representation (2D/3D building view)

**NFR-4.3.4** Installation usability:
- Node mounting: <15 minutes per unit (including wiring)
- Initial configuration: Automated where possible, <1 hour for 100-node system
- Documentation: Comprehensive, with visual guides

### 4.4 Security Requirements

**NFR-4.4.1** Physical security:
- Tamper-evident enclosures
- Accelerometer-based tampering detection
- Secure mounting preventing casual removal

**NFR-4.4.2** Network security:
- Encrypted communication: TLS 1.3 or equivalent
- Certificate-based node authentication
- Isolated network segment (VLAN or physical separation)
- No direct internet connectivity for nodes (only coordinator)

**NFR-4.4.3** Access control:
- Role-based access control (RBAC) with minimum 5 defined roles
- Multi-factor authentication (MFA) for administrative functions
- Session management: timeout after 15 minutes inactivity

**NFR-4.4.4** Data security:
- Encryption at rest: AES-256
- Encryption in transit: TLS 1.3
- Secure key management (hardware security module preferred)

**NFR-4.4.5** Audit security:
- Cryptographic log signing (detect tampering)
- Immutable log storage (append-only)
- Separate audit log access control

**NFR-4.4.6** Vulnerability management:
- Security updates deployed within 30 days of disclosure (critical vulnerabilities within 7 days)
- Regular penetration testing (annually minimum)
- CVE monitoring and response process

**Related Questions:**
- [Could evacuation data reveal sensitive building layouts?](#information-security)
- [How do you prevent malicious interference or false signals?](#signal-integrity)
- [Should the system operate in an offline-only emergency mode?](#operational-security)

**NFR-4.4.7** Privacy protection:
- GDPR compliance (UK GDPR)
- Data minimization (collect only necessary data)
- Anonymization of occupant tracking data
- Privacy Impact Assessment (PIA) conducted and documented

**Related Question:** [In what way can this information be shared without inviting malicious attack vectors or compromising the security of the individual?](#privacy-security)

### 4.5 Maintainability Requirements

**NFR-4.5.1** Modularity:
- Hardware: Replaceable components without full node replacement
- Software: Modular architecture enabling component updates
- Sensors: Hot-swappable (where feasible)

**NFR-4.5.2** Diagnostics:
- Built-in self-test (BIST) functionality
- Remote diagnostics capability
- Detailed error reporting with root cause analysis

**NFR-4.5.3** Documentation:
- User manuals (facility manager, emergency responder)
- Technical documentation (system administrator, installer)
- API documentation (developer, integrator)
- Maintenance procedures (technician)

**NFR-4.5.4** Code quality:
- Minimum 80% unit test coverage
- Static analysis tools integrated in CI/CD
- Code review process for all changes
- Documented coding standards

**NFR-4.5.5** Update frequency:
- Security patches: As needed (within 30 days of disclosure)
- Bug fixes: Monthly release cycle
- Feature updates: Quarterly release cycle
- Firmware updates: Semi-annually (unless critical issues)

### 4.6 Compliance Requirements

**NFR-4.6.1** Regulatory compliance:
- BS 5499 Pt 4:2000 (fire safety signs)
- Building Safety Act 2022 (Section 156)
- UK GDPR (data protection)
- Equality Act 2010 (accessibility)
- ISO 7010 (safety symbols)
- ISO 16484 (building automation standards)

**Related Question:** [How will the system support its legislative obligations, and in fact supersede them?](#regulatory-supersession)

**NFR-4.6.2** Compliance documentation:
- Compliance matrix mapping requirements to features
- Third-party audit reports (annually)
- Certification documentation
- Conformity declarations

**NFR-4.6.3** Evidence generation:
- Automated compliance reports
- Audit trail supporting due diligence claims
- Drill documentation meeting regulatory frequency
- Maintenance records demonstrating system upkeep

**Related Question:** [What evidence is required currently to demonstrate baseline 'due diligence' of compliance?](#due-diligence-evidence)

**NFR-4.6.4** Standards supersession:
- System SHALL meet or exceed all BS 5499 requirements
- Additional capabilities beyond minimum compliance clearly documented
- Demonstrable safety improvements over static signage (measured via drill data)

**NFR-4.6.5** Authority approval:
- Fire service consultation during design phase
- Building control approval for installations
- Insurance company notification and potential premium reductions

### 4.7 Environmental Requirements

**NFR-4.7.1** Operating conditions:
- Temperature: -10°C to +50°C (operational), -20°C to +60°C (survival)
- Humidity: 10% to 90% non-condensing
- Dust/particulate: IP54 rating minimum
- Vibration resistance: IEC 60068-2-6 compliant

**NFR-4.7.2** Emergency conditions tolerance:
- Smoke exposure: Maintain functionality for minimum 60 minutes in moderate smoke
- Heat exposure: Maintain functionality up to 65°C for 30 minutes
- Water exposure (sprinkler activation): IP65 rating

**NFR-4.7.3** Power consumption:
- Normal operation: <10W per node
- Emergency operation: <5W per node (battery conservation mode)
- Standby: <2W per node

**NFR-4.7.4** Battery specifications:
- Type: Lithium iron phosphate (LiFePO4) for safety
- Capacity: Minimum 3 hours emergency operation at full brightness
- Lifespan: >5 years before replacement
- Charging: Continuous trickle charge when mains available

**NFR-4.7.5** Environmental responsibility:
- RoHS compliant (restriction of hazardous substances)
- Recyclable materials where possible
- Energy efficiency: Energy Star certification (if applicable category)
- End-of-life disposal program

### 4.8 Testability & Validation Requirements

**NFR-4.8.1** Unit testing:
- Minimum 80% code coverage
- Automated testing in CI/CD pipeline
- Mock external dependencies

**NFR-4.8.2** Integration testing:
- Node-to-node communication tests
- Coordinator integration tests
- Third-party system integration tests

**NFR-4.8.3** System testing:
- End-to-end evacuation scenario tests
- Performance testing (load, stress, endurance)
- Security testing (penetration testing, vulnerability scanning)

**NFR-4.8.4** Field testing:
- Beta deployments in controlled environments
- Real-world drill validation
- User acceptance testing with facility managers

**NFR-4.8.5** Simulation testing:
- Monte Carlo simulations for various emergency scenarios
- Graph algorithm validation (correctness of routing)
- Failure mode injection testing

**Related Question:** [How do you simulate emergencies?](#simulation-methods)

**NFR-4.8.6** Validation metrics:
- Evacuation time improvement vs. static signage: target >20% reduction
- System reliability: <1 critical failure per 100,000 operating hours
- User satisfaction: SUS score >75

**Related Questions:**
- [How do you measure evacuation improvement?](#improvement-metrics)
- [How do you compare static vs smart signage objectively?](#comparison-methodology)

---

## 5. External Interface Requirements

### 5.1 User Interfaces

#### 5.1.1 SmartExit™ Node Display

**UI-5.1.1** Physical specifications:
- Display technology: High-brightness LED matrix
- Size: Minimum 300mm × 150mm visible area
- Resolution: Sufficient for clear symbol rendering (minimum 128×64 pixels)
- Colors: Minimum 3 (green, amber, red) + white

**UI-5.1.2** Display modes:
- **Normal mode:** Static "EXIT" symbol with running person (ISO 7010 E001)
- **Active evacuation mode:** Animated directional arrow + distance
- **Hazard warning mode:** Warning symbol + hazard type + alternative direction
- **Blocked route mode:** "DO NOT ENTER" + alternative direction
- **System fault mode:** "OUT OF SERVICE" (static backup LEDs)

#### 5.1.2 Management Web Dashboard

**UI-5.1.3** Dashboard SHALL provide:
- **Real-time building status:** 2D/3D visualization with node status color-coding
- **Live sensor data:** Temperature, smoke detection status per zone
- **Alert panel:** Current warnings/errors requiring attention
- **Evacuation routes:** Visual representation of active guidance
- **System health:** Node operational status, network topology

**UI-5.1.4** Dashboard views:
- Overview (building-wide status)
- Floor-specific views
- Node detail view (individual unit status)
- Historical data (drill reports, incidents, maintenance)
- Configuration (building model, settings)

**UI-5.1.5** Responsive design:
- Desktop (primary): 1920×1080 minimum
- Tablet: 1024×768 minimum
- Mobile: 375×667 minimum (read-only status viewing)

#### 5.1.3 Mobile Application (First Responders)

**UI-5.1.6** Mobile app SHALL provide:
- Real-time building status
- Hazard locations on floor plan
- Estimated occupant locations (aggregated)
- Manual override controls (with authentication)
- Incident timeline

**UI-5.1.7** Platforms:
- iOS 14.0+ (iPhone, iPad)
- Android 10+ (phone, tablet)

### 5.2 Hardware Interfaces

#### 5.2.1 SmartExit™ Node Interfaces

**HW-5.2.1** Power interface:
- Primary: 230VAC mains via internal power supply, OR Power over Ethernet (PoE 802.3at)
- Backup: Internal battery pack (hot-swappable module)

**HW-5.2.2** Network interfaces:
- Ethernet: RJ45, 10/100/1000 Mbps, PoE-capable
- WiFi: 802.11ac/ax dual-band (2.4GHz + 5GHz)
- Emergency mesh: Sub-GHz proprietary protocol (868MHz or 915MHz depending on region)

**HW-5.2.3** Sensor interfaces:
- I2C bus for internal sensors (temperature, smoke, accelerometer)
- GPIO for auxiliary sensors (motion, light)
- Analog inputs for legacy sensor integration

**HW-5.2.4** Maintenance interface:
- USB-C port for local configuration/diagnostics (covered, tool-access only)
- Physical reset button (recessed, requires pin tool)
- Status LED indicators (power, network, fault)

#### 5.2.2 External Sensor Integration

**HW-5.2.5** Supported sensor types:
- Smoke detectors (photoelectric, ionization, multi-criteria)
- Heat detectors (fixed temperature, rate-of-rise)
- Flame detectors (UV, IR)
- Gas detectors (CO, CO2)
- Occupancy sensors (PIR, ultrasonic, camera-based)
- Door status sensors (magnetic reed, access control)

**HW-5.2.6** Connection methods:
- Wired: 0-10V analog, 4-20mA current loop, dry contact
- Wireless: Zigbee, Z-Wave, BLE
- Network: BACnet, Modbus TCP/RTU, MQTT

### 5.3 Software Interfaces

#### 5.3.1 Fire Alarm Panel Integration

**SW-5.3.1** The system SHALL integrate with fire alarm panels via:
- Proprietary protocols (manufacturer-specific, configurable)
- Dry contact inputs (zone activation signals)
- BACnet MS/TP or BACnet/IP
- Modbus RTU or TCP

**SW-5.3.2** Data received from fire alarms:
- Alarm activation (general)
- Zone-specific activation
- Alarm type (smoke, heat, manual pull)
- System status (normal, fault, test)

#### 5.3.2 Building Management System (BMS) Integration

**SW-5.3.3** BACnet integration:
- BACnet/IP (primary)
- BACnet MS/TP (legacy systems)
- Exposed objects: Analog Input (sensors), Binary Output (display status)

**SW-5.3.4** Data exchanged with BMS:
- HVAC operational status (fan on/off, damper positions)
- Door lock status
- Lighting levels
- Occupancy data
- System alerts

#### 5.3.3 Access Control System Integration

**SW-5.3.5** The system SHALL receive from access control:
- Door open/closed status
- Lock/unlock status
- Card swipe events (for occupancy estimation, anonymized)

**SW-5.3.6** The system MAY send to access control:
- Emergency unlock commands (fail-safe mode)
- Restricted area lockdown (prevent entry to hazardous zones)

#### 5.3.4 Emergency Services Integration

**SW-5.3.7** Standard protocols:
- CAP (Common Alerting Protocol) for incident notifications
- EDXL (Emergency Data Exchange Language) for resource coordination
- Web services API for fire service dashboard access

**SW-5.3.8** Data shared with emergency services (time-limited access during incidents):
- Building layout and floor plans
- Current hazard locations
- Active evacuation routes
- Estimated occupant locations (aggregated, anonymized)
- System operational status
- Incident timeline

### 5.4 Communication Interfaces

#### 5.4.1 Network Protocols

**COM-5.4.1** Application layer:
- HTTPS (RESTful API)
- WebSocket (real-time updates)
- MQTT (IoT device communication)
- SNMP (network management)

**COM-5.4.2** Transport layer:
- TCP (reliable delivery for critical messages)
- UDP (time-sensitive but non-critical updates)

**COM-5.4.3** Network layer:
- IPv4 (required)
- IPv6 (supported)
- Multicast for efficient broadcast to multiple nodes

**COM-5.4.4** Data link layer:
- Ethernet (IEEE 802.3)
- WiFi (IEEE 802.11ac/ax)
- Proprietary mesh (time-division multiple access)

#### 5.4.2 API Specifications

**COM-5.4.5** RESTful API endpoints (examples):
- `GET /api/v1/building/status` - Overall building status
- `GET /api/v1/nodes` - List all nodes
- `GET /api/v1/nodes/{id}` - Specific node details
- `POST /api/v1/routes/calculate` - Manual route calculation
- `POST /api/v1/emergency/activate` - Trigger evacuation
- `GET /api/v1/logs` - Retrieve event logs
- `PUT /api/v1/config/building` - Update building model

**COM-5.4.6** WebSocket topics (pub/sub):
- `/events/hazards` - Real-time hazard detection
- `/events/routes` - Route recalculations
- `/events/nodes/{id}/status` - Per-node status updates
- `/events/system/alerts` - System-wide alerts

**COM-5.4.7** Authentication:
- OAuth 2.0 with JWT tokens
- API keys for service-to-service
- Certificate-based for node authentication

---

## 6. System Constraints

### 6.1 Technical Constraints

**CONST-6.1.1** The system MUST operate within real-time constraints (<2s route recalculation) even in large buildings (10,000+ nodes)

**CONST-6.1.2** Nodes SHALL be limited to embedded computing resources (ARM-class processors, 1-2GB RAM)

**CONST-6.1.3** Display surface area is constrained by fire safety sign standards (approximately 300mm × 150mm)

**CONST-6.1.4** Battery backup duration constrained by practical weight/size limitations (3-4 hours maximum)

**CONST-6.1.5** Wireless mesh range limited by building materials and interference (~30-50m in typical commercial buildings)

**Related Question:** [What is the recalculation rate, what layer of obfuscation is required to do so in a valid time complexity and not stumble to a pitfall of super polynomial or intractable complexities?](#algorithmic-constraints)

### 6.2 Business Constraints

**CONST-6.2.1** The system SHALL be cost-competitive with traditional static signage over a 10-year lifecycle

**CONST-6.2.2** Installation SHALL NOT require building closure (retrofit-friendly)

**CONST-6.2.3** The system SHALL be operable by facility staff with minimal technical training (<4 hours)

**CONST-6.2.4** Vendor lock-in SHALL be minimized through use of open standards and documented APIs

### 6.3 Regulatory Constraints

**CONST-6.3.1** All signage SHALL meet or exceed BS 5499 Pt 4:2000 requirements

**CONST-6.3.2** The system SHALL comply with UK GDPR regarding any occupant tracking data

**CONST-6.3.3** Installations SHALL receive building control approval before commissioning

**CONST-6.3.4** Fire service SHALL be consulted during installation planning

**CONST-6.3.5** The system SHALL NOT replace required emergency lighting (complementary system only)

### 6.4 Ethical Constraints

**CONST-6.4.1** The system SHALL prioritize human safety over all other considerations (including property protection)

**CONST-6.4.2** No individual SHALL be identifiable from occupancy tracking data without explicit consent

**CONST-6.4.3** System logging SHALL NOT be used for employee surveillance purposes

**CONST-6.4.4** Failure modes SHALL be transparent and not create false sense of security

**Related Question:** [Who is authorised to override automated decisions?](#override-authority)

### 6.5 Operational Constraints

**CONST-6.5.1** The system SHALL remain operational during power outages (battery backup)

**CONST-6.5.2** The system SHALL NOT interfere with emergency services radio communication

**CONST-6.5.3** Maintenance SHALL be performed during scheduled windows with minimal disruption

**CONST-6.5.4** The system SHALL degrade gracefully rather than fail catastrophically

---

## 7. Appendices

### 7.1 Requirements Traceability Matrix

This section maps the questions posed in the original problem definition to specific requirements in this document.

| Question Category | Question Summary | Related Requirements |
|------------------|------------------|---------------------|
| **Human Factors & Usability** | Do current methods account for human error under duress? | FR-3.3.1 to FR-3.3.10, NFR-4.3.1 |
| **Risk & Compliance** | Is compliance adequate for safety? | Section 1.3, NFR-4.6.1 to NFR-4.6.5 |
| **Routing & Optimization** | Will system optimize for shortest/safest/least congested? | FR-3.1.3, FR-3.1.5, FR-3.1.6 |
| **User Group Considerations** | Considerations for disabled, children, patients? | FR-3.1.3, FR-3.3.7 |
| **Degradation Detection** | How is signage degradation detected? | FR-3.5.1 to FR-3.5.7 |
| **Layout Changes** | How are layout changes detected and updated? | FR-3.6.4, FR-3.5.5 |
| **Failure Handling** | What happens if sign fails or is destroyed? | FR-3.11.1 to FR-3.11.8 |
| **Multi-Floor & Complex Buildings** | Behavior in multi-floor/multi-tenant buildings? | FR-3.6.6 to FR-3.6.8 |
| **Environmental Resilience** | How do smoke, heat, power failure affect operation? | FR-3.11.3, FR-3.11.4, NFR-4.7.2 |
| **Sensors** | Which sensors are integral vs. optional? | FR-3.2.1 to FR-3.2.3 |
| **Testing & Maintenance** | Testing frequency and methods? | FR-3.5.2, FR-3.10.1 to FR-3.10.6 |
| **Confidence & Safety Thresholds** | Confidence level before route deemed unsafe? | FR-3.1.7 to FR-3.1.9 |
| **External Integration** | What external systems integrate? | FR-3.9.1, FR-3.9.2 |
| **Graph Modeling** | What graphing models represent building? | FR-3.1.1 |
| **Edge Weighting** | How are edges weighted? | FR-3.1.2 |
| **Algorithmic Complexity** | Recalculation rate and complexity? | FR-3.1.4, FR-3.1.5, NFR-4.1.1, NFR-4.1.6 |
| **Network Architecture** | Central coordinator or decentralized mesh? | FR-3.4.1 to FR-3.4.10 |
| **Node Discovery** | How do nodes discover each other? | FR-3.4.3 |
| **Network Partitions** | What happens if network partitions occur? | FR-3.4.6, FR-3.4.7 |
| **Consensus** | How is consensus reached on route safety? | FR-3.4.5 |
| **Cascading Failures** | How to prevent cascading failures? | FR-3.4.8 |
| **Concurrent Events** | How many concurrent events handled? | NFR-4.1.4, NFR-4.1.7 |
| **Event Prioritization** | How are events prioritized? | NFR-4.1.7 |
| **Computational Lag** | What if computation lags behind real-world? | NFR-4.1.8 |
| **Display Design** | What information on signs? Symbols vs. text? | FR-3.3.2 to FR-3.3.7 |
| **Information Overload** | How much information is too much? | FR-3.3.3, FR-3.3.5 |
| **Guidance Consistency** | How to prevent contradictory guidance? | FR-3.3.9 |
| **Ignored Guidance** | What if dynamic sign is ignored? | FR-3.3.10 |
| **Firmware Updates** | How are updates safely deployed? | FR-3.8.1 to FR-3.8.7 |
| **Emergency Simulation** | How to simulate emergencies? | FR-3.10.1 to FR-3.10.5 |
| **Security & Privacy** | Could data reveal sensitive layouts? Prevent malicious attack? | NFR-4.4.1 to NFR-4.4.7, FR-3.7.7 |
| **External Control** | Should firefighters have routing control? | FR-3.9.2, FR-3.9.3 |
| **Compliance Evidence** | What evidence demonstrates due diligence? | FR-3.7.8, NFR-4.6.3 |
| **Incident Investigation** | System robustness under investigative scrutiny? | FR-3.7.3, FR-3.7.9, FR-3.7.10 |
| **Liability Concerns** | Does logging invite liability? | FR-3.7.10 (addresses this concern) |
| **Data Ownership** | Who owns the data? Retention policies? | FR-3.7.5, FR-3.7.6 |
| **Deployment Versatility** | Versatility across different building types? | Section 2.1, FR-3.6.1, FR-3.6.9 |
| **Model Accuracy** | Degree of accuracy in building model? | FR-3.6.3 |
| **Model Maintenance** | How is model kept up to date? | FR-3.6.4 |
| **Obstruction Detection** | How are obstructions detected? | FR-3.2.6, FR-3.2.7 |
| **Expertise Requirements** | Technical expertise required for operation? | Section 2.3, NFR-4.3.2 |
| **Data Extensibility** | Extensible benefits of data? | FR-3.9.2, FR-3.9.4 to FR-3.9.6 |
| **Testing & Validation** | How to measure improvement vs. static signage? | NFR-4.8.5, NFR-4.8.6 |

### 7.2 Glossary of Terms

| Term | Definition |
|------|------------|
| **Assembly Point** | Designated safe location outside building where evacuees gather after evacuation |
| **BACnet** | Building Automation and Control Networks protocol (ASHRAE standard) |
| **Confidence Score** | Numerical representation (0-100%) of system certainty in route safety |
| **Edge** | Connection between two nodes/vertices in graph representation of building |
| **Evacuee** | Person being evacuated from building during emergency |
| **Failsafe** | Design principle where system defaults to safe state upon failure |
| **Fire Alarm Panel** | Central control system for fire detection and alarm devices |
| **Graceful Degradation** | System maintaining partial functionality after component failures |
| **Graph** | Mathematical representation of building as vertices (locations) and edges (paths) |
| **Hazard** | Detected danger such as fire, smoke, or obstruction |
| **Mesh Network** | Network topology where nodes connect peer-to-peer without central hub |
| **Node** | Individual SmartExit™ unit within the network |
| **Refuge Area** | Fire-protected space where evacuees can await rescue if routes blocked |
| **Route Confidence** | Measure of data quality and freshness supporting route recommendation |
| **SmartExit™** | Intelligent fire exit sign hardware unit |
| **SmartRoute™** | Proprietary software system for route calculation and monitoring |
| **Topology** | Spatial arrangement and connectivity of nodes within building |
| **Vertex** | Point in graph representation (room, intersection, exit) |

### 7.3 Assumptions

1. Buildings have structural integrity allowing evacuation (not applicable for building collapse scenarios)
2. Basic electrical and network infrastructure available for node installation
3. Digital or paper floor plans available for initial system configuration
4. Organizations commit to ongoing system maintenance and testing
5. Evacuees are physically capable of following guidance (specialized assistance for mobility-impaired in scope)
6. Emergency services response times align with UK averages (8-10 minutes for urban areas)
7. Building occupants have basic familiarity with emergency exit signage concepts
8. Regulatory environment remains stable (BS 5499, Building Safety Act 2022)

### 7.4 Dependencies

**External Dependencies:**
1. **Hardware Suppliers:** LED panels, sensors, embedded computing modules
2. **Network Infrastructure:** Ethernet cabling, WiFi access points, PoE switches
3. **Third-Party Systems:** Fire alarm panels, BMS, access control systems
4. **Standards Bodies:** ISO, BSI, ASHRAE (for protocol specifications)
5. **Regulatory Authorities:** Local fire services, building control, Health & Safety Executive

**Internal Dependencies:**
1. **Software Development:** Route calculation algorithms, display rendering, network protocols
2. **System Integration:** API development for external system connectivity
3. **Data Management:** Database design, log storage infrastructure
4. **Testing Infrastructure:** Simulation environments, drill coordination tools
5. **Documentation:** User manuals, technical specifications, compliance documentation

### 7.5 Acronyms and Abbreviations

| Acronym | Full Form |
|---------|-----------|
| **API** | Application Programming Interface |
| **BACnet** | Building Automation and Control Networks |
| **BIST** | Built-In Self-Test |
| **BLE** | Bluetooth Low Energy |
| **BMS** | Building Management System |
| **CAP** | Common Alerting Protocol |
| **CMMS** | Computerized Maintenance Management System |
| **CVE** | Common Vulnerabilities and Exposures |
| **EDXL** | Emergency Data Exchange Language |
| **GDPR** | General Data Protection Regulation |
| **GPIO** | General Purpose Input/Output |
| **HVAC** | Heating, Ventilation, and Air Conditioning |
| **I2C** | Inter-Integrated Circuit (communication protocol) |
| **IFC** | Industry Foundation Classes (building model format) |
| **IoT** | Internet of Things |
| **IP** | Ingress Protection (rating for dust/water resistance) |
| **ISO** | International Organization for Standardization |
| **JWT** | JSON Web Token |
| **LED** | Light-Emitting Diode |
| **MFA** | Multi-Factor Authentication |
| **MQTT** | Message Queuing Telemetry Transport |
| **MTBF** | Mean Time Between Failures |
| **MTTR** | Mean Time To Repair |
| **ONVIF** | Open Network Video Interface Forum |
| **PIR** | Passive Infrared (motion sensor) |
| **PoE** | Power over Ethernet |
| **RBAC** | Role-Based Access Control |
| **RF** | Radio Frequency |
| **RoHS** | Restriction of Hazardous Substances |
| **SUS** | System Usability Scale |
| **TLS** | Transport Layer Security |
| **UDP** | User Datagram Protocol |
| **WCAG** | Web Content Accessibility Guidelines |

### 7.6 References

1. [LH CFP - Safety Signs Guidance](https://www.lhcfp.co.uk/safetysignsguidance.pdf) - UK fire exit sign requirements
2. [Fire Protection Online - UK Fire Exit Signs Regulations](https://www.fireprotectiononline.co.uk/info/the-uk-fire-exit-signs-regulations/) - Regulatory compliance guide
3. [IBTimes - Fire Safety After Grenfell](https://www.ibtimes.co.uk/fire-safety-after-grenfell-why-emergency-signage-still-falls-short-1733205) - Post-Grenfell signage analysis
4. [UK Government - Fire Statistics](https://www.gov.uk/government/statistical-data-sets/fire0102-previous-data-tables) - Official fire incident data
5. [UK Government - Fire Casualties](https://www.gov.uk/government/statistical-data-sets/fire0301-previous-data-tables) - Casualty statistics
6. BS 5499 Pt 4:2000 - Safety signs including fire safety signs
7. Building Safety Act 2022 - UK legislation (Section 156)
8. ISO 7010:2019 - Graphical symbols for safety colors and safety signs
9. UK GDPR - Data protection framework
10. Equality Act 2010 - Accessibility requirements

### 7.7 Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Lead | [To be assigned] | | |
| Technical Architect | [To be assigned] | | |
| Safety Consultant | [To be assigned] | | |
| Facility Manager Representative | [To be assigned] | | |
| First Responder Liaison | [To be assigned] | | |

### 7.8 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-03 | MKJM563 | Initial draft based on problem definition and questions |

---

## Document End

This Software Requirements Specification provides a comprehensive foundation for the SmartExit™ Fire Evacuation System development. All requirements are traceable to the original problem statement and questions posed, ensuring that the system addresses real-world challenges in emergency evacuation while maintaining compliance, safety, and usability.

**Next Steps:**
1. Technical review by fire safety experts
2. Consultation with fire and rescue services
3. Prototype development plan
4. Pilot site selection
5. Iterative refinement based on stakeholder feedback
