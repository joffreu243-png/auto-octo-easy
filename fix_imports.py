#!/usr/bin/env python3
"""
Fix Import Issues for Windows Compatibility

This script automatically fixes import issues in OctoMaster Pro
by ensuring proper path setup and fallback imports.
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple


def fix_file_imports(file_path: Path) -> Tuple[bool, str]:
    """Fix imports in a single file.

    Args:
        file_path: Path to Python file

    Returns:
        Tuple of (changed, message)
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Pattern 1: Fix "from src.module" imports to have fallback
        pattern1 = r'^(\s*)from src\.([^\s]+) import (.+)$'

        def replace_import(match):
            indent = match.group(1)
            module = match.group(2)
            imports = match.group(3)

            return f"""{indent}try:
{indent}    from {module} import {imports}
{indent}except ImportError:
{indent}    from src.{module} import {imports}"""

        content = re.sub(pattern1, replace_import, content, flags=re.MULTILINE)

        # Add sys.path setup at the beginning if not present
        if 'sys.path.insert' not in content and 'from src.' in content:
            header = '''import sys
from pathlib import Path

# Add project root to path for Windows compatibility
project_root = Path(__file__).parent
while not (project_root / "src").exists() and project_root.parent != project_root:
    project_root = project_root.parent

src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

'''
            # Find the first import line
            import_match = re.search(r'^(import |from )', content, re.MULTILINE)
            if import_match:
                insert_pos = import_match.start()
                content = content[:insert_pos] + header + content[insert_pos:]

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, f"Fixed imports in {file_path.relative_to(Path.cwd())}"

        return False, f"No changes needed in {file_path.relative_to(Path.cwd())}"

    except Exception as e:
        return False, f"Error processing {file_path}: {e}"


def find_python_files(root: Path) -> List[Path]:
    """Find all Python files in project.

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
        if not any(part in exclude_dirs for part in py_file.parts):
            python_files.append(py_file)

    return python_files


def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - Import Fixer")
    print("=" * 60)
    print()

    project_root = Path.cwd()
    print(f"Project root: {project_root}")
    print()

    # Find all Python files
    python_files = find_python_files(project_root)
    print(f"Found {len(python_files)} Python files")
    print()

    # Fix each file
    fixed_count = 0
    for file_path in python_files:
        changed, message = fix_file_imports(file_path)
        if changed:
            print(f"✓ {message}")
            fixed_count += 1

    print()
    print("=" * 60)
    print(f"Fixed {fixed_count} files")
    print("=" * 60)

    if fixed_count > 0:
        print()
        print("Import issues fixed! You can now run the application.")
    else:
        print()
        print("No import issues found. Everything looks good!")


if __name__ == "__main__":
    main()
