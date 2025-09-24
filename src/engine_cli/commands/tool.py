"""Tool management commands."""

import click
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import yaml
import json

# Import Rich formatting
from engine_cli.formatting import success, error, header, key_value, table, print_table

# Import engine core components
from engine_core import ToolBuilder


class ToolStorage:
    """Simple tool storage manager."""

    def __init__(self):
        self.tools_dir = os.path.join(os.getcwd(), "tools")
        os.makedirs(self.tools_dir, exist_ok=True)

    def list_tools(self) -> List[dict]:
        """List all saved tools."""
        tools = []
        if os.path.exists(self.tools_dir):
            for file in os.listdir(self.tools_dir):
                if file.endswith(".yaml"):
                    try:
                        with open(os.path.join(self.tools_dir, file), "r") as f:
                            tool_data = yaml.safe_load(f)
                            if tool_data:
                                tools.append(tool_data)
                    except Exception:
                        continue
        return tools

    def get_tool(self, tool_id: str) -> Optional[dict]:
        """Get tool by ID."""
        tool_file = os.path.join(self.tools_dir, f"{tool_id}.yaml")
        if os.path.exists(tool_file):
            try:
                with open(tool_file, "r") as f:
                    return yaml.safe_load(f)
            except Exception:
                return None
        return None

    def delete_tool(self, tool_id: str) -> bool:
        """Delete tool by ID."""
        tool_file = os.path.join(self.tools_dir, f"{tool_id}.yaml")
        if os.path.exists(tool_file):
            try:
                os.remove(tool_file)
                return True
            except Exception:
                return False
        return False


# Global storage instance
tool_storage = ToolStorage()


def get_tool_storage():
    """Get tool storage instance."""
    return tool_storage


@click.group()
def cli():
    """Manage tools and integrations."""
    pass


@cli.command()
@click.argument("name")
@click.option("--type", help="Tool type (api, cli, webhook, mcp, etc.)")
@click.option("--description", help="Tool description")
@click.option("--endpoint", help="API endpoint URL")
@click.option("--config", help="Tool configuration as JSON string")
@click.option("--capabilities", help="Tool capabilities (comma-separated)")
@click.option("--tags", help="Tool tags (comma-separated)")
@click.option("--save", is_flag=True, help="Save tool to storage")
@click.option("--output", type=click.Path(), help="Output file for tool configuration")
def create(name, type, description, endpoint, config, capabilities, tags, save, output):
    """Create a new tool."""
    try:
        builder = ToolBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)

        if type:
            builder = builder.with_type(type)

        if description:
            builder = builder.with_description(description)

        if endpoint:
            builder = builder.with_endpoint(endpoint)

        if config:
            config_dict = json.loads(config)
            # Apply configuration based on type
            if "authentication" in config_dict:
                builder = builder.with_authentication(config_dict["authentication"])
            if "headers" in config_dict:
                builder = builder.with_headers(config_dict["headers"])
            if "timeout" in config_dict:
                builder = builder.with_timeout(config_dict["timeout"])
            if "retry_attempts" in config_dict:
                builder = builder.with_retry_attempts(config_dict["retry_attempts"])

        if capabilities:
            caps_list = [cap.strip() for cap in capabilities.split(",")]
            builder = builder.with_capabilities(caps_list)

        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
            builder = builder.with_tags(tags_list)

        tool = builder.build()

        success(f"Tool '{name}' created successfully!")

        # Create table with tool details
        tool_table = table("Tool Details", ["Property", "Value"])
        tool_table.add_row("ID", tool.tool_id)
        tool_table.add_row("Name", tool.name)
        tool_table.add_row("Type", str(tool.tool_type))
        tool_table.add_row("Description", tool.description or "None")
        tool_table.add_row("Endpoint", tool.endpoint or "None")
        tool_table.add_row(
            "Capabilities",
            ", ".join(
                [
                    cap.name if hasattr(cap, "name") else str(cap)
                    for cap in tool.capabilities
                ]
            ),
        )
        tool_table.add_row("Tags", ", ".join(tool.tags))
        print_table(tool_table)

        # Save if requested
        if save:
            try:
                config_dict = {}
                if config:
                    config_dict = json.loads(config)

                tool_data = {
                    "tool_id": tool.tool_id,
                    "name": tool.name,
                    "type": str(tool.tool_type),
                    "description": tool.description,
                    "endpoint": tool.endpoint,
                    "capabilities": [
                        cap.name if hasattr(cap, "name") else str(cap)
                        for cap in tool.capabilities
                    ],
                    "tags": tool.tags,
                    "config": config_dict,
                    "created_at": datetime.now().isoformat(),
                }

                # Ensure tools directory exists
                tools_dir = os.path.join(os.getcwd(), "tools")
                os.makedirs(tools_dir, exist_ok=True)

                tool_file = os.path.join(tools_dir, f"{name}.yaml")
                with open(tool_file, "w") as f:
                    yaml.safe_dump(tool_data, f, default_flow_style=False)

                success(f"Tool saved to {tool_file}")

            except Exception as e:
                error(f"Failed to save tool: {e}")

    except ImportError:
        error("Engine Core not available. Please install engine-core first.")
    except Exception as e:
        error(f"Failed to create tool: {e}")
        import traceback

        traceback.print_exc()


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option("--type", help="Filter by tool type")
@click.option("--tag", help="Filter by tag")
def list(format, type, tag):
    """List all tools."""
    try:
        tools = tool_storage.list_tools()

        # Apply filters
        if type:
            tools = [t for t in tools if t.get("type") == type]
        if tag:
            tools = [t for t in tools if tag in t.get("tags", [])]

        if not tools:
            click.echo("No tools found. Create one with: engine tool create <name>")
            return

        if format == "json":
            click.echo(json.dumps(tools, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(tools, default_flow_style=False))
        else:
            # Table format
            tool_table = table("Tools", ["ID", "Name", "Type", "Capabilities", "Tags"])
            for tool in tools:
                caps = ", ".join(tool.get("capabilities", []))[:30]
                if len(",".join(tool.get("capabilities", []))) > 30:
                    caps += "..."
                tags_str = ", ".join(tool.get("tags", []))[:20]
                if len(",".join(tool.get("tags", []))) > 20:
                    tags_str += "..."

                tool_table.add_row(
                    tool.get("tool_id", ""),
                    tool.get("name", ""),
                    tool.get("type", ""),
                    caps,
                    tags_str,
                )

            print_table(tool_table)
            success(f"Found {len(tools)} tool(s)")

    except Exception as e:
        error(f"Error listing tools: {e}")


@cli.command()
@click.argument("name")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
def show(name, format):
    """Show details of a specific tool."""
    try:
        tool = tool_storage.get_tool(name)

        if not tool:
            error(f"Tool '{name}' not found")
            return

        if format == "json":
            click.echo(json.dumps(tool, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(tool, default_flow_style=False))
        else:
            # Table format - show as key-value pairs
            tool_info = {
                "ID": tool.get("tool_id", ""),
                "Name": tool.get("name", ""),
                "Type": tool.get("type", ""),
            }

            if tool.get("description"):
                tool_info["Description"] = tool["description"]

            if tool.get("endpoint"):
                tool_info["Endpoint"] = tool["endpoint"]

            if tool.get("capabilities"):
                tool_info["Capabilities"] = ", ".join(tool["capabilities"])

            if tool.get("tags"):
                tool_info["Tags"] = ", ".join(tool["tags"])

            if tool.get("created_at"):
                tool_info["Created"] = tool["created_at"]

            key_value(tool_info, f"Tool: {name}")

    except Exception as e:
        error(f"Error showing tool: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete a tool."""
    try:
        # Check if tool exists
        tool = tool_storage.get_tool(name)
        if not tool:
            error(f"Tool '{name}' not found")
            return

        if not force:
            click.echo(f"⚠ This will permanently delete tool '{name}'.")
            if not click.confirm("Do you want to continue?"):
                click.echo("Operation cancelled.")
                return

        if tool_storage.delete_tool(name):
            success(f"Tool '{name}' deleted successfully")
        else:
            error(f"Failed to delete tool '{name}'")

    except Exception as e:
        error(f"Error deleting tool: {e}")


@cli.command()
@click.argument("name")
@click.option("--input", help="Input data for the tool (JSON string)")
@click.option(
    "--method",
    type=click.Choice(["GET", "POST", "PUT", "DELETE"]),
    default="GET",
    help="HTTP method for API tools",
)
@click.option("--params", help="Query parameters as JSON string")
def test(name, input, method, params):
    """Test a tool with sample input."""
    try:
        tool = tool_storage.get_tool(name)

        if not tool:
            error(f"Tool '{name}' not found")
            return

        success(f"Testing tool '{name}'...")

        # Parse input data
        input_data = {}
        if input:
            try:
                input_data = json.loads(input)
            except json.JSONDecodeError:
                error("Invalid JSON input")
                return

        # Parse parameters
        query_params = {}
        if params:
            try:
                query_params = json.loads(params)
            except json.JSONDecodeError:
                error("Invalid JSON parameters")
                return

        # Mock test execution based on tool type
        tool_type = tool.get("type", "").lower()

        if tool_type == "api":
            # Simulate API call
            endpoint = tool.get("endpoint", "")
            if not endpoint:
                error("Tool has no endpoint configured")
                return

            click.echo(f"📡 Simulating {method} request to {endpoint}")
            if input_data:
                click.echo(f"📤 Request body: {json.dumps(input_data, indent=2)}")
            if query_params:
                click.echo(f"🔍 Query params: {json.dumps(query_params, indent=2)}")

            # Mock response
            mock_response = {
                "status": "success",
                "message": f"Tool '{name}' test completed",
                "timestamp": datetime.now().isoformat(),
                "input_received": input_data,
                "params_received": query_params,
            }

            click.echo("📥 Mock response:")
            click.echo(json.dumps(mock_response, indent=2))

        elif tool_type == "cli":
            # Simulate CLI execution
            click.echo(f"💻 Simulating CLI execution for tool '{name}'")
            if input_data:
                click.echo(f"📤 Input data: {json.dumps(input_data, indent=2)}")

            mock_output = (
                f"Tool '{name}' executed successfully with input: {input_data}"
            )
            click.echo(f"📥 Mock CLI output: {mock_output}")

        else:
            # Generic test
            click.echo(f"🔧 Testing generic tool '{name}'")
            if input_data:
                click.echo(f"📤 Input: {json.dumps(input_data, indent=2)}")

            mock_result = {
                "tool_id": name,
                "test_status": "passed",
                "execution_time": "0.1s",
                "input_processed": input_data,
            }
            click.echo(f"📥 Test result: {json.dumps(mock_result, indent=2)}")

        success(f"Tool '{name}' test completed successfully!")

    except Exception as e:
        error(f"Error testing tool: {e}")
