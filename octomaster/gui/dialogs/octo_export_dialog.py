"""
Octo Export Dialog.

Dialog for exporting workflow as Python script with Octo Browser integration.
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QCheckBox,
    QTextEdit,
    QLineEdit,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from loguru import logger
import asyncio
from pathlib import Path

from octomaster.integrations.octo.api_client import OctoAPIClient, OctoProfile
from octomaster.core.workflow import Workflow


class OctoExportDialog(QDialog):
    """Dialog for exporting workflow with Octo Browser integration."""

    export_completed = pyqtSignal(str)  # Emits file path when export completes

    def __init__(self, workflow: Workflow, octo_settings: dict, parent=None):
        super().__init__(parent)
        self.workflow = workflow
        self.octo_settings = octo_settings
        self.profiles = []
        self.selected_profile = None

        self.setWindowTitle("Export to Python with Octo Browser")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.setup_ui()
        self.load_profiles()

    def setup_ui(self):
        """Setup dialog UI."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("<h2>📤 Export to Python with Octo Browser</h2>")
        layout.addWidget(header)

        # Profile selection
        profile_group = QGroupBox("Octo Browser Profile")
        profile_layout = QFormLayout()

        self.profile_combo = QComboBox()
        self.profile_combo.currentIndexChanged.connect(self.on_profile_selected)
        profile_layout.addRow("Profile:", self.profile_combo)

        self.refresh_btn = QPushButton("🔄 Refresh Profiles")
        self.refresh_btn.clicked.connect(self.load_profiles)
        profile_layout.addRow("", self.refresh_btn)

        # Profile info
        self.profile_info_label = QLabel("Select a profile to see details")
        self.profile_info_label.setWordWrap(True)
        self.profile_info_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        profile_layout.addRow("Info:", self.profile_info_label)

        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QFormLayout()

        # Script type
        self.script_type_combo = QComboBox()
        self.script_type_combo.addItems([
            "Playwright (async)",
            "Playwright (sync)",
            "Selenium",
        ])
        options_layout.addRow("Script Type:", self.script_type_combo)

        # Headless mode
        self.headless_check = QCheckBox()
        self.headless_check.setChecked(False)
        options_layout.addRow("Headless Mode:", self.headless_check)

        # Include comments
        self.comments_check = QCheckBox()
        self.comments_check.setChecked(True)
        options_layout.addRow("Include Comments:", self.comments_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Script preview
        preview_label = QLabel("<b>Script Preview:</b>")
        layout.addWidget(preview_label)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(200)
        self.preview_text.setStyleSheet("font-family: 'Courier New', monospace; font-size: 10pt;")
        layout.addWidget(self.preview_text)

        # Generate button
        generate_btn = QPushButton("🔨 Generate Preview")
        generate_btn.clicked.connect(self.generate_preview)
        layout.addWidget(generate_btn)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        export_btn = QPushButton("💾 Export Script")
        export_btn.clicked.connect(self.export_script)
        button_layout.addWidget(export_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_profiles(self):
        """Load profiles from Octo Browser."""
        if not self.octo_settings.get('api_token'):
            QMessageBox.warning(
                self,
                "No API Token",
                "Please configure Octo Browser API settings first.\n\n"
                "Go to Tools → Settings → Octo Browser"
            )
            return

        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Loading...")
        self.profile_combo.clear()
        self.profile_combo.addItem("Loading profiles...", None)

        # Run async load
        asyncio.create_task(self._load_profiles_async())

    async def _load_profiles_async(self):
        """Async profile loading."""
        try:
            client = OctoAPIClient(
                api_token=self.octo_settings['api_token'],
                base_url=self.octo_settings.get('api_url', 'http://localhost:58888')
            )

            profiles = await client.list_profiles()
            self.profiles = profiles

            # Update combo box
            self.profile_combo.clear()

            if not profiles:
                self.profile_combo.addItem("No profiles found", None)
            else:
                for profile in profiles:
                    # Show profile title with tags
                    tags_str = ", ".join(profile.tags) if profile.tags else "No tags"
                    display_name = f"{profile.title} ({tags_str})"
                    self.profile_combo.addItem(display_name, profile)

            await client.close()

            logger.info(f"Loaded {len(profiles)} Octo profiles")

        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            self.profile_combo.clear()
            self.profile_combo.addItem(f"Error: {str(e)}", None)

            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load profiles:\n\n{str(e)}\n\n"
                "Make sure Octo Browser is running."
            )

        finally:
            self.refresh_btn.setEnabled(True)
            self.refresh_btn.setText("🔄 Refresh Profiles")

    def on_profile_selected(self, index: int):
        """Handle profile selection."""
        profile = self.profile_combo.currentData()
        self.selected_profile = profile

        if profile:
            # Show profile info
            proxy_info = "No proxy"
            if profile.proxy:
                proxy_type = profile.proxy.get('type', 'Unknown')
                proxy_host = profile.proxy.get('host', '')
                proxy_info = f"{proxy_type}: {proxy_host}"

            tags_info = ", ".join(profile.tags) if profile.tags else "No tags"

            info_text = f"""
<b>UUID:</b> {profile.uuid}<br>
<b>Tags:</b> {tags_info}<br>
<b>Proxy:</b> {proxy_info}
            """.strip()

            self.profile_info_label.setText(info_text)
        else:
            self.profile_info_label.setText("No profile selected")

    def generate_preview(self):
        """Generate script preview."""
        if not self.selected_profile:
            QMessageBox.warning(self, "No Profile", "Please select an Octo Browser profile first.")
            return

        script_code = self._generate_script()
        self.preview_text.setPlainText(script_code)

    def _generate_script(self) -> str:
        """Generate Python script code with Octo integration.

        Returns:
            Python script as string
        """
        profile = self.selected_profile
        script_type = self.script_type_combo.currentText()
        headless = self.headless_check.isChecked()
        include_comments = self.comments_check.isChecked()

        lines = []

        # Header
        if include_comments:
            lines.append(f"# Generated by OctoMaster Pro")
            lines.append(f"# Workflow: {self.workflow.name}")
            lines.append(f"# Octo Profile: {profile.title}")
            lines.append("")

        # Determine script type
        if "Playwright" in script_type:
            async_mode = "async" in script_type
            lines.extend(self._generate_playwright_script(profile, headless, async_mode, include_comments))
        elif "Selenium" in script_type:
            lines.extend(self._generate_selenium_script(profile, headless, include_comments))

        return "\n".join(lines)

    def _generate_playwright_script(self, profile: OctoProfile, headless: bool, async_mode: bool, comments: bool) -> list:
        """Generate Playwright script."""
        lines = []

        # Imports
        lines.append("import asyncio")
        lines.append("import httpx")
        if async_mode:
            lines.append("from playwright.async_api import async_playwright")
        else:
            lines.append("from playwright.sync_api import sync_playwright")
        lines.append("")

        # Constants
        lines.append(f"OCTO_API_TOKEN = '{self.octo_settings['api_token']}'")
        lines.append(f"OCTO_API_URL = '{self.octo_settings.get('api_url', 'http://localhost:58888')}'")
        lines.append(f"PROFILE_UUID = '{profile.uuid}'")
        lines.append("")

        if async_mode:
            # Async version
            lines.append("async def start_octo_profile():")
            if comments:
                lines.append("    \"\"\"Start Octo Browser profile and return WebSocket endpoint.\"\"\"")
            lines.append("    async with httpx.AsyncClient() as client:")
            lines.append("        response = await client.post(")
            lines.append(f"            f'{{OCTO_API_URL}}/api/profiles/start',")
            lines.append("            headers={'X-Octo-Api-Token': OCTO_API_TOKEN},")
            lines.append(f"            json={{'uuid': PROFILE_UUID, 'headless': {headless}}}")
            lines.append("        )")
            lines.append("        data = response.json()['data']")
            lines.append("        return data['ws_endpoint']")
            lines.append("")

            lines.append("async def main():")
            if comments:
                lines.append("    \"\"\"Main workflow execution.\"\"\"")
            lines.append("    # Start Octo profile")
            lines.append("    ws_endpoint = await start_octo_profile()")
            lines.append("    print(f'Connected to Octo profile: {ws_endpoint}')")
            lines.append("")
            lines.append("    # Connect Playwright to Octo Browser")
            lines.append("    async with async_playwright() as p:")
            lines.append("        browser = await p.chromium.connect_over_cdp(ws_endpoint)")
            lines.append("        context = browser.contexts[0]")
            lines.append("        page = context.pages[0]")
            lines.append("")

            # Add workflow blocks
            if comments:
                lines.append("        # Execute workflow blocks")
            for block in self.workflow.blocks:
                lines.extend(self._generate_block_code(block, "        ", async_mode=True))

            lines.append("")
            if comments:
                lines.append("        # Keep browser open for inspection")
            lines.append("        await page.wait_for_timeout(5000)")
            lines.append("        await browser.close()")
            lines.append("")

            lines.append("if __name__ == '__main__':")
            lines.append("    asyncio.run(main())")
        else:
            # Sync version
            lines.append("def start_octo_profile():")
            if comments:
                lines.append("    \"\"\"Start Octo Browser profile and return WebSocket endpoint.\"\"\"")
            lines.append("    with httpx.Client() as client:")
            lines.append("        response = client.post(")
            lines.append(f"            f'{{OCTO_API_URL}}/api/profiles/start',")
            lines.append("            headers={'X-Octo-Api-Token': OCTO_API_TOKEN},")
            lines.append(f"            json={{'uuid': PROFILE_UUID, 'headless': {headless}}}")
            lines.append("        )")
            lines.append("        data = response.json()['data']")
            lines.append("        return data['ws_endpoint']")
            lines.append("")

            lines.append("def main():")
            if comments:
                lines.append("    \"\"\"Main workflow execution.\"\"\"")
            lines.append("    # Start Octo profile")
            lines.append("    ws_endpoint = start_octo_profile()")
            lines.append("    print(f'Connected to Octo profile: {ws_endpoint}')")
            lines.append("")
            lines.append("    # Connect Playwright to Octo Browser")
            lines.append("    with sync_playwright() as p:")
            lines.append("        browser = p.chromium.connect_over_cdp(ws_endpoint)")
            lines.append("        context = browser.contexts[0]")
            lines.append("        page = context.pages[0]")
            lines.append("")

            # Add workflow blocks
            if comments:
                lines.append("        # Execute workflow blocks")
            for block in self.workflow.blocks:
                lines.extend(self._generate_block_code(block, "        ", async_mode=False))

            lines.append("")
            lines.append("        browser.close()")
            lines.append("")

            lines.append("if __name__ == '__main__':")
            lines.append("    main()")

        return lines

    def _generate_selenium_script(self, profile: OctoProfile, headless: bool, comments: bool) -> list:
        """Generate Selenium script."""
        lines = []

        # Imports
        lines.append("import httpx")
        lines.append("from selenium import webdriver")
        lines.append("from selenium.webdriver.chrome.options import Options")
        lines.append("from selenium.webdriver.common.by import By")
        lines.append("import time")
        lines.append("")

        # Constants
        lines.append(f"OCTO_API_TOKEN = '{self.octo_settings['api_token']}'")
        lines.append(f"OCTO_API_URL = '{self.octo_settings.get('api_url', 'http://localhost:58888')}'")
        lines.append(f"PROFILE_UUID = '{profile.uuid}'")
        lines.append("")

        lines.append("def start_octo_profile():")
        if comments:
            lines.append("    \"\"\"Start Octo Browser profile and return debug port.\"\"\"")
        lines.append("    with httpx.Client() as client:")
        lines.append("        response = client.post(")
        lines.append(f"            f'{{OCTO_API_URL}}/api/profiles/start',")
        lines.append("            headers={'X-Octo-Api-Token': OCTO_API_TOKEN},")
        lines.append(f"            json={{'uuid': PROFILE_UUID, 'headless': {headless}}}")
        lines.append("        )")
        lines.append("        data = response.json()['data']")
        lines.append("        return data['debug_port']")
        lines.append("")

        lines.append("def main():")
        if comments:
            lines.append("    \"\"\"Main workflow execution.\"\"\"")
        lines.append("    # Start Octo profile")
        lines.append("    debug_port = start_octo_profile()")
        lines.append("    print(f'Octo profile started on port: {debug_port}')")
        lines.append("")

        lines.append("    # Connect Selenium to Octo Browser")
        lines.append("    options = Options()")
        lines.append("    options.add_experimental_option('debuggerAddress', f'127.0.0.1:{debug_port}')")
        lines.append("")

        lines.append("    driver = webdriver.Chrome(options=options)")
        lines.append("")

        # Add workflow blocks
        if comments:
            lines.append("    # Execute workflow blocks")
        for block in self.workflow.blocks:
            lines.extend(self._generate_block_code(block, "    ", async_mode=False, selenium=True))

        lines.append("")
        lines.append("    # Keep browser open")
        lines.append("    time.sleep(5)")
        lines.append("    driver.quit()")
        lines.append("")

        lines.append("if __name__ == '__main__':")
        lines.append("    main()")

        return lines

    def _generate_block_code(self, block, indent: str, async_mode: bool = False, selenium: bool = False) -> list:
        """Generate code for a single block."""
        lines = []
        await_str = "await " if async_mode else ""

        # Get block parameters
        selector = block.parameters.get('selector', '')
        text = block.parameters.get('text', '')
        url = block.parameters.get('url', '')

        block_type = str(block.type.value) if hasattr(block.type, 'value') else str(block.type)

        if selenium:
            # Selenium code generation
            if block_type == 'OPEN_URL' or 'url' in block.parameters:
                lines.append(f"{indent}driver.get('{url}')")
            elif block_type == 'CLICK' and selector:
                lines.append(f"{indent}driver.find_element(By.CSS_SELECTOR, '{selector}').click()")
            elif block_type == 'TYPE_TEXT' and selector and text:
                lines.append(f"{indent}driver.find_element(By.CSS_SELECTOR, '{selector}').send_keys('{text}')")
            elif block_type == 'WAIT':
                lines.append(f"{indent}time.sleep(2)")
        else:
            # Playwright code generation
            if block_type == 'OPEN_URL' or 'url' in block.parameters:
                lines.append(f"{indent}{await_str}page.goto('{url}')")
            elif block_type == 'CLICK' and selector:
                lines.append(f"{indent}{await_str}page.click('{selector}')")
            elif block_type == 'TYPE_TEXT' and selector and text:
                lines.append(f"{indent}{await_str}page.fill('{selector}', '{text}')")
            elif block_type == 'WAIT':
                lines.append(f"{indent}{await_str}page.wait_for_timeout(2000)")

        return lines

    def export_script(self):
        """Export script to file."""
        if not self.selected_profile:
            QMessageBox.warning(self, "No Profile", "Please select an Octo Browser profile first.")
            return

        # Get save file path
        default_name = f"{self.workflow.name.replace(' ', '_')}_octo.py"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Python Script",
            default_name,
            "Python Files (*.py);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Generate script
            script_code = self._generate_script()

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(script_code)

            logger.info(f"Exported script to: {file_path}")

            QMessageBox.information(
                self,
                "Export Successful",
                f"✅ Script exported successfully!\n\n"
                f"File: {file_path}\n\n"
                f"To run:\n"
                f"1. Make sure Octo Browser is running\n"
                f"2. Run: python {Path(file_path).name}"
            )

            self.export_completed.emit(file_path)
            self.accept()

        except Exception as e:
            logger.error(f"Export failed: {e}")
            QMessageBox.critical(
                self,
                "Export Error",
                f"❌ Failed to export script:\n\n{str(e)}"
            )
