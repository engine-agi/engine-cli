"""Team management commands."""

import click
import os
import yaml
import json
from typing import List, Optional
from datetime import datetime

# Import Rich formatting
from engine_cli.formatting import success, error, key_value, table, print_table

# Import engine core components
from engine_core import TeamBuilder, TeamCoordinationStrategy, TeamMemberRole


class TeamStorage:
    """Simple team storage manager."""

    def __init__(self):
        self.teams_dir = os.path.join(os.getcwd(), "teams")
        os.makedirs(self.teams_dir, exist_ok=True)

    def list_teams(self) -> List[dict]:
        """List all saved teams."""
        teams = []
        if os.path.exists(self.teams_dir):
            for file in os.listdir(self.teams_dir):
                if file.endswith(".yaml"):
                    try:
                        with open(os.path.join(self.teams_dir, file), "r") as f:
                            team_data = yaml.safe_load(f)
                            if team_data:
                                teams.append(team_data)
                    except Exception:
                        continue
        return teams

    def get_team(self, team_id: str) -> Optional[dict]:
        """Get team by ID."""
        team_file = os.path.join(self.teams_dir, f"{team_id}.yaml")
        if os.path.exists(team_file):
            try:
                with open(team_file, "r") as f:
                    return yaml.safe_load(f)
            except Exception:
                return None
        return None

    def delete_team(self, team_id: str) -> bool:
        """Delete team by ID."""
        team_file = os.path.join(self.teams_dir, f"{team_id}.yaml")
        if os.path.exists(team_file):
            try:
                os.remove(team_file)
                return True
            except Exception:
                return False
        return False


# Global storage instance
team_storage = TeamStorage()


def get_team_storage():
    """Get team storage instance."""
    return team_storage


@click.group()
def cli():
    """Manage agent teams."""
    pass


@cli.command()
@click.argument("name")
@click.option("--agents", help="Agent IDs (comma-separated)")
@click.option(
    "--leader",
    help="Agent ID to be the team leader (required for hierarchical strategy)",
)
@click.option(
    "--strategy",
    type=click.Choice(["hierarchical", "collaborative", "parallel", "sequential"]),
    default="collaborative",
    help="Coordination strategy",
)
@click.option("--description", help="Team description")
@click.option("--save", is_flag=True, help="Save team to storage")
@click.option("--output", type=click.Path(), help="Output file for team configuration")
def create(name, agents, leader, strategy, description, save, output):
    """Create a new team with agent coordination."""
    try:
        # Convert string to enum
        strategy_enum = TeamCoordinationStrategy(strategy.lower())

        # Build the team using TeamBuilder
        builder = TeamBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)
        builder = builder.with_coordination_strategy(strategy_enum)

        if description:
            builder = builder.with_description(description)

        # Load agents if specified
        agent_dict = {}
        if agents:
            # Split by comma and strip whitespace
            agent_ids = [a.strip() for a in agents.split(",")]
        else:
            agent_ids = []

        # Add members to team builder
        for agent_id in agent_ids:
            builder = builder.add_member(agent_id)

        # Create real agent objects for the build method
        for agent_id in agent_ids:
            from engine_core import AgentBuilder

            agent_builder = AgentBuilder()
            agent_builder = agent_builder.with_id(agent_id)
            agent_builder = agent_builder.with_name(agent_id)
            agent_builder = agent_builder.with_model("claude-3.5-sonnet")

            agent_obj = agent_builder.build()
            agent_dict[agent_id] = agent_obj

        # Build the team with agents
        team = builder.build(agents=agent_dict)

        # Display team info
        success(f"Team '{name}' created successfully!")

        # Create table with team details
        team_table = table("Team Details", ["Property", "Value"])
        team_table.add_row("ID", team.id)
        team_table.add_row("Name", team.name)
        team_table.add_row("Strategy", team.coordination_strategy)
        team_table.add_row(
            "Agents",
            ", ".join([a.id for a in team.agents.values()]) if team.agents else "None",
        )
        team_table.add_row("Leader", leader or "None")
        team_table.add_row("Description", description or "None")
        print_table(team_table)

        # Save if requested
        if save:
            try:
                team_data = {
                    "id": team.id,
                    "name": team.name,
                    "coordination_strategy": team.coordination_strategy,
                    "agents": (
                        [a.id for a in team.agents.values()] if team.agents else []
                    ),
                    "leader": leader,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                }

                # Ensure teams directory exists
                teams_dir = os.path.join(os.getcwd(), "teams")
                os.makedirs(teams_dir, exist_ok=True)

                team_file = os.path.join(teams_dir, f"{name}.yaml")
                with open(team_file, "w") as f:
                    yaml.safe_dump(team_data, f, default_flow_style=False)

                success(f"Team saved to {team_file}")

            except Exception as e:
                error(f"Failed to save team: {e}")

    except Exception as e:
        error(f"Failed to create team: {e}")
        import traceback

        traceback.print_exc()


@cli.command()
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
def list(format):
    """List all saved teams."""
    try:
        teams = team_storage.list_teams()

        if not teams:
            click.echo("No teams found. Create one with: engine team create <name>")
            return

        if format == "json":
            click.echo(json.dumps(teams, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(teams, default_flow_style=False))
        else:
            # Table format
            team_table = table(
                "Teams", ["ID", "Name", "Strategy", "Agents", "Description"]
            )

            for team in teams:
                agents = ", ".join(team.get("agents", [])) if team.get("agents") else ""
                desc = (
                    team.get("description", "")[:30] + "..."
                    if team.get("description") and len(team.get("description", "")) > 30
                    else team.get("description", "")
                )
                team_table.add_row(
                    team.get("id", ""),
                    team.get("name", ""),
                    team.get("coordination_strategy", ""),
                    agents,
                    desc,
                )

            print_table(team_table)
            success(f"Found {len(teams)} team(s)")

    except Exception as e:
        error(f"Error listing teams: {e}")


@cli.command()
@click.argument("name")
@click.option(
    "--format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
def show(name, format):
    """Show details of a specific team."""
    try:
        team = team_storage.get_team(name)

        if not team:
            error(f"Team '{name}' not found")
            return

        if format == "json":
            click.echo(json.dumps(team, indent=2))
        elif format == "yaml":
            click.echo(yaml.dump(team, default_flow_style=False))
        else:
            # Table format - show as key-value pairs
            team_info = {
                "ID": team.get("id", ""),
                "Name": team.get("name", ""),
                "Strategy": team.get("coordination_strategy", ""),
            }

            if team.get("description"):
                team_info["Description"] = team["description"]

            if team.get("agents"):
                team_info["Agents"] = ", ".join(team["agents"])

            if team.get("created_at"):
                team_info["Created"] = team["created_at"]

            key_value(team_info, f"Team: {name}")

    except Exception as e:
        error(f"Error showing team: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete a team."""
    try:
        # Check if team exists
        team = team_storage.get_team(name)
        if not team:
            error(f"Team '{name}' not found")
            return

        if not force:
            click.echo(f"⚠ This will permanently delete team '{name}'.")
            if not click.confirm("Do you want to continue?"):
                click.echo("Operation cancelled.")
                return

        if team_storage.delete_team(name):
            success(f"Team '{name}' deleted successfully")
        else:
            error(f"Failed to delete team '{name}'")

    except Exception as e:
        error(f"Error deleting team: {e}")
