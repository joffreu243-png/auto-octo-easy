#!/usr/bin/env python3
"""
Example: Creating workflow templates.

This script creates several useful templates for common automation tasks.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType
from octomaster.core.templates import Template, TemplateInput, TemplateManager


def create_google_search_template():
    """Create Google search template."""

    # Create workflow
    workflow = Workflow(name="Google Search")

    # Open Google
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "https://google.com")
    workflow.add_block(open_url)

    # Type search query (with template variable)
    type_query = Block(type=BlockType.TYPE_TEXT)
    type_query.set_parameter("selector", "input[name='q']")
    type_query.set_parameter("text", "{{search_query}}")
    workflow.add_block(type_query)

    # Click search
    click_search = Block(type=BlockType.CLICK)
    click_search.set_parameter("selector", "input[name='btnK']")
    workflow.add_block(click_search)

    # Wait for results
    wait_results = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_results.set_parameter("selector", "#search")
    workflow.add_block(wait_results)

    # Screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "{{output_path}}")
    workflow.add_block(screenshot)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    # Create template
    template = Template(
        id="google-search",
        name="Google Search",
        description="Search Google and take a screenshot of results",
        category="scraping",
        difficulty="easy",
        author="OctoMaster Team",
        icon="🔍",
        tags=["google", "search", "screenshot"],
        inputs=[
            TemplateInput(
                name="search_query",
                label="Search Query",
                type="string",
                description="What to search for",
                default="Python programming",
                required=True,
            ),
            TemplateInput(
                name="output_path",
                label="Screenshot Path",
                type="string",
                description="Where to save the screenshot",
                default="google_results.png",
                required=False,
            ),
        ],
        outputs=["screenshot"],
        workflow=workflow,
    )

    return template


def create_form_fill_template():
    """Create form filling template."""

    workflow = Workflow(name="Fill Form")

    # Open URL
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{form_url}}")
    workflow.add_block(open_url)

    # Fill name
    fill_name = Block(type=BlockType.TYPE_TEXT)
    fill_name.set_parameter("selector", "{{name_selector}}")
    fill_name.set_parameter("text", "{{name}}")
    workflow.add_block(fill_name)

    # Fill email
    fill_email = Block(type=BlockType.TYPE_TEXT)
    fill_email.set_parameter("selector", "{{email_selector}}")
    fill_email.set_parameter("text", "{{email}}")
    workflow.add_block(fill_email)

    # Fill message
    fill_message = Block(type=BlockType.TYPE_TEXT)
    fill_message.set_parameter("selector", "{{message_selector}}")
    fill_message.set_parameter("text", "{{message}}")
    workflow.add_block(fill_message)

    # Submit
    submit = Block(type=BlockType.CLICK)
    submit.set_parameter("selector", "{{submit_selector}}")
    workflow.add_block(submit)

    # Connect
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="form-fill",
        name="Form Filler",
        description="Automatically fill and submit web forms",
        category="forms",
        difficulty="easy",
        author="OctoMaster Team",
        icon="📝",
        tags=["form", "automation", "contact"],
        inputs=[
            TemplateInput(
                name="form_url",
                label="Form URL",
                type="string",
                description="URL of the form to fill",
                required=True,
            ),
            TemplateInput(
                name="name",
                label="Name",
                type="string",
                description="Name to enter",
                required=True,
            ),
            TemplateInput(
                name="email",
                label="Email",
                type="string",
                description="Email to enter",
                required=True,
            ),
            TemplateInput(
                name="message",
                label="Message",
                type="string",
                description="Message to enter",
                required=True,
            ),
            TemplateInput(
                name="name_selector",
                label="Name Field Selector",
                type="string",
                default="input[name='name']",
            ),
            TemplateInput(
                name="email_selector",
                label="Email Field Selector",
                type="string",
                default="input[name='email']",
            ),
            TemplateInput(
                name="message_selector",
                label="Message Field Selector",
                type="string",
                default="textarea[name='message']",
            ),
            TemplateInput(
                name="submit_selector",
                label="Submit Button Selector",
                type="string",
                default="button[type='submit']",
            ),
        ],
        workflow=workflow,
    )

    return template


def create_price_monitor_template():
    """Create price monitoring template."""

    workflow = Workflow(name="Price Monitor")

    # Open product page
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{product_url}}")
    workflow.add_block(open_url)

    # Wait for price
    wait_price = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_price.set_parameter("selector", "{{price_selector}}")
    workflow.add_block(wait_price)

    # Get price
    get_price = Block(type=BlockType.GET_TEXT)
    get_price.set_parameter("selector", "{{price_selector}}")
    get_price.set_parameter("variable", "current_price")
    workflow.add_block(get_price)

    # Screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "price_{{timestamp}}.png")
    workflow.add_block(screenshot)

    # Connect
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="price-monitor",
        name="Price Monitor",
        description="Monitor product prices on e-commerce sites",
        category="ecommerce",
        difficulty="easy",
        author="OctoMaster Team",
        icon="💰",
        tags=["price", "monitoring", "ecommerce", "shopping"],
        inputs=[
            TemplateInput(
                name="product_url",
                label="Product URL",
                type="string",
                description="URL of the product to monitor",
                required=True,
            ),
            TemplateInput(
                name="price_selector",
                label="Price Selector",
                type="string",
                description="CSS selector for the price element",
                default=".price",
                required=True,
            ),
        ],
        outputs=["current_price", "screenshot"],
        workflow=workflow,
    )

    return template


def main():
    """Main function."""
    print("=" * 60)
    print("Creating Workflow Templates")
    print("=" * 60)

    # Create templates directory
    templates_dir = Path("resources/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create templates
    templates = [
        create_google_search_template(),
        create_form_fill_template(),
        create_price_monitor_template(),
    ]

    # Save templates
    for template in templates:
        file_path = templates_dir / f"{template.id}.template"
        template.save(file_path)
        print(f"\n✓ Created: {template.name}")
        print(f"  Category: {template.category}")
        print(f"  Difficulty: {template.difficulty}")
        print(f"  Inputs: {len(template.inputs)}")
        print(f"  Saved to: {file_path}")

    # Test template manager
    print("\n" + "=" * 60)
    print("Testing Template Manager")
    print("=" * 60)

    manager = TemplateManager(templates_dir)

    print(f"\nLoaded {len(manager.templates)} templates")
    print(f"Categories: {manager.get_categories()}")

    # Test search
    print("\n--- Searching for 'search' ---")
    results = manager.search(query="search")
    for template in results:
        print(f"  - {template.name}")

    # Test filtering by category
    print("\n--- Templates in 'scraping' category ---")
    scraping_templates = manager.get_by_category("scraping")
    for template in scraping_templates:
        print(f"  - {template.name}")

    # Test instantiation
    print("\n--- Instantiating Google Search template ---")
    google_template = manager.get_template("google-search")
    if google_template:
        params = {"search_query": "OctoMaster Pro", "output_path": "test_screenshot.png"}

        # Validate parameters
        is_valid, errors = google_template.validate_parameters(params)
        if is_valid:
            workflow = google_template.instantiate(params)
            print(f"  ✓ Created workflow: {workflow.name}")
            print(f"  Blocks: {len(workflow.blocks)}")
        else:
            print(f"  ✗ Validation errors: {errors}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
