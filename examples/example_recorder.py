#!/usr/bin/env python3
"""
Example: Using the action recorder.

This example shows how to use the Recorder to capture actions and convert to workflow.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.automation.recorder import Recorder


def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - Recorder Example")
    print("=" * 60)

    # Create recorder
    recorder = Recorder()
    print("\nRecorder created")

    # Start recording
    recorder.start()
    print("Recording started...")

    # Simulate user actions
    print("\nSimulating user actions:")

    # Navigate to Google
    print("  1. Navigate to Google")
    recorder.record_navigation("https://google.com")

    # Type in search box
    print("  2. Type 'OctoMaster Pro'")
    recorder.record_type("input[name='q']", "OctoMaster Pro")

    # Click search button
    print("  3. Click search button")
    recorder.record_click("input[name='btnK']")

    # Wait a bit (simulated)
    import time

    time.sleep(0.5)

    # Click first result
    print("  4. Click first result")
    recorder.record_click("h3:first-of-type")

    # Stop recording
    recorder.stop()
    print("\nRecording stopped")

    # Get summary
    summary = recorder.get_summary()
    print("\nRecording Summary:")
    print(f"  Total actions: {summary['total_actions']}")
    print(f"  Action types: {summary['action_types']}")

    # Print recorded actions
    print("\nRecorded Actions:")
    for i, action in enumerate(recorder.recorded_actions, 1):
        print(f"  {i}. {action}")

    # Convert to workflow
    workflow = recorder.to_workflow(name="Recorded Google Search")
    print(f"\nGenerated workflow: {workflow.name}")
    print(f"  Blocks: {len(workflow.blocks)}")
    print(f"  Connections: {len(workflow.connections)}")

    # Save workflow
    output_path = Path(__file__).parent / "recorded_workflow.workflow"
    workflow.save(output_path)
    print(f"\nWorkflow saved to: {output_path}")

    # Export as Python
    code = workflow.export_to_python()
    code_path = Path(__file__).parent / "recorded_workflow.py"
    with open(code_path, "w") as f:
        f.write(code)
    print(f"Python code exported to: {code_path}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
