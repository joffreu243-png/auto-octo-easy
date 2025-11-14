#!/usr/bin/env python3
"""
Example: Creating advanced workflow templates.

This script creates additional useful templates for various automation scenarios.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from octomaster.core.workflow import Workflow
from octomaster.core.block import Block, BlockType
from octomaster.core.templates import Template, TemplateInput, TemplateManager


def create_social_media_post_template():
    """Create social media posting template."""

    workflow = Workflow(name="Social Media Post")

    # Open social media platform
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{platform_url}}")
    workflow.add_block(open_url)

    # Wait for login (user should be logged in)
    wait_page = Block(type=BlockType.WAIT_FOR_LOAD)
    workflow.add_block(wait_page)

    # Click create post button
    click_create = Block(type=BlockType.CLICK)
    click_create.set_parameter("selector", "{{create_button_selector}}")
    workflow.add_block(click_create)

    # Wait for editor
    wait_editor = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_editor.set_parameter("selector", "{{editor_selector}}")
    workflow.add_block(wait_editor)

    # Type post content
    type_content = Block(type=BlockType.TYPE_TEXT)
    type_content.set_parameter("selector", "{{editor_selector}}")
    type_content.set_parameter("text", "{{post_content}}")
    workflow.add_block(type_content)

    # Upload image (if provided)
    upload_image = Block(type=BlockType.UPLOAD_FILE)
    upload_image.set_parameter("selector", "{{upload_selector}}")
    upload_image.set_parameter("file_path", "{{image_path}}")
    workflow.add_block(upload_image)

    # Wait before posting
    wait_before_post = Block(type=BlockType.WAIT)
    wait_before_post.set_parameter("seconds", "{{wait_seconds}}")
    workflow.add_block(wait_before_post)

    # Click post button
    click_post = Block(type=BlockType.CLICK)
    click_post.set_parameter("selector", "{{post_button_selector}}")
    workflow.add_block(click_post)

    # Wait for confirmation
    wait_confirm = Block(type=BlockType.WAIT)
    wait_confirm.set_parameter("seconds", 3)
    workflow.add_block(wait_confirm)

    # Screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "post_{{timestamp}}.png")
    workflow.add_block(screenshot)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="social-media-post",
        name="Social Media Post",
        description="Automatically post content to social media platforms",
        category="social",
        difficulty="medium",
        author="OctoMaster Team",
        icon="📱",
        tags=["social media", "posting", "automation", "marketing"],
        inputs=[
            TemplateInput(
                name="platform_url",
                label="Platform URL",
                type="string",
                description="URL of the social media platform",
                default="https://twitter.com",
                required=True,
            ),
            TemplateInput(
                name="post_content",
                label="Post Content",
                type="text",
                description="Content to post",
                required=True,
            ),
            TemplateInput(
                name="image_path",
                label="Image Path",
                type="string",
                description="Path to image to upload (optional)",
                required=False,
            ),
            TemplateInput(
                name="wait_seconds",
                label="Wait Before Posting",
                type="number",
                description="Seconds to wait before posting",
                default="2",
                required=False,
            ),
            TemplateInput(
                name="create_button_selector",
                label="Create Button Selector",
                type="string",
                default="[data-testid='SideNav_NewTweet_Button']",
            ),
            TemplateInput(
                name="editor_selector",
                label="Editor Selector",
                type="string",
                default="[data-testid='tweetTextarea_0']",
            ),
            TemplateInput(
                name="upload_selector",
                label="Upload Selector",
                type="string",
                default="input[type='file']",
            ),
            TemplateInput(
                name="post_button_selector",
                label="Post Button Selector",
                type="string",
                default="[data-testid='tweetButtonInline']",
            ),
        ],
        outputs=["screenshot"],
        workflow=workflow,
    )

    return template


def create_table_scraper_template():
    """Create table data scraping template."""

    workflow = Workflow(name="Table Scraper")

    # Open page with table
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{table_url}}")
    workflow.add_block(open_url)

    # Wait for table
    wait_table = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_table.set_parameter("selector", "{{table_selector}}")
    workflow.add_block(wait_table)

    # Extract table data
    extract_table = Block(type=BlockType.EXTRACT_TABLE)
    extract_table.set_parameter("selector", "{{table_selector}}")
    extract_table.set_parameter("variable", "table_data")
    workflow.add_block(extract_table)

    # Save to CSV
    save_csv = Block(type=BlockType.SAVE_DATA)
    save_csv.set_parameter("data", "{{table_data}}")
    save_csv.set_parameter("format", "csv")
    save_csv.set_parameter("path", "{{output_file}}")
    workflow.add_block(save_csv)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="table-scraper",
        name="Table Scraper",
        description="Extract data from HTML tables and save to CSV/Excel",
        category="scraping",
        difficulty="easy",
        author="OctoMaster Team",
        icon="📊",
        tags=["scraping", "data extraction", "table", "csv"],
        inputs=[
            TemplateInput(
                name="table_url",
                label="Page URL",
                type="string",
                description="URL of the page with the table",
                required=True,
            ),
            TemplateInput(
                name="table_selector",
                label="Table Selector",
                type="string",
                description="CSS selector for the table",
                default="table",
                required=True,
            ),
            TemplateInput(
                name="output_file",
                label="Output File",
                type="string",
                description="Path to save the data",
                default="table_data.csv",
                required=True,
            ),
        ],
        outputs=["table_data", "csv_file"],
        workflow=workflow,
    )

    return template


def create_login_template():
    """Create login automation template."""

    workflow = Workflow(name="Auto Login")

    # Open login page
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{login_url}}")
    workflow.add_block(open_url)

    # Wait for login form
    wait_form = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_form.set_parameter("selector", "{{username_selector}}")
    workflow.add_block(wait_form)

    # Enter username
    enter_username = Block(type=BlockType.TYPE_TEXT)
    enter_username.set_parameter("selector", "{{username_selector}}")
    enter_username.set_parameter("text", "{{username}}")
    workflow.add_block(enter_username)

    # Enter password
    enter_password = Block(type=BlockType.TYPE_TEXT)
    enter_password.set_parameter("selector", "{{password_selector}}")
    enter_password.set_parameter("text", "{{password}}")
    workflow.add_block(enter_password)

    # Click login button
    click_login = Block(type=BlockType.CLICK)
    click_login.set_parameter("selector", "{{login_button_selector}}")
    workflow.add_block(click_login)

    # Wait for successful login
    wait_success = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_success.set_parameter("selector", "{{success_element}}")
    wait_success.set_parameter("timeout", 10)
    workflow.add_block(wait_success)

    # Save cookies
    save_cookies = Block(type=BlockType.GET_COOKIES)
    save_cookies.set_parameter("variable", "session_cookies")
    workflow.add_block(save_cookies)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="auto-login",
        name="Auto Login",
        description="Automatically login to websites and save session",
        category="authentication",
        difficulty="easy",
        author="OctoMaster Team",
        icon="🔐",
        tags=["login", "authentication", "automation", "cookies"],
        inputs=[
            TemplateInput(
                name="login_url",
                label="Login URL",
                type="string",
                description="URL of the login page",
                required=True,
            ),
            TemplateInput(
                name="username",
                label="Username",
                type="string",
                description="Username or email",
                required=True,
            ),
            TemplateInput(
                name="password",
                label="Password",
                type="password",
                description="Password",
                required=True,
            ),
            TemplateInput(
                name="username_selector",
                label="Username Field Selector",
                type="string",
                default="input[name='username']",
            ),
            TemplateInput(
                name="password_selector",
                label="Password Field Selector",
                type="string",
                default="input[name='password']",
            ),
            TemplateInput(
                name="login_button_selector",
                label="Login Button Selector",
                type="string",
                default="button[type='submit']",
            ),
            TemplateInput(
                name="success_element",
                label="Success Element Selector",
                type="string",
                description="Element that appears after successful login",
                default=".dashboard",
            ),
        ],
        outputs=["session_cookies"],
        workflow=workflow,
    )

    return template


def create_screenshot_comparison_template():
    """Create screenshot comparison template."""

    workflow = Workflow(name="Screenshot Comparison")

    # Open page
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{page_url}}")
    workflow.add_block(open_url)

    # Wait for page load
    wait_page = Block(type=BlockType.WAIT_FOR_LOAD)
    workflow.add_block(wait_page)

    # Wait additional time
    wait_extra = Block(type=BlockType.WAIT)
    wait_extra.set_parameter("seconds", "{{wait_seconds}}")
    workflow.add_block(wait_extra)

    # Take screenshot
    screenshot = Block(type=BlockType.SCREENSHOT)
    screenshot.set_parameter("path", "{{output_path}}")
    screenshot.set_parameter("full_page", "{{full_page}}")
    workflow.add_block(screenshot)

    # Compare with baseline (if provided)
    compare = Block(type=BlockType.COMPARE_IMAGE)
    compare.set_parameter("baseline_path", "{{baseline_path}}")
    compare.set_parameter("current_path", "{{output_path}}")
    compare.set_parameter("diff_path", "diff_{{timestamp}}.png")
    compare.set_parameter("threshold", "{{threshold}}")
    workflow.add_block(compare)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="screenshot-comparison",
        name="Screenshot Comparison",
        description="Take screenshots and compare with baseline for visual regression testing",
        category="testing",
        difficulty="medium",
        author="OctoMaster Team",
        icon="📸",
        tags=["screenshot", "testing", "visual regression", "comparison"],
        inputs=[
            TemplateInput(
                name="page_url",
                label="Page URL",
                type="string",
                description="URL of the page to screenshot",
                required=True,
            ),
            TemplateInput(
                name="output_path",
                label="Screenshot Path",
                type="string",
                description="Where to save the screenshot",
                default="screenshot.png",
                required=True,
            ),
            TemplateInput(
                name="baseline_path",
                label="Baseline Path",
                type="string",
                description="Path to baseline image for comparison",
                required=False,
            ),
            TemplateInput(
                name="wait_seconds",
                label="Wait Time",
                type="number",
                description="Seconds to wait before screenshot",
                default="2",
            ),
            TemplateInput(
                name="full_page",
                label="Full Page",
                type="boolean",
                description="Capture full page or viewport only",
                default="true",
            ),
            TemplateInput(
                name="threshold",
                label="Comparison Threshold",
                type="number",
                description="Acceptable difference threshold (0-100)",
                default="5",
            ),
        ],
        outputs=["screenshot", "diff_image", "is_different"],
        workflow=workflow,
    )

    return template


def create_api_test_template():
    """Create API testing template."""

    workflow = Workflow(name="API Test")

    # Open API documentation or test page
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{api_doc_url}}")
    workflow.add_block(open_url)

    # Execute API request
    api_request = Block(type=BlockType.HTTP_REQUEST)
    api_request.set_parameter("method", "{{http_method}}")
    api_request.set_parameter("url", "{{api_endpoint}}")
    api_request.set_parameter("headers", "{{headers}}")
    api_request.set_parameter("body", "{{request_body}}")
    api_request.set_parameter("variable", "api_response")
    workflow.add_block(api_request)

    # Validate status code
    validate_status = Block(type=BlockType.CONDITION)
    validate_status.set_parameter("condition", "{{api_response.status}} == {{expected_status}}")
    workflow.add_block(validate_status)

    # Extract response data
    extract_data = Block(type=BlockType.EXTRACT_JSON)
    extract_data.set_parameter("json", "{{api_response.body}}")
    extract_data.set_parameter("path", "{{json_path}}")
    extract_data.set_parameter("variable", "extracted_value")
    workflow.add_block(extract_data)

    # Log result
    log_result = Block(type=BlockType.LOG)
    log_result.set_parameter("message", "API Test Result: {{extracted_value}}")
    log_result.set_parameter("level", "info")
    workflow.add_block(log_result)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="api-test",
        name="API Test",
        description="Test API endpoints and validate responses",
        category="testing",
        difficulty="medium",
        author="OctoMaster Team",
        icon="🔌",
        tags=["api", "testing", "http", "validation"],
        inputs=[
            TemplateInput(
                name="api_doc_url",
                label="API Documentation URL",
                type="string",
                description="URL of API documentation (optional)",
                required=False,
            ),
            TemplateInput(
                name="api_endpoint",
                label="API Endpoint",
                type="string",
                description="Full URL of the API endpoint",
                required=True,
            ),
            TemplateInput(
                name="http_method",
                label="HTTP Method",
                type="string",
                description="GET, POST, PUT, DELETE, etc.",
                default="GET",
                required=True,
            ),
            TemplateInput(
                name="headers",
                label="Headers",
                type="text",
                description="Request headers (JSON format)",
                default='{"Content-Type": "application/json"}',
            ),
            TemplateInput(
                name="request_body",
                label="Request Body",
                type="text",
                description="Request body (JSON format)",
                required=False,
            ),
            TemplateInput(
                name="expected_status",
                label="Expected Status Code",
                type="number",
                description="Expected HTTP status code",
                default="200",
                required=True,
            ),
            TemplateInput(
                name="json_path",
                label="JSON Path",
                type="string",
                description="JSONPath to extract from response",
                default="$.data",
            ),
        ],
        outputs=["api_response", "extracted_value"],
        workflow=workflow,
    )

    return template


def create_email_sender_template():
    """Create email sending template."""

    workflow = Workflow(name="Email Sender")

    # Open webmail or compose page
    open_url = Block(type=BlockType.OPEN_URL)
    open_url.set_parameter("url", "{{webmail_url}}")
    workflow.add_block(open_url)

    # Click compose
    click_compose = Block(type=BlockType.CLICK)
    click_compose.set_parameter("selector", "{{compose_button}}")
    workflow.add_block(click_compose)

    # Wait for compose window
    wait_compose = Block(type=BlockType.WAIT_FOR_ELEMENT)
    wait_compose.set_parameter("selector", "{{to_field_selector}}")
    workflow.add_block(wait_compose)

    # Fill recipient
    fill_to = Block(type=BlockType.TYPE_TEXT)
    fill_to.set_parameter("selector", "{{to_field_selector}}")
    fill_to.set_parameter("text", "{{recipient}}")
    workflow.add_block(fill_to)

    # Fill subject
    fill_subject = Block(type=BlockType.TYPE_TEXT)
    fill_subject.set_parameter("selector", "{{subject_field_selector}}")
    fill_subject.set_parameter("text", "{{subject}}")
    workflow.add_block(fill_subject)

    # Fill body
    fill_body = Block(type=BlockType.TYPE_TEXT)
    fill_body.set_parameter("selector", "{{body_field_selector}}")
    fill_body.set_parameter("text", "{{body}}")
    workflow.add_block(fill_body)

    # Attach file (if provided)
    attach_file = Block(type=BlockType.UPLOAD_FILE)
    attach_file.set_parameter("selector", "{{attachment_selector}}")
    attach_file.set_parameter("file_path", "{{attachment_path}}")
    workflow.add_block(attach_file)

    # Wait before sending
    wait_send = Block(type=BlockType.WAIT)
    wait_send.set_parameter("seconds", 2)
    workflow.add_block(wait_send)

    # Click send
    click_send = Block(type=BlockType.CLICK)
    click_send.set_parameter("selector", "{{send_button_selector}}")
    workflow.add_block(click_send)

    # Connect blocks
    blocks = workflow.blocks
    for i in range(len(blocks) - 1):
        workflow.connect_blocks(blocks[i].id, blocks[i + 1].id)

    template = Template(
        id="email-sender",
        name="Email Sender",
        description="Send emails via webmail interface with attachments",
        category="communication",
        difficulty="medium",
        author="OctoMaster Team",
        icon="📧",
        tags=["email", "sending", "webmail", "automation"],
        inputs=[
            TemplateInput(
                name="webmail_url",
                label="Webmail URL",
                type="string",
                description="URL of webmail service",
                default="https://mail.google.com",
                required=True,
            ),
            TemplateInput(
                name="recipient",
                label="Recipient",
                type="string",
                description="Email recipient address",
                required=True,
            ),
            TemplateInput(
                name="subject",
                label="Subject",
                type="string",
                description="Email subject",
                required=True,
            ),
            TemplateInput(
                name="body",
                label="Body",
                type="text",
                description="Email body content",
                required=True,
            ),
            TemplateInput(
                name="attachment_path",
                label="Attachment Path",
                type="string",
                description="Path to file to attach (optional)",
                required=False,
            ),
            TemplateInput(
                name="compose_button",
                label="Compose Button Selector",
                type="string",
                default=".T-I.T-I-KE",
            ),
            TemplateInput(
                name="to_field_selector",
                label="To Field Selector",
                type="string",
                default="textarea[name='to']",
            ),
            TemplateInput(
                name="subject_field_selector",
                label="Subject Field Selector",
                type="string",
                default="input[name='subjectbox']",
            ),
            TemplateInput(
                name="body_field_selector",
                label="Body Field Selector",
                type="string",
                default="div[aria-label='Message Body']",
            ),
            TemplateInput(
                name="attachment_selector",
                label="Attachment Selector",
                type="string",
                default="input[type='file'][name='Filedata']",
            ),
            TemplateInput(
                name="send_button_selector",
                label="Send Button Selector",
                type="string",
                default="div[aria-label='Send']",
            ),
        ],
        outputs=["sent_confirmation"],
        workflow=workflow,
    )

    return template


def main():
    """Main function."""
    print("=" * 60)
    print("Creating Advanced Workflow Templates")
    print("=" * 60)

    # Create templates directory
    templates_dir = Path("resources/templates")
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Create templates
    templates = [
        create_social_media_post_template(),
        create_table_scraper_template(),
        create_login_template(),
        create_screenshot_comparison_template(),
        create_api_test_template(),
        create_email_sender_template(),
    ]

    # Save templates
    for template in templates:
        file_path = templates_dir / f"{template.id}.template"
        template.save(file_path)
        print(f"\n✓ Created: {template.name}")
        print(f"  ID: {template.id}")
        print(f"  Category: {template.category}")
        print(f"  Difficulty: {template.difficulty}")
        print(f"  Inputs: {len(template.inputs)}")
        print(f"  Icon: {template.icon}")
        print(f"  Saved to: {file_path}")

    print("\n" + "=" * 60)
    print(f"Successfully created {len(templates)} advanced templates!")
    print("=" * 60)

    # Show summary
    print("\nTemplate Summary:")
    print("-" * 60)
    categories = {}
    for template in templates:
        if template.category not in categories:
            categories[template.category] = []
        categories[template.category].append(template.name)

    for category, names in categories.items():
        print(f"\n{category.upper()}:")
        for name in names:
            print(f"  • {name}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()
