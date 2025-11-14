"""
Dialogs module for OctoMaster Pro.

Contains all dialog windows used in the application.
"""

from octomaster.gui.dialogs.plugins_dialog import PluginsDialog
from octomaster.gui.dialogs.templates_dialog import TemplatesDialog
from octomaster.gui.dialogs.octo_settings_dialog import OctoSettingsDialog
from octomaster.gui.dialogs.octo_export_dialog import OctoExportDialog
from octomaster.gui.dialogs.update_dialog import UpdateDialog

__all__ = [
    'PluginsDialog',
    'TemplatesDialog',
    'OctoSettingsDialog',
    'OctoExportDialog',
    'UpdateDialog',
]
