#!/usr/bin/env python3
"""
OctoMaster Pro - Command Line Interface.

Provides CLI commands for working with workflows, templates, and automation.
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional

import click
from loguru import logger

from octomaster.core.workflow import Workflow
from octomaster.core.templates import TemplateManager
from octomaster.automation.executor import WorkflowExecutor
from octomaster.core.config import Config


# Configure logger for CLI
logger.remove()
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <level>{message}</level>",
    level="INFO",
)


@click.group()
@click.version_option(version="0.1.0-alpha", prog_name="OctoMaster Pro")
def cli():
    """
    OctoMaster Pro - Browser Automation Platform

    Visual workflow builder for browser automation with AI assistance.
    """
    pass


# ========== Workflow Commands ==========


@cli.group()
def workflow():
    """Manage workflows."""
    pass


@workflow.command("list")
@click.option("--dir", "-d", default="projects", help="Projects directory")
def list_workflows(dir: str):
    """List all workflows."""
    projects_dir = Path(dir)

    if not projects_dir.exists():
        click.echo(f"Directory not found: {projects_dir}")
        return

    workflow_files = list(projects_dir.glob("**/*.workflow"))

    if not workflow_files:
        click.echo("No workflows found")
        return

    click.echo(f"\nFound {len(workflow_files)} workflows:\n")

    for file_path in workflow_files:
        try:
            wf = Workflow.load(file_path)
            click.echo(f"  • {wf.name}")
            click.echo(f"    Path: {file_path}")
            click.echo(f"    Blocks: {len(wf.blocks)}")
            click.echo()
        except Exception as e:
            click.echo(f"  ✗ {file_path}: Error loading - {e}\n")


@workflow.command("run")
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--headless/--no-headless", default=False, help="Run in headless mode")
@click.option("--browser", default="chromium", help="Browser to use (chromium/firefox/webkit)")
def run_workflow(workflow_file: str, headless: bool, browser: str):
    """Execute a workflow."""
    click.echo(f"\n🚀 Running workflow: {workflow_file}\n")

    async def run():
        try:
            # Load workflow
            wf = Workflow.load(Path(workflow_file))
            click.echo(f"Loaded workflow: {wf.name}")
            click.echo(f"Blocks: {len(wf.blocks)}")
            click.echo(f"Connections: {len(wf.connections)}")
            click.echo()

            # Validate
            is_valid, errors = wf.validate()
            if not is_valid:
                click.echo("❌ Validation failed:")
                for error in errors:
                    click.echo(f"  • {error}")
                return

            # Execute
            executor = WorkflowExecutor(wf)
            success = await executor.execute(headless=headless)

            # Results
            stats = executor.get_stats()
            click.echo("\n" + "=" * 60)
            if success:
                click.echo("✅ Workflow completed successfully!")
            else:
                click.echo("❌ Workflow failed!")

            click.echo(f"\nStats:")
            click.echo(f"  Duration: {stats['duration']:.2f}s")
            click.echo(f"  Total blocks: {stats['total_blocks']}")
            click.echo(f"  Successful: {stats['successful']}")
            click.echo(f"  Failed: {stats['failed']}")
            click.echo("=" * 60)

        except Exception as e:
            click.echo(f"❌ Error: {e}")
            logger.exception("Workflow execution failed")

    asyncio.run(run())


@workflow.command("export")
@click.argument("workflow_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--format", default="python", type=click.Choice(["python", "json"]))
def export_workflow(workflow_file: str, output_file: str, format: str):
    """Export workflow to Python code or JSON."""
    try:
        wf = Workflow.load(Path(workflow_file))

        if format == "python":
            code = wf.export_to_python()
            with open(output_file, "w") as f:
                f.write(code)
        elif format == "json":
            wf.save(Path(output_file))

        click.echo(f"✅ Exported to: {output_file}")

    except Exception as e:
        click.echo(f"❌ Error: {e}")


# ========== Template Commands ==========


@cli.group()
def template():
    """Manage templates."""
    pass


@template.command("list")
@click.option("--category", "-c", help="Filter by category")
@click.option("--search", "-s", help="Search templates")
def list_templates(category: Optional[str], search: Optional[str]):
    """List available templates."""
    manager = TemplateManager()

    templates = manager.search(query=search, category=category)

    if not templates:
        click.echo("No templates found")
        return

    click.echo(f"\nFound {len(templates)} templates:\n")

    for tpl in templates:
        click.echo(f"  {tpl.icon} {tpl.name}")
        click.echo(f"    Category: {tpl.category} | Difficulty: {tpl.difficulty}")
        click.echo(f"    {tpl.description}")
        click.echo()


@template.command("info")
@click.argument("template_id")
def template_info(template_id: str):
    """Show detailed template information."""
    manager = TemplateManager()
    tpl = manager.get_template(template_id)

    if not tpl:
        click.echo(f"Template not found: {template_id}")
        return

    click.echo(f"\n{tpl.icon} {tpl.name}")
    click.echo("=" * 60)
    click.echo(f"ID: {tpl.id}")
    click.echo(f"Category: {tpl.category}")
    click.echo(f"Difficulty: {tpl.difficulty}")
    click.echo(f"Author: {tpl.author}")
    click.echo(f"Version: {tpl.version}")
    click.echo(f"Tags: {', '.join(tpl.tags)}")
    click.echo(f"\nDescription:\n{tpl.description}")

    if tpl.inputs:
        click.echo(f"\nInputs:")
        for inp in tpl.inputs:
            required = " (required)" if inp.required else ""
            click.echo(f"  • {inp.label}{required}")
            click.echo(f"    Type: {inp.type}")
            click.echo(f"    Description: {inp.description}")
            if inp.default is not None:
                click.echo(f"    Default: {inp.default}")
            click.echo()


@template.command("use")
@click.argument("template_id")
@click.option("--output", "-o", help="Output workflow file")
def use_template(template_id: str, output: Optional[str]):
    """Create a workflow from a template."""
    manager = TemplateManager()
    tpl = manager.get_template(template_id)

    if not tpl:
        click.echo(f"Template not found: {template_id}")
        return

    click.echo(f"\nUsing template: {tpl.name}\n")

    # Collect input parameters
    params = {}
    for inp in tpl.inputs:
        prompt = f"{inp.label}"
        if inp.description:
            prompt += f" ({inp.description})"
        if inp.default is not None:
            prompt += f" [{inp.default}]"

        value = click.prompt(prompt, default=inp.default or "", type=str)
        params[inp.name] = value

    # Validate
    is_valid, errors = tpl.validate_parameters(params)
    if not is_valid:
        click.echo("\n❌ Validation errors:")
        for error in errors:
            click.echo(f"  • {error}")
        return

    # Instantiate
    try:
        workflow = tpl.instantiate(params)

        # Save
        if not output:
            output = f"{tpl.id}_workflow.workflow"

        workflow.save(Path(output))

        click.echo(f"\n✅ Workflow created: {output}")
        click.echo(f"Blocks: {len(workflow.blocks)}")

    except Exception as e:
        click.echo(f"\n❌ Error: {e}")


# ========== GUI Command ==========


@cli.command()
def gui():
    """Launch the GUI application."""
    click.echo("Launching OctoMaster Pro GUI...")

    # Import here to avoid loading Qt if not needed
    from PyQt6.QtWidgets import QApplication
    from octomaster.gui.main_window import MainWindow
    from octomaster.core.config import Config

    app = QApplication(sys.argv)
    config = Config()
    window = MainWindow(config)
    window.show()

    sys.exit(app.exec())


# ========== Info Commands ==========


@cli.command()
def version():
    """Show version information."""
    click.echo("OctoMaster Pro v0.1.0-alpha")
    click.echo("Browser automation platform with visual workflow builder")


@cli.command()
def info():
    """Show system information."""
    config = Config()

    click.echo("\nOctoMaster Pro - System Information")
    click.echo("=" * 60)
    click.echo(f"Version: {config.app_version}")
    click.echo(f"Environment: {config.app_env}")
    click.echo(f"Project Root: {config.project_root}")
    click.echo(f"Default Browser: {config.default_browser}")
    click.echo(f"Headless Mode: {config.headless}")

    # Template stats
    manager = TemplateManager()
    stats = manager.get_stats()

    click.echo(f"\nTemplates:")
    click.echo(f"  Total: {stats['total_templates']}")
    click.echo(f"  Categories: {stats['categories']}")

    click.echo()


def main():
    """Main CLI entry point."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        logger.exception("CLI error")
        sys.exit(1)


if __name__ == "__main__":
    main()
