# Windows Installation Guide for OctoMaster Pro

Complete guide for installing and running OctoMaster Pro on Windows 10/11.

## Prerequisites

### 1. Python Installation

**Supported Versions: Python 3.11, 3.12, or 3.13**

⚠️ **WARNING:** Do NOT use Python 3.14 (development version - not stable!)

1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install pip"
   - Choose "Customize installation"
   - ✅ Enable "Install for all users" (optional but recommended)

3. Verify installation:
```cmd
python --version
```
Should show: `Python 3.11.x` or `Python 3.12.x` or `Python 3.13.x`

### 2. Microsoft C++ Build Tools (Optional but Recommended)

Some Python packages (like `greenlet`) may require compilation on Windows.

**Option A: Install Visual Studio Build Tools** (Recommended)
- Download from: https://visualstudio.microsoft.com/downloads/
- Select "Build Tools for Visual Studio"
- In installer, select: "Desktop development with C++"

**Option B: Skip if using binary wheels**
- Our `setup_windows.bat` uses `--prefer-binary` to avoid compilation
- This works for most users without Build Tools

## Quick Installation

### Method 1: Automated Setup (Recommended)

1. Open **Command Prompt** or **PowerShell** as Administrator
2. Navigate to project directory:
```cmd
cd path\to\auto-octo-easy
```

3. Run automated setup:
```cmd
setup_windows.bat
```

The script will:
- ✅ Check Python version
- ✅ Upgrade pip/setuptools/wheel
- ✅ Install all dependencies with binary wheels
- ✅ Create necessary directories

### Method 2: Manual Installation

If automated setup fails, follow these steps:

1. Upgrade pip:
```cmd
python -m pip install --upgrade pip setuptools wheel
```

2. Install dependencies:
```cmd
pip install -r requirements.txt --prefer-binary
```

3. Configure environment:
```cmd
copy .env.example .env
notepad .env
```

## Troubleshooting

### Problem 1: "greenlet" compilation error

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Solution A: Use binary wheel**
```cmd
fix_greenlet.bat
```

**Solution B: Install from pre-built wheel**
1. Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#greenlet
2. Download wheel for your Python version (e.g., `greenlet-xxx-cp311-win_amd64.whl`)
3. Install:
```cmd
pip install path\to\downloaded_wheel.whl
```

**Solution C: Install Build Tools** (see Prerequisites above)

### Problem 2: Import errors ("ModuleNotFoundError")

**Solution:**
```cmd
python fix_imports.py
```

This script automatically fixes import paths for Windows compatibility.

### Problem 3: PyQt6 deprecated warnings

**Solution:**
```cmd
python fix_pyqt6.py
```

This script removes deprecated PyQt6 API usage.

### Problem 4: "Python not found" or wrong version

**Check installed Python:**
```cmd
python --version
py --list
```

**If multiple Python versions installed:**
```cmd
REM Use specific version
py -3.11 -m pip install -r requirements.txt --prefer-binary
py -3.11 main.py
```

### Problem 5: Permission errors during installation

**Solution:** Run Command Prompt as Administrator
- Right-click Command Prompt
- Select "Run as administrator"
- Navigate to project and run setup again

### Problem 6: SSL/Certificate errors

**Solution:**
```cmd
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org --prefer-binary
```

## Running OctoMaster Pro

### First Run

1. **Configure environment:**
```cmd
notepad .env
```

Add your configuration:
```ini
# Octo Browser API
OCTO_API_TOKEN=your_api_token_here
OCTO_API_URL=https://app.octobrowser.net/api/v2/automation

# Application Settings
LOG_LEVEL=INFO
DEBUG=False

# AI Settings (optional)
OPENAI_API_KEY=your_openai_key_here
```

2. **Start application:**
```cmd
python main.py
```

### Normal Usage

After initial setup, simply run:
```cmd
python main.py
```

## Development Mode

### Install development dependencies:
```cmd
pip install -r requirements-dev.txt --prefer-binary
```

### Run with debug logging:
```cmd
set LOG_LEVEL=DEBUG
python main.py
```

### Run tests:
```cmd
pytest
```

## Creating Desktop Shortcut

1. Create new shortcut on Desktop
2. Target:
```
C:\Python311\python.exe "C:\path\to\auto-octo-easy\main.py"
```
3. Start in:
```
C:\path\to\auto-octo-easy
```
4. Icon: Choose Python icon or custom icon

## Performance Optimization for Windows

### 1. Disable Windows Defender real-time scanning for project folder
- Speeds up file operations
- Add project folder to exclusions

### 2. Use SSD for better performance
- Install on SSD if available
- Significant improvement for database operations

### 3. Increase virtual memory
- Control Panel → System → Advanced → Performance Settings
- Set custom size: Min 4GB, Max 8GB

## Common Windows-Specific Issues

### Path Length Limit

Windows has 260-character path limit (before Windows 10 version 1607).

**Enable long paths:**
1. Open Registry Editor (regedit)
2. Navigate to: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Set `LongPathsEnabled` to `1`
4. Restart computer

**Or use Git Bash with long path support**

### Antivirus Interference

Some antivirus software may block Python or dependencies.

**Solution:**
- Add Python and project folder to antivirus exclusions
- Temporarily disable during installation

### Firewall Blocking

Browser automation may be blocked by Windows Firewall.

**Solution:**
- Allow Python through Windows Firewall
- Add inbound/outbound rules for Python

## Uninstallation

To completely remove OctoMaster Pro:

1. **Uninstall Python packages:**
```cmd
pip uninstall -r requirements.txt -y
```

2. **Delete project folder:**
```cmd
rmdir /s /q C:\path\to\auto-octo-easy
```

3. **Remove Python (optional):**
- Control Panel → Programs → Uninstall Python

## Getting Help

### Check logs:
```cmd
type logs\octomaster_YYYY-MM-DD.log
```

### Test Python environment:
```cmd
python -c "import sys; print(f'Python {sys.version}')"
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import playwright; print('Playwright OK')"
```

### Community Support:
- GitHub Issues: https://github.com/yourusername/auto-octo-easy/issues
- Documentation: See README.md

## Advanced Configuration

### Custom Python Path

If Python is not in PATH:
```cmd
set PATH=C:\Python311;C:\Python311\Scripts;%PATH%
```

### Virtual Environment (Recommended for isolation)

```cmd
REM Create virtual environment
python -m venv venv

REM Activate
venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt --prefer-binary

REM Run app
python main.py

REM Deactivate when done
deactivate
```

### Running as Windows Service

Use `nssm` (Non-Sucking Service Manager):
1. Download from: https://nssm.cc/download
2. Install service:
```cmd
nssm install OctoMasterPro "C:\Python311\python.exe" "C:\path\to\auto-octo-easy\main.py"
nssm start OctoMasterPro
```

## Update Guide

To update to latest version:

```cmd
REM Pull latest changes
git pull

REM Update dependencies
pip install -r requirements.txt --upgrade --prefer-binary

REM Run fixes
python fix_imports.py
python fix_pyqt6.py
```

---

**Still having issues?** Please check the main [README.md](README.md) or create an issue on GitHub with:
- Your Windows version
- Python version (`python --version`)
- Full error message
- Contents of latest log file
