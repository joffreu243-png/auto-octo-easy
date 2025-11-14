"""Project export and import for OctoMaster Pro."""

from typing import Dict, Any
from pathlib import Path
import json
import zipfile
from datetime import datetime
from loguru import logger


class ProjectExporter:
    """Export complete OctoMaster Pro projects."""

    def export(self, project: Dict[str, Any], output_path: Path) -> bool:
        """Export project to ZIP file.

        Args:
            project: Project data
            output_path: Output ZIP path

        Returns:
            True if successful
        """
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Export project metadata
                metadata = {
                    "name": project.get("name", "Untitled Project"),
                    "version": "1.0",
                    "exported_at": datetime.now().isoformat(),
                    "octomaster_version": "1.0.0",
                }
                zipf.writestr("project.json", json.dumps(metadata, indent=2))

                # Export workflows
                if "workflows" in project:
                    for i, workflow in enumerate(project["workflows"]):
                        zipf.writestr(f"workflows/workflow_{i}.json", json.dumps(workflow, indent=2))

                # Export templates
                if "templates" in project:
                    for i, template in enumerate(project["templates"]):
                        zipf.writestr(f"templates/template_{i}.json", json.dumps(template, indent=2))

                # Export configurations
                if "config" in project:
                    zipf.writestr("config.json", json.dumps(project["config"], indent=2))

            logger.info(f"Exported project to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export project: {e}")
            return False


class ProjectImporter:
    """Import OctoMaster Pro projects."""

    def import_project(self, zip_path: Path) -> Dict[str, Any]:
        """Import project from ZIP file.

        Args:
            zip_path: ZIP file path

        Returns:
            Project data
        """
        try:
            project = {}

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Read metadata
                if "project.json" in zipf.namelist():
                    project["metadata"] = json.loads(zipf.read("project.json"))

                # Read workflows
                project["workflows"] = []
                for name in zipf.namelist():
                    if name.startswith("workflows/"):
                        workflow = json.loads(zipf.read(name))
                        project["workflows"].append(workflow)

                # Read templates
                project["templates"] = []
                for name in zipf.namelist():
                    if name.startswith("templates/"):
                        template = json.loads(zipf.read(name))
                        project["templates"].append(template)

                # Read config
                if "config.json" in zipf.namelist():
                    project["config"] = json.loads(zipf.read("config.json"))

            logger.info(f"Imported project from {zip_path}")
            return project

        except Exception as e:
            logger.error(f"Failed to import project: {e}")
            return {}
