#!/usr/bin/env python3
"""
Example: Using the Plugin System.

This example shows how to discover, load, and manage plugins.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.core.plugins.manager import PluginManager
from octomaster.core.plugins.plugin import PluginType


def main():
    """Main function."""
    print("=" * 60)
    print("OctoMaster Pro - Plugin System Example")
    print("=" * 60)

    # Create plugin manager
    plugins_dir = Path(__file__).parent.parent / "plugins"
    manager = PluginManager(plugins_dir=plugins_dir)

    print(f"\nPlugins directory: {plugins_dir}")

    # Discover plugins
    print("\n" + "-" * 60)
    print("Discovering plugins...")
    print("-" * 60)

    plugin_ids = manager.discover_plugins()
    print(f"\nFound {len(plugin_ids)} plugins:")
    for plugin_id in plugin_ids:
        print(f"  • {plugin_id}")

    # Load all plugins
    print("\n" + "-" * 60)
    print("Loading plugins...")
    print("-" * 60)

    loaded_count = manager.load_all_plugins()
    print(f"\nSuccessfully loaded {loaded_count} plugins")

    # List loaded plugins
    print("\n" + "-" * 60)
    print("Loaded Plugins:")
    print("-" * 60)

    for plugin_info in manager.list_plugins():
        status = "✓" if plugin_info["active"] else "✗"
        print(f"\n{status} {plugin_info['name']} v{plugin_info['version']}")
        print(f"  ID: {plugin_info['id']}")
        print(f"  Type: {plugin_info['type']}")
        print(f"  Author: {plugin_info['author']}")
        print(f"  Active: {plugin_info['active']}")

    # Get plugin statistics
    print("\n" + "-" * 60)
    print("Plugin Statistics:")
    print("-" * 60)

    stats = manager.get_stats()
    print(f"\nTotal plugins: {stats['total']}")
    print(f"Active: {stats['active']}")
    print(f"Inactive: {stats['inactive']}")
    print()
    print("By type:")
    for plugin_type in PluginType:
        count = stats.get(f"type_{plugin_type.value}", 0)
        if count > 0:
            print(f"  {plugin_type.value}: {count}")

    # Work with specific plugins
    print("\n" + "-" * 60)
    print("Working with Block Plugin:")
    print("-" * 60)

    block_plugins = manager.get_plugins_by_type(PluginType.BLOCK)
    if block_plugins:
        plugin = block_plugins[0]
        print(f"\nPlugin: {plugin.metadata.name}")
        print(f"Description: {plugin.metadata.description}")

        # Get custom block types
        block_types = plugin.get_block_types()
        print(f"\nProvides {len(block_types)} custom block types:")
        for block_class in block_types:
            block = block_class()
            print(f"  • {block.name} - {block.description}")

        # Get categories
        categories = plugin.get_block_categories()
        print(f"\nCategories:")
        for category, blocks in categories.items():
            print(f"  {category}:")
            for block_id in blocks:
                print(f"    - {block_id}")

    # Work with theme plugin
    print("\n" + "-" * 60)
    print("Working with Theme Plugin:")
    print("-" * 60)

    theme_plugins = manager.get_plugins_by_type(PluginType.THEME)
    if theme_plugins:
        plugin = theme_plugins[0]
        print(f"\nPlugin: {plugin.metadata.name}")
        print(f"Description: {plugin.metadata.description}")

        # Get colors
        colors = plugin.get_colors()
        print(f"\nProvides {len(colors)} colors:")
        for color_name, color_value in list(colors.items())[:5]:
            print(f"  • {color_name}: {color_value}")
        print("  ...")

    # Disable and re-enable a plugin
    print("\n" + "-" * 60)
    print("Testing Plugin Enable/Disable:")
    print("-" * 60)

    if plugin_ids:
        test_plugin_id = plugin_ids[0]
        print(f"\nDisabling plugin: {test_plugin_id}")
        if manager.disable_plugin(test_plugin_id):
            print("  ✓ Plugin disabled")

        plugin = manager.get_plugin(test_plugin_id)
        print(f"  Active: {plugin.is_active}")

        print(f"\nRe-enabling plugin: {test_plugin_id}")
        if manager.enable_plugin(test_plugin_id):
            print("  ✓ Plugin enabled")

        print(f"  Active: {plugin.is_active}")

    # Cleanup
    print("\n" + "-" * 60)
    print("Cleanup:")
    print("-" * 60)

    manager.unload_all_plugins()
    print("\n✓ All plugins unloaded")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
