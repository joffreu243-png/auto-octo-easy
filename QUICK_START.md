# 🚀 Quick Start Guide

## How to Run OctoMaster Pro

### Option 1: Direct Python Execution (Recommended)

```bash
# Using the run script (sets up environment variables)
./run.sh

# Or directly with Python
python3 main.py
```

### Option 2: After Package Installation

If you installed the package with `pip install -e .`, you can run:

```bash
# GUI mode
octomaster

# CLI mode (not yet implemented)
octomaster-cli
```

**Important:** If you get a "CLI not yet implemented" error, it means you're running the wrong entry point. Use Option 1 instead.

### Option 3: Using Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Dependencies

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

Key dependencies:
- PyQt6 >= 6.6.0
- playwright >= 1.40.0
- selenium >= 4.16.0
- qasync >= 0.24.0
- httpx[http2] >= 0.25.0
- loguru >= 0.7.2

## Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"

**Solution:** Install dependencies:
```bash
pip install -r requirements.txt
```

### "CLI not yet implemented" error

**Solution:** You're running the wrong entry point. Use:
```bash
python3 main.py
```

### Package installation issues

If you installed with `pip install -e .` and want to update to the latest code:

```bash
# Uninstall the package
pip uninstall octomaster-pro

# Run directly instead
python3 main.py
```

Or reinstall:
```bash
pip install -e .
```

## Environment Variables

The application sets these automatically, but you can override them:

```bash
# Disable GPU acceleration (useful in VMs)
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer --no-sandbox"
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_SOFTWARE=1

# Disable Qt warnings
export QT_LOGGING_RULES="*.debug=false;qt.qpa.*=false"

# Set log level
export LOG_LEVEL=INFO  # or DEBUG, WARNING, ERROR
```

## First Run

1. **Start the application:**
   ```bash
   python3 main.py
   ```

2. **Configure Octo Browser** (if using Octo integration):
   - Go to `Tools → 🌐 Octo Browser Settings...`
   - Enter your API Token from Octo Browser
   - Click "Test Connection"
   - Click "Save"

3. **Create your first workflow:**
   - `File → New Workflow` (Ctrl+N)
   - Use the Inspector Mode to record actions
   - Save the workflow (Ctrl+S)

4. **Export to Python script:**
   - `File → Export → Export with 🌐 Octo Browser...`
   - Select a profile
   - Generate and save the script

## Getting Help

- Documentation: See README.md and other guides
- Issues: Report bugs on GitHub
- Logs: Check `logs/octomaster_*.log` for error details

---

**Happy automating! 🎯**
