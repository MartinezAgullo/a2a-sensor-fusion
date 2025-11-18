# A2A Sensor Fusion

## Prototype 1

**Prototype 1**: Notebook-based version. This code simulates a sensor fusion system where a **Fusion Agent** orchestrates an **Agent-to-Agent (A2A) Task** to retrieve raw data from two simulated **Sensor Agents** (`Radar` and `Visual`), normalizes that data using a local **Model Context Protocol (MCP)** function, and produces a final standardized **A2A Artifact** (report).

## Prototype 2

**Prototype 2**: More complex implementation of [prototype_1.ipynb](prototypes/prototype_1.ipynb). Uses more complete definition of the models ([models.py](prototypes/prototype_2/models.py)), servers ([sensor_radar_server.py](prototypes/prototype_2/sensor_radar_server.py) and [sensor_visual_server.py](prototypes/prototype_2/sensor_visual_server.py)), client ([mcp_tool.py](prototypes/prototype_2/main_fusion_client.py)) and mcp tool ([mcp_tool.py](prototypes/prototype_2/mcp_tool.py)). The servers are executed on ports 8001 and 8002.

Initialise servers:
```bash
# Terminal 1
source .venv/bin/activate  
cd prototype_2/
python sensor_radar_server.py

# Terminal 2
source .venv/bin/activate
cd prototype_2/
python python sensor_visual_server.py
```

Execute clients:
```bash
# Terminal 3
source .venv/bin/activate
cd prototype_2/
python main_fusion_client.py

```

The modular design in [prototype 2](prototypes/prototype_2) allos to easily add a new sensor (Acoustic, Infrared, LIDAR, EW, Weather, whatever)

<!-- Note that the tasks to the server could be submited via POST commands
```bash
# To Radar Agent
curl -X POST http://localhost:8001/process_task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"test","sector_id":"Test","request_type":"track"}'

# To Visual Agent
curl -X POST http://localhost:8002/process_task \
  -H "Content-Type: application/json" \
  -d '{"task_id":"test","sector_id":"Test","request_type":"track"}'
``` -->
Alternatively:
```bash
# Terminal 3
source .venv/bin/activate  
cd prototype_2/
source run_system.sh 
```

## Prototype 3

**Prototype 3**: Enhancements:
 * Add AgentCard, AgentSkill, and Discovery to A2A agents. 
 * Convert [mcp_tool.py](prototypes/prototype_2/mcp_tool.py) into a real MCP server using the official MCP SDK

 ```bash
source .venv/bin/activate  
cd prototype_3/
source run_system.sh 
```
