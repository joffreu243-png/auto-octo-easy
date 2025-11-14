"""
Setup script for OctoMaster Pro.

This file exists for backwards compatibility with pip install -e .
For development, prefer using Poetry: poetry install
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements from pyproject.toml or fall back to requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
else:
    # Minimal requirements if file doesn't exist
    requirements = [
        "PyQt6>=6.6.0",
        "playwright>=1.40.0",
        "selenium>=4.16.0",
        "loguru>=0.7.2",
        "pydantic>=2.5.2",
        "sqlalchemy>=2.0.23",
        "httpx>=0.25.2",
    ]

setup(
    name="octomaster-pro",
    version="1.0.0-alpha",
    description="Advanced browser automation platform with visual workflow builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OctoMaster Team",
    author_email="support@octomaster.pro",
    url="https://github.com/octomaster/octomaster-pro",
    project_urls={
        "Documentation": "https://docs.octomaster.pro",
        "Source": "https://github.com/octomaster/octomaster-pro",
        "Bug Tracker": "https://github.com/octomaster/octomaster-pro/issues",
    },
    packages=find_packages(where=".", include=["src*", "octomaster*"]),
    package_dir={"": "."},
    python_requires=">=3.11",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-qt>=4.2.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0",
            "mypy>=1.7.1",
            "ruff>=0.1.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "octomaster=src.core.app:main",
            "octomaster-cli=src.cli.main:cli_main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Testing",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Environment :: X11 Applications :: Qt",
    ],
    keywords="automation browser playwright selenium workflow visual-editor ai",
    license="MIT",
    include_package_data=True,
    zip_safe=False,
)
