#!/bin/bash

# Prototype 4: Full A2A SDK Integration - Startup Script
# =======================================================

echo "🚀 Starting Prototype 4: Full A2A SDK Integration"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected!"
    echo "   Consider activating .venv first"
    echo ""
fi

# Create logs directory
mkdir -p logs

# Start Radar Agent in background
echo "📡 Starting Radar Agent (Port 8001)..."
python sensor_radar_server.py > logs/logs_radar.txt 2>&1 &
RADAR_PID=$!
sleep 3

# Start Visual Agent in background
echo "👁️  Starting Visual Agent (Port 8002)..."
python sensor_visual_server.py > logs/logs_visual.txt 2>&1 &
VISUAL_PID=$!
sleep 3

# Check if servers are up
echo ""
echo "✅ Checking server health..."
if curl -s http://localhost:8001/.well-known/ai-agent.json > /dev/null; then
    echo "   ✓ Radar Agent operational"
else
    echo "   ✗ Radar Agent failed to start"
fi

if curl -s http://localhost:8002/.well-known/ai-agent.json > /dev/null; then
    echo "   ✓ Visual Agent operational"
else
    echo "   ✗ Visual Agent failed to start"
fi

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