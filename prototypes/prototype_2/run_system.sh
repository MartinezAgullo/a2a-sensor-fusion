#!/bin/bash

# Autonomous Sensor Fusion Agent - Startup Script
# ================================================

echo "🚀 Starting Autonomous Sensor Fusion Agent System"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected!"
    echo "   Consider activating .venv first: source .venv/bin/activate"
    echo ""
fi

# Start Radar Agent in background
echo "📡 Starting Radar Agent (Port 8001)..."
python sensor_radar_server.py > logs/logs_radar.txt 2>&1 &
RADAR_PID=$!
sleep 2

# Start Visual Agent in background
echo "👁️  Starting Visual Agent (Port 8002)..."
python sensor_visual_server.py > logs/logs_visual.txt 2>&1 &
VISUAL_PID=$!
sleep 2

# Check if servers are up
echo ""
echo "✅ Checking server health..."
curl -s http://localhost:8001/ > /dev/null && echo "   ✓ Radar Agent operational" || echo "   ✗ Radar Agent failed"
curl -s http://localhost:8002/ > /dev/null && echo "   ✓ Visual Agent operational" || echo "   ✗ Visual Agent failed"

echo ""
echo "🎯 Running Fusion Agent..."
echo "=================================================="
python main_fusion_client.py

# Cleanup
echo ""
echo "🛑 Shutting down agents..."
kill $RADAR_PID $VISUAL_PID 2>/dev/null
echo "✅ All agents stopped"
echo ""
echo "📋 Server logs available in:"
echo "   - logs/logs_radar.txt"
echo "   - logs/logs_visual.txt"