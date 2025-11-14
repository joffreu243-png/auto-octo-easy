#!/usr/bin/env python3
"""
Fix PyQt6 Compatibility Issues

This script automatically fixes deprecated PyQt6 API usage
for better compatibility across different PyQt6 versions.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


# Deprecated API patterns and their replacements
DEPRECATED_PATTERNS = [
    # AA_UseHighDpiPixmaps is deprecated (enabled by default in PyQt6)
    (
        r'app\.setAttribute\(Qt\.ApplicationAttribute\.AA_UseHighDpiPixmaps,\s*True\)',
        '# app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)  # Deprecated in PyQt6',
        'AA_UseHighDpiPixmaps (deprecated)'
    ),
    (
        r'QApplication\.setAttribute\(Qt\.ApplicationAttribute\.AA_UseHighDpiPixmaps,\s*True\)',
        '# QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)  # Deprecated in PyQt6',
        'AA_UseHighDpiPixmaps (deprecated)'
    ),

    # Qt.MidButton is deprecated, use Qt.MiddleButton
    (
        r'Qt\.MouseButton\.MidButton',
        'Qt.MouseButton.MiddleButton',
        'Qt.MidButton → Qt.MiddleButton'
    ),
    (
        r'Qt\.MidButton',
        'Qt.MouseButton.MiddleButton',
        'Qt.MidButton → Qt.MiddleButton'
    ),

    # QFont.Bold is deprecated, use QFont.Weight.Bold
    (
        r'QFont\.Bold',
        'QFont.Weight.Bold',
        'QFont.Bold → QFont.Weight.Bold'
    ),

    # exec_() is deprecated, use exec()
    (
        r'\.exec_\(\)',
        '.exec()',
        'exec_() → exec()'
    ),
]


def fix_file_pyqt6(file_path: Path) -> Tuple[bool, List[str]]:
    """Fix PyQt6 deprecated API usage in a file.

    Args:
        file_path: Path to Python file

    Returns:
        Tuple of (changed, list of fixes applied)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        fixes_applied = []

        for pattern, replacement, description in DEPRECATED_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes_applied.append(description)

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, fixes_applied

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []


def find_pyqt_files(root: Path) -> List[Path]:
    """Find all Python files that likely use PyQt6.

    Args:
        root: Project root directory

    Returns:
        List of Python file paths
    """
    python_files = []

    # Exclude certain directories
    exclude_dirs = {'.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache'}

    for py_file in root.rglob('*.py'):
        # Check if any parent is in exclude_dirs
        if any(part in exclude_dirs for part in py_file.parts):
            continue

        try:
            content = py_file.read_text(encoding='utf-8')
            # Check if file uses PyQt6
            if 'PyQt6' in content or 'from Qt' in content:
                python_files.append(py_file)
        except Exception:
            pass

    return python_files


def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - PyQt6 Compatibility Fixer")
    print("=" * 60)
    print()

    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    print()

    # Find all PyQt6 files
    pyqt_files = find_pyqt_files(project_root)
    print(f"Found {len(pyqt_files)} Python files using PyQt6")
    print()

    # Fix each file
    total_fixes = 0
    files_changed = 0

    for file_path in pyqt_files:
        changed, fixes = fix_file_pyqt6(file_path)

        if changed:
            files_changed += 1
            rel_path = file_path.relative_to(project_root)
            print(f"✓ Fixed {rel_path}")

            for fix in fixes:
                print(f"  - {fix}")
                total_fixes += 1

            print()

    print("=" * 60)
    print(f"Fixed {total_fixes} deprecated API usages in {files_changed} files")
    print("=" * 60)

    if files_changed > 0:
        print()
        print("PyQt6 compatibility issues fixed!")
        print()
        print("Changes made:")
        print("  - Removed deprecated AA_UseHighDpiPixmaps (enabled by default)")
        print("  - Updated deprecated Qt constants and methods")
        print("  - Replaced exec_() with exec()")
    else:
        print()
        print("No PyQt6 compatibility issues found. Everything looks good!")


if __name__ == "__main__":
    main()
