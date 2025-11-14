# Troubleshooting Guide - OctoMaster Pro

## Browser Panel Crashes / Segmentation Fault

**Symptoms:**
- Application crashes when opening Browser panel
- `Segmentation fault (core dumped)` error
- EGL/GPU errors in console
- `ImageEGL.cpp:112 (operator()): eglCreateImage failed` errors

**Cause:**
This is a known issue with Qt WebEngine GPU rendering in virtual machines (VMware, VirtualBox, etc.).

### Solution 1: Use the Safe Startup Script (Recommended)

```bash
./run.sh
```

This script automatically sets the required environment variables.

### Solution 2: Set Environment Variables Manually

Before running the application:

```bash
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --disable-software-rasterizer --no-sandbox"
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_SOFTWARE=1

python main.py
```

### Solution 3: Create .env File

Copy `.env.example` to `.env` and ensure these lines are present:

```env
QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu --disable-software-rasterizer --no-sandbox
QT_XCB_GL_INTEGRATION=none
LIBGL_ALWAYS_SOFTWARE=1
```

Then run normally:
```bash
python main.py
```

### Solution 4: Disable Browser Panel

If the above solutions don't work, the Browser Panel will show a warning message but the application will continue to work. You can use:

1. **Workflow Executor** - Run workflows using Playwright (external browser)
2. **Recorder** - Record actions in external browser
3. **CLI Mode** - Run workflows from command line

**Note:** The embedded Browser Panel is for preview only. For actual automation, Playwright browser is used (which works fine in VMs).

---

## Missing PyQt6-WebEngine

**Symptoms:**
- `ImportError: cannot import name 'QWebEngineView'`
- Browser panel shows "Not Available" message

**Solution:**

Install PyQt6-WebEngine:

```bash
pip install PyQt6-WebEngine
```

---

## Playwright Browser Issues

**Symptoms:**
- "Browser not found" error
- Playwright fails to start

**Solution:**

Install Playwright browsers:

```bash
playwright install chromium
# Or for all browsers:
playwright install
```

---

## Database Errors

**Symptoms:**
- `sqlalchemy.exc.OperationalError`
- Database locked errors

**Solution:**

1. Close all OctoMaster instances
2. Delete `octomaster.db` file (if safe to do so)
3. Restart the application

---

## Import Errors

**Symptoms:**
- `ModuleNotFoundError`
- Missing dependencies

**Solution:**

Reinstall all dependencies:

```bash
pip install -r requirements.txt
```

---

## Logging and Debugging

Enable detailed logging:

```bash
LOG_LEVEL=DEBUG python main.py
```

Logs are saved to `logs/` directory.

---

## Virtual Machine Specific Issues

### VMware Workstation/Player

1. Enable 3D acceleration in VM settings (may help or hurt)
2. Increase video memory to 256MB+
3. Use the `run.sh` script

### VirtualBox

1. Disable 3D acceleration in VM settings
2. Use VBoxSVGA graphics controller
3. Use the `run.sh` script

### WSL2 (Windows Subsystem for Linux)

1. Install VcXsrv or similar X server
2. Set DISPLAY variable: `export DISPLAY=:0`
3. Use software rendering

---

## Performance Issues

**Slow visual editor:**

1. Reduce number of blocks in workflow
2. Disable animations in settings
3. Close unused panels

**High memory usage:**

1. Close Browser panel when not needed
2. Limit concurrent workflow executions
3. Clear temp files regularly

---

## Still Having Issues?

1. Check logs in `logs/` directory
2. Run with `DEBUG=true LOG_LEVEL=DEBUG`
3. Create GitHub issue with:
   - Your OS and version
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce

---

## Quick Reference

### Safe Start (VM)
```bash
./run.sh
```

### Normal Start
```bash
python main.py
# or
./venv/bin/python main.py
```

### CLI Mode
```bash
python -m octomaster.cli workflow run my_workflow.json
```

### Debug Mode
```bash
DEBUG=true LOG_LEVEL=DEBUG python main.py
```
