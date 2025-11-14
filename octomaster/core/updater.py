"""
Auto-updater for OctoMaster Pro.

Checks for updates from Git repository and updates the application.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger
from dataclasses import dataclass


@dataclass
class UpdateInfo:
    """Information about available update."""

    has_updates: bool
    current_branch: str
    current_commit: str
    remote_commit: str
    commits_behind: int
    changelog: str


class AutoUpdater:
    """Auto-updater for OctoMaster Pro using Git."""

    def __init__(self, project_root: Path):
        """Initialize auto-updater.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.git_dir = project_root / ".git"

    def is_git_repo(self) -> bool:
        """Check if project is a Git repository.

        Returns:
            True if this is a Git repo
        """
        return self.git_dir.exists()

    def get_current_branch(self) -> Optional[str]:
        """Get current Git branch name.

        Returns:
            Branch name or None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except Exception as e:
            logger.error(f"Failed to get current branch: {e}")

        return None

    def get_current_commit(self) -> Optional[str]:
        """Get current commit hash.

        Returns:
            Commit hash or None
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except Exception as e:
            logger.error(f"Failed to get current commit: {e}")

        return None

    def fetch_updates(self) -> bool:
        """Fetch updates from remote repository.

        Returns:
            True if fetch successful
        """
        try:
            logger.info("Fetching updates from remote...")

            result = subprocess.run(
                ["git", "fetch", "origin"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                logger.info("Fetch completed successfully")
                return True
            else:
                logger.error(f"Fetch failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Fetch timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to fetch updates: {e}")
            return False

    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check if updates are available.

        Returns:
            UpdateInfo object or None if check failed
        """
        if not self.is_git_repo():
            logger.warning("Not a Git repository")
            return None

        # Get current state
        current_branch = self.get_current_branch()
        if not current_branch:
            return None

        current_commit = self.get_current_commit()
        if not current_commit:
            return None

        # Fetch updates
        if not self.fetch_updates():
            return None

        # Get remote commit
        try:
            result = subprocess.run(
                ["git", "rev-parse", f"origin/{current_branch}"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                logger.error(f"Failed to get remote commit: {result.stderr}")
                return None

            remote_commit = result.stdout.strip()

        except Exception as e:
            logger.error(f"Failed to get remote commit: {e}")
            return None

        # Check if behind
        has_updates = current_commit != remote_commit

        # Get number of commits behind
        commits_behind = 0
        changelog = ""

        if has_updates:
            try:
                # Count commits
                result = subprocess.run(
                    ["git", "rev-list", "--count", f"{current_commit}..{remote_commit}"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    commits_behind = int(result.stdout.strip())

                # Get changelog
                result = subprocess.run(
                    ["git", "log", "--oneline", f"{current_commit}..{remote_commit}"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    changelog = result.stdout.strip()

            except Exception as e:
                logger.error(f"Failed to get update details: {e}")

        return UpdateInfo(
            has_updates=has_updates,
            current_branch=current_branch,
            current_commit=current_commit[:7],  # Short hash
            remote_commit=remote_commit[:7],
            commits_behind=commits_behind,
            changelog=changelog
        )

    def has_local_changes(self) -> Tuple[bool, str]:
        """Check if there are uncommitted local changes.

        Returns:
            Tuple of (has_changes, status_output)
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                status = result.stdout.strip()
                has_changes = len(status) > 0
                return has_changes, status

        except Exception as e:
            logger.error(f"Failed to check local changes: {e}")

        return False, ""

    def stash_changes(self) -> bool:
        """Stash local changes.

        Returns:
            True if stash successful
        """
        try:
            logger.info("Stashing local changes...")

            result = subprocess.run(
                ["git", "stash", "push", "-m", "Auto-stash before update"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Local changes stashed")
                return True
            else:
                logger.error(f"Stash failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to stash changes: {e}")
            return False

    def apply_stash(self) -> bool:
        """Apply stashed changes.

        Returns:
            True if apply successful
        """
        try:
            logger.info("Applying stashed changes...")

            result = subprocess.run(
                ["git", "stash", "pop"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info("Stashed changes applied")
                return True
            else:
                logger.warning(f"Stash apply had conflicts: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to apply stash: {e}")
            return False

    def pull_updates(self) -> Tuple[bool, str]:
        """Pull updates from remote repository.

        Returns:
            Tuple of (success, output_message)
        """
        if not self.is_git_repo():
            return False, "Not a Git repository"

        current_branch = self.get_current_branch()
        if not current_branch:
            return False, "Could not determine current branch"

        # Check for local changes
        has_changes, status = self.has_local_changes()
        stashed = False

        if has_changes:
            logger.info(f"Local changes detected:\n{status}")

            # Stash changes
            if not self.stash_changes():
                return False, "Failed to stash local changes"

            stashed = True

        try:
            logger.info(f"Pulling updates from origin/{current_branch}...")

            # Pull updates
            result = subprocess.run(
                ["git", "pull", "origin", current_branch],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info("Pull completed successfully")
                output = result.stdout

                # Apply stashed changes if any
                if stashed:
                    if not self.apply_stash():
                        output += "\n\n⚠️ Warning: Could not automatically apply your local changes. They are stashed and can be applied manually with 'git stash pop'"

                return True, output
            else:
                logger.error(f"Pull failed: {result.stderr}")

                # Try to restore stash if pull failed
                if stashed:
                    self.apply_stash()

                return False, f"Update failed: {result.stderr}"

        except subprocess.TimeoutExpired:
            logger.error("Pull timed out")

            if stashed:
                self.apply_stash()

            return False, "Update timed out"

        except Exception as e:
            logger.error(f"Failed to pull updates: {e}")

            if stashed:
                self.apply_stash()

            return False, f"Update failed: {str(e)}"

    def install_dependencies(self) -> Tuple[bool, str]:
        """Install/update Python dependencies from requirements.txt.

        Returns:
            Tuple of (success, output_message)
        """
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            return True, "No requirements.txt found, skipping dependency installation"

        try:
            logger.info("Installing/updating dependencies...")

            # Use pip to install requirements
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--upgrade"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )

            if result.returncode == 0:
                logger.info("Dependencies installed successfully")
                return True, "Dependencies updated successfully"
            else:
                logger.error(f"Dependency installation failed: {result.stderr}")
                return False, f"Failed to install dependencies: {result.stderr}"

        except subprocess.TimeoutExpired:
            logger.error("Dependency installation timed out")
            return False, "Dependency installation timed out"

        except Exception as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False, f"Failed to install dependencies: {str(e)}"
