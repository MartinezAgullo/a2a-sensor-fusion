### Core Components

1.  **Data Models** (`models.py`)
    -   `RadarData`: Polar coordinate format (range, azimuth)
    -   `VisualData`: Classification with certainty percentage
    -   `NormalizedTarget`: Standardized Cartesian output
    -   `A2ATask`: Request structure for agent communication
    -   `A2AArtifact`: Final fusion report structure

2.  **MCP Tool** (`mcp_tool.py`)
    -   Converts polar → Cartesian coordinates
    -   Normalizes confidence scores (0-100% → 0.0-1.0)
    -   Standardizes target classification
    -   Pure function, easily testable

3.  **Radar Agent** (`sensor_radar_server.py`)
    -   FastAPI server on port 8001
    -   Simulates radar sensor readings
    -   Returns range and azimuth in polar coordinates
    -   Health check endpoint

4.  **Visual Agent** (`sensor_visual_server.py`)
    -   FastAPI server on port 8002
    -   Simulates visual classification
    -   Returns target type and certainty percentage
    -   Health check endpoint

5.  **Fusion Agent** (`main_fusion_client.py`)
    -   Orchestrates A2A communication
    -   Sends tasks to both sensor agents
    -   Collects disparate data
    -   Invokes MCP tool for normalization
    -   Generates final A2A artifact (report)




                    ╔══════════════════════════════════════════╗
                    ║         USER / OPERATOR                  ║
                    ║    "Track target in Alpha Sector"        ║
                    ╚═════════════════╤════════════════════════╝
                                      │
                                      ▼
    ╔═══════════════════════════════════════════════════════════════╗
    ║                    FUSION AGENT (Client)                      ║
    ║                   main_fusion_client.py                       ║
    ║                      Port: Client Side                        ║
    ╠═══════════════════════════════════════════════════════════════╣
    ║                                                               ║
    ║  Phase 1: A2A Task Creation                                   ║
    ║  ┌─────────────────────────────────────────────┐              ║
    ║  │ A2ATask(                                     │             ║
    ║  │   task_id="uuid",                            │             ║
    ║  │   sector_id="Alpha Sector",                  │             ║
    ║  │   request_type="track"                       │             ║
    ║  │ )                                            │             ║
    ║  └─────────────────────────────────────────────┘              ║
    ║                                                               ║
    ║  Phase 2: A2A Communication (HTTP POST)                       ║
    ║  ┌───────────────────────┐  ┌───────────────────────┐         ║
    ║  │  → Radar Agent        │  │  → Visual Agent       │         ║
    ║  │  (localhost:8001)     │  │  (localhost:8002)     │         ║
    ║  └───────────────────────┘  └───────────────────────┘         ║
    ║                                                               ║
    ║  Phase 3: Collect Raw Data                                    ║
    ║  ┌───────────────────────┐  ┌───────────────────────┐         ║
    ║  │ RadarData:            │  │ VisualData:           │         ║
    ║  │ • range: 2384.8m      │  │ • class: "drone"      │         ║
    ║  │ • azimuth: 97.4°      │  │ • certainty: 95%      │         ║
    ║  └───────────────────────┘  └───────────────────────┘         ║
    ║                                                               ║
    ║  Phase 4: MCP Tool Call                                       ║
    ║  ┌─────────────────────────────────────────────┐              ║
    ║  │ data_normalization_tool()                   │              ║
    ║  │                                             │              ║
    ║  │ Input: RadarData + VisualData               │              ║
    ║  │                                             │              ║
    ║  │ Processing:                                 │              ║
    ║  │ 1. Polar → Cartesian conversion             │              ║
    ║  │    X = R × cos(θ) = -307.15m                │              ║
    ║  │    Y = R × sin(θ) = 2364.94m                │              ║
    ║  │                                             │              ║
    ║  │ 2. Confidence normalization                 │              ║ 
    ║  │    95% → 0.95                               │              ║
    ║  │                                             │              ║
    ║  │ Output: NormalizedTarget                    │              ║
    ║  └─────────────────────────────────────────────┘              ║
    ║                                                               ║
    ║  Phase 5: A2A Artifact Generation                             ║
    ║  ┌─────────────────────────────────────────────┐              ║
    ║  │ A2AArtifact(                                │              ║
    ║  │   fusion_id="RPT-0dba53be",                 │              ║
    ║  │   targets=[NormalizedTarget],               │              ║
    ║  │   summary="Track successful..."             │              ║
    ║  │ )                                           │              ║
    ║  └─────────────────────────────────────────────┘              ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            │                                                   │
            ▼                                                   ▼
    ╔═══════════════════╗                         ╔═══════════════════╗
    ║  RADAR AGENT      ║                         ║  VISUAL AGENT     ║
    ║  (A2A Server)     ║                         ║  (A2A Server)     ║
    ║                   ║                         ║                   ║
    ║ sensor_radar_     ║                         ║ sensor_visual_    ║
    ║ server.py         ║                         ║ server.py         ║
    ║                   ║                         ║                   ║
    ║ Port: 8001        ║                         ║ Port: 8002        ║
    ╠═══════════════════╣                         ╠═══════════════════╣
    ║                   ║                         ║                   ║
    ║ Endpoints:        ║                         ║ Endpoints:        ║
    ║ • GET /           ║                         ║ • GET /           ║
    ║   Health check    ║                         ║   Health check    ║
    ║                   ║                         ║                   ║
    ║ • POST /          ║                         ║ • POST /          ║
    ║   process_task    ║                         ║   process_task    ║
    ║                   ║                         ║                   ║
    ║ Output Format:    ║                         ║ Output Format:    ║
    ║ ┌───────────────┐ ║                         ║ ┌───────────────┐ ║
    ║ │ RadarData:    │ ║                         ║ │ VisualData:   │ ║
    ║ │ • range_m     │ ║                         ║ │ • class       │ ║
    ║ │ • azimuth_deg │ ║                         ║ │ • certainty_% │ ║
    ║ └───────────────┘ ║                         ║ └───────────────┘ ║
    ║                   ║                         ║                   ║
    ║ Simulates:        ║                         ║ Simulates:        ║
    ║ • Radar hardware  ║                         ║ • Camera/sensor   ║
    ║ • Distance calc   ║                         ║ • ML classifier   ║
    ║ • Bearing measure ║                         ║ • Confidence score║
    ║                   ║                         ║                   ║
    ╚═══════════════════╝                         ╚═══════════════════╝




<!-- ```
┌─────────────────────────────────────────────────────────────┐
│                  USER REQUEST                               │
│          "Track target in Alpha Sector"                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│               FUSION AGENT (Client)                         │
│                                                             │
│  1️⃣  Create A2ATask(sector_id="Alpha Sector")               │
│                                                             │
│  2️⃣  Send HTTP POST → Radar Agent                           │
│     Response: {range_meters: 2384.8, azimuth_degrees: 97.4} │
│                                                             │
│  3️⃣  Send HTTP POST → Visual Agent                          │
│     Response: {classification: "drone", certainty: 95}      │
│                                                             │
│  4️⃣  Call MCP Tool: data_normalization_tool()               │
│     Input: RadarData + VisualData                           │
│     Processing:                                             │
│       - Convert polar → Cartesian                           │
│       - Normalize confidence 95% → 0.95                     │
│     Output: NormalizedTarget                                │
│       {x: -307.15, y: 2364.94, type: "DRONE", conf: 0.95}   │
│                                                             │
│  5️⃣  Generate A2AArtifact (Final Report)                    │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   OUTPUT TO USER                            │
│              JSON Report + Summary                          │
└─────────────────────────────────────────────────────────────┘

``` -->
