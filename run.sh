#!/bin/bash
# OctoMaster Pro - Safe Startup Script
# This script sets environment variables to prevent GPU crashes in VMs

echo "Starting OctoMaster Pro..."

# Disable GPU acceleration for Qt WebEngine
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer --no-sandbox --disable-dev-shm-usage"
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_SOFTWARE=1

# Disable Qt warnings
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"

# Run the application
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    ./venv/bin/python main.py "$@"
elif command -v python3 &> /dev/null; then
    echo "Using system Python..."
    python3 main.py "$@"
else
    echo "Error: Python not found"
    exit 1
fi
