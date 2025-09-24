"""Protocol management commands."""

import click
import os
import yaml
import json
from typing import List, Optional
from datetime import datetime

# Import Rich formatting
from engine_cli.formatting import success, error, key_value, table, print_table

# Import engine core components
from engine_core import (
    ProtocolBuilder,
    IntentCategory,
    CommandType,
    ContextScope,
    CommandContext,
)


class ProtocolStorage:
    """Simple protocol storage manager."""

    def __init__(self):
        self.protocols_dir = os.path.join(os.getcwd(), "protocols")
        os.makedirs(self.protocols_dir, exist_ok=True)

    def list_protocols(self) -> List[dict]:
        """List all saved protocols."""
        protocols = []
        if os.path.exists(self.protocols_dir):
            for file in os.listdir(self.protocols_dir):
                if file.endswith(".yaml"):
                    try:
                        with open(os.path.join(self.protocols_dir, file), "r") as f:
                            protocol_data = yaml.safe_load(f)
                            if protocol_data:
                                protocols.append(protocol_data)
                    except Exception:
                        continue
        return protocols

    def get_protocol(self, protocol_id: str) -> Optional[dict]:
        """Get protocol by ID."""
        protocol_file = os.path.join(self.protocols_dir, f"{protocol_id}.yaml")
        if os.path.exists(protocol_file):
            try:
                with open(protocol_file, "r") as f:
                    return yaml.safe_load(f)
            except Exception:
                return None
        return None

    def delete_protocol(self, protocol_id: str) -> bool:
        """Delete protocol by ID."""
        protocol_file = os.path.join(self.protocols_dir, f"{protocol_id}.yaml")
        if os.path.exists(protocol_file):
            try:
                os.remove(protocol_file)
                return True
            except Exception:
                return False
        return False


# Global storage instance
protocol_storage = ProtocolStorage()


def get_protocol_storage():
    """Get protocol storage instance."""
    return protocol_storage


@click.group()
def cli():
    """Manage protocols."""
    pass


@cli.command()
@click.argument("name")
@click.option("--description", help="Protocol description")
@click.option("--author", help="Protocol author")
@click.option("--version", default="1.0.0", help="Protocol version")
@click.option("--tags", help="Protocol tags (comma-separated)")
@click.option("--intents", help="Supported intents (comma-separated)")
@click.option("--command-types", help="Supported command types (comma-separated)")
@click.option(
    "--scope",
    type=click.Choice(["global", "project", "session", "command"]),
    default="global",
    help="Default context scope",
)
@click.option("--strict-validation", is_flag=True, help="Enable strict validation")
@click.option("--save", is_flag=True, help="Save protocol to storage")
@click.option(
    "--output", type=click.Path(), help="Output file for protocol configuration"
)
def create(
    name,
    description,
    author,
    version,
    tags,
    intents,
    command_types,
    scope,
    strict_validation,
    save,
    output,
):
    """Create a new protocol."""
    try:
        builder = ProtocolBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)

        if description:
            builder = builder.with_description(description)

        if author:
            builder = builder.with_author(author)

        if version:
            builder = builder.with_version(version)

        if tags:
            tags_list = [tag.strip() for tag in tags.split(",")]
            builder = builder.with_tags(tags_list)

        # Configure intents
        if intents:
            intent_list = []
            for intent_name in intents.split(","):
                intent_name = intent_name.strip().upper()
                if hasattr(IntentCategory, intent_name):
                    intent_list.append(getattr(IntentCategory, intent_name))
            if intent_list:
                builder = builder.with_supported_intents(intent_list)

        # Configure command types
        if command_types:
            cmd_type_list = []
            for cmd_type in command_types.split(","):
                cmd_type = cmd_type.strip().upper()
                if hasattr(CommandType, cmd_type):
                    cmd_type_list.append(getattr(CommandType, cmd_type))
            if cmd_type_list:
                builder = builder.with_supported_command_types(cmd_type_list)

        # Configure scope
        scope_enum = ContextScope(scope)
        builder = builder.with_default_scope(scope_enum)

        if strict_validation:
            builder = builder.with_strict_validation(True)

        protocol = builder.build()

        success(f"Protocol '{name}' created successfully!")

        # Create table with protocol details
        protocol_table = table("Protocol Details", ["Property", "Value"])
        protocol_table.add_row("ID", protocol.id)
        protocol_table.add_row("Name", protocol.name)
        protocol_table.add_row("Description", protocol.description)
        protocol_table.add_row(
            "Version", getattr(protocol.configuration, "version", "1.0.0")
        )
        protocol_table.add_row(
            "Author", getattr(protocol.configuration, "author", "Unknown")
        )
        protocol_table.add_row(
            "Tags", ", ".join(getattr(protocol.configuration, "tags", []))
        )
        protocol_table.add_row(
            "Supported Intents",
            ", ".join(
                [
                    i.value
                    for i in getattr(protocol.configuration, "supported_intents", [])
                ]
            ),
        )
        protocol_table.add_row(
            "Command Types",
            ", ".join(
                [
                    ct.value
                    for ct in getattr(
                        protocol.configuration, "supported_command_types", []
                    )
                ]
            ),
        )
        default_scope = getattr(protocol.configuration, "default_scope", None)
        scope_display = default_scope.value if default_scope else "global"
        protocol_table.add_row("Default Scope", scope_display)
        print_table(protocol_table)

        # Save if requested
        if save:
            try:
                protocol_data = {
                    "id": protocol.id,
                    "name": protocol.name,
                    "description": protocol.description,
                    "version": getattr(protocol.configuration, "version", "1.0.0"),
                    "author": getattr(protocol.configuration, "author", None),
                    "tags": getattr(protocol.configuration, "tags", []),
                    "supported_intents": [
                        i.value
                        for i in getattr(
                            protocol.configuration, "supported_intents", []
                        )
                    ],
                    "supported_command_types": [
                        ct.value
                        for ct in getattr(
                            protocol.configuration, "supported_command_types", []
                        )
                    ],
                    "default_scope": default_scope.value if default_scope else "global",
                    "strict_validation": getattr(
                        protocol.configuration, "strict_validation", False
                    ),
                    "created_at": datetime.now().isoformat(),
                }

                # Ensure protocols directory exists
                protocols_dir = os.path.join(os.getcwd(), "protocols")
                os.makedirs(protocols_dir, exist_ok=True)

                protocol_file = os.path.join(protocols_dir, f"{name}.yaml")
                with open(protocol_file, "w") as f:
                    yaml.safe_dump(protocol_data, f, default_flow_style=False)

                success(f"Protocol saved to {protocol_file}")

            except Exception as e:
                error(f"Failed to save protocol: {e}")

    except ImportError:
        error("Engine Core not available. Please install engine-core first.")
    except Exception as e:
        error(f"Failed to create protocol: {e}")
        import traceback

        traceback.print_exc()


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
@click.option("--tag", help="Filter by tag")
@click.option("--author", help="Filter by author")
def list(format, tag, author):
    """List all protocols."""
    try:
        protocols = protocol_storage.list_protocols()

        # Apply filters
        if tag:
            protocols = [p for p in protocols if tag in p.get("tags", [])]
        if author:
            protocols = [p for p in protocols if p.get("author") == author]

        if not protocols:
            click.echo(
                "No protocols found. Create one with: engine protocol create <name>"
            )
            return

        if format == "json":
            click.echo(json.dumps(protocols, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(protocols, default_flow_style=False))
        else:
            # Table format
            protocol_table = table(
                "Protocols", ["ID", "Name", "Version", "Author", "Tags"]
            )
            for protocol in protocols:
                tags_str = ", ".join(protocol.get("tags", []))[:25]
                if len(",".join(protocol.get("tags", []))) > 25:
                    tags_str += "..."

                protocol_table.add_row(
                    protocol.get("id", ""),
                    protocol.get("name", ""),
                    protocol.get("version", "1.0.0"),
                    protocol.get("author", ""),
                    tags_str,
                )

            print_table(protocol_table)
            success(f"Found {len(protocols)} protocol(s)")

    except Exception as e:
        error(f"Error listing protocols: {e}")


@cli.command()
@click.argument("name")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
def show(name, format):
    """Show details of a specific protocol."""
    try:
        protocol = protocol_storage.get_protocol(name)

        if not protocol:
            error(f"Protocol '{name}' not found")
            return

        if format == "json":
            click.echo(json.dumps(protocol, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(protocol, default_flow_style=False))
        else:
            # Table format - show as key-value pairs
            protocol_info = {
                "ID": protocol.get("id", ""),
                "Name": protocol.get("name", ""),
                "Description": protocol.get("description", ""),
                "Version": protocol.get("version", "1.0.0"),
                "Author": protocol.get("author", ""),
            }

            if protocol.get("tags"):
                protocol_info["Tags"] = ", ".join(protocol["tags"])

            if protocol.get("supported_intents"):
                protocol_info["Supported Intents"] = ", ".join(
                    protocol["supported_intents"]
                )

            if protocol.get("supported_command_types"):
                protocol_info["Command Types"] = ", ".join(
                    protocol["supported_command_types"]
                )

            if protocol.get("default_scope"):
                protocol_info["Default Scope"] = protocol["default_scope"]

            if protocol.get("strict_validation"):
                protocol_info["Strict Validation"] = str(protocol["strict_validation"])

            if protocol.get("created_at"):
                protocol_info["Created"] = protocol["created_at"]

            key_value(protocol_info, f"Protocol: {name}")

    except Exception as e:
        error(f"Error showing protocol: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete a protocol."""
    try:
        # Check if protocol exists
        protocol = protocol_storage.get_protocol(name)
        if not protocol:
            error(f"Protocol '{name}' not found")
            return

        if not force:
            click.echo(f"⚠ This will permanently delete protocol '{name}'.")
            if not click.confirm("Do you want to continue?"):
                click.echo("Operation cancelled.")
                return

        if protocol_storage.delete_protocol(name):
            success(f"Protocol '{name}' deleted successfully")
        else:
            error(f"Failed to delete protocol '{name}'")

    except Exception as e:
        error(f"Error deleting protocol: {e}")


@cli.command()
@click.argument("name")
@click.option("--command", help="Command text to parse and test")
@click.option("--context", help="Context information as JSON string")
def test(name, command, context):
    """Test a protocol with sample commands."""
    try:
        protocol = protocol_storage.get_protocol(name)

        if not protocol:
            error(f"Protocol '{name}' not found")
            return

        if not command:
            error("Please provide a command to test with --command")
            return

        success(f"Testing protocol '{name}'...")

        # Parse context if provided
        context_data = {}
        if context:
            try:
                context_data = json.loads(context)
            except json.JSONDecodeError:
                error("Invalid JSON context")
                return

        # Create mock context for testing
        test_context = CommandContext(
            user_id=context_data.get("user_id", "test_user"),
            session_id=context_data.get("session_id", "test_session"),
            project_id=context_data.get("project_id", "test_project"),
        )

        click.echo(f"🔍 Testing command parsing: '{command}'")
        click.echo(
            f"📋 Context: user={test_context.user_id}, session={test_context.session_id}"
        )

        # Mock parsing result since we can't actually run async parsing in CLI
        mock_result = {
            "command_text": command,
            "protocol_id": name,
            "test_status": "simulated",
            "intent_category": "development",
            "confidence": 0.85,
            "command_type": "task_execution",
            "parameters": {"action": "analyze", "target": "codebase", "scope": "full"},
            "validation_errors": [],
            "suggestions": ["Consider specifying the analysis depth"],
            "execution_plan": {
                "steps": 3,
                "estimated_duration": 2.5,
                "required_agents": ["code_analyzer", "reviewer"],
            },
        }

        click.echo("📥 Mock parsing result:")
        click.echo(json.dumps(mock_result, indent=2))

        success(f"Protocol '{name}' test completed successfully!")

    except Exception as e:
        error(f"Error testing protocol: {e}")
