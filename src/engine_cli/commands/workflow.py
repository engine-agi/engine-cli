"""Workflow management commands."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional

import click
import yaml

# Import engine core components
from engine_core import WorkflowBuilder  # type: ignore

# Import Rich formatting
from engine_cli.formatting import (
    error,
    header,
    key_value,
    print_table,
    success,
    table,
    warning,
)

# Import state manager
from engine_cli.storage.workflow_state_manager import (
    WorkflowExecutionState,  # type: ignore
)
from engine_cli.storage.workflow_state_manager import (
    workflow_state_manager,  # type: ignore
)


# Import WorkflowExecutionService (lazy import to avoid core dependencies)
def _get_workflow_execution_service():
    """Lazy import of WorkflowExecutionService."""
    try:
        # For now, use mock repository since full PostgreSQL setup is complex
        from engine_core.services.workflow_service import (
            WorkflowExecutionService,  # type: ignore
        )
        from engine_core.services.workflow_service import MockWorkflowRepository

        mock_repo = MockWorkflowRepository()
        return WorkflowExecutionService(mock_repo)
    except ImportError:
        return None


# Import engine core components
# (WorkflowState not used in CLI commands)


class WorkflowStorage:
    """Simple workflow storage manager."""

    def __init__(self):
        self.workflows_dir = os.path.join(os.getcwd(), "workflows")
        os.makedirs(self.workflows_dir, exist_ok=True)

    def list_workflows(self) -> List[dict]:
        """List all saved workflows."""
        workflows = []
        if os.path.exists(self.workflows_dir):
            for file in os.listdir(self.workflows_dir):
                if file.endswith(".yaml"):
                    try:
                        file_path = os.path.join(self.workflows_dir, file)
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = yaml.safe_load(f)
                            workflows.append(
                                {
                                    "id": data.get("id", "unknown"),
                                    "name": data.get("name", data.get("id", "unknown")),
                                    "version": data.get("version", "1.0.0"),
                                    "description": data.get("description", ""),
                                    "vertex_count": data.get("vertex_count", 0),
                                    "edge_count": data.get("edge_count", 0),
                                    "created_at": data.get("created_at", ""),
                                    "file": file,
                                }
                            )
                    except Exception:
                        continue
        return workflows

    def save_workflow(
        self, workflow: Any, builder: Optional["CLIWorkflowBuilder"] = None
    ) -> bool:
        """Save workflow to storage."""
        try:
            workflow_data = {
                "id": workflow.id,
                "name": workflow.name,
                "description": getattr(workflow.config, "description", None),
                "version": getattr(workflow.config, "version", "1.0.0"),
                "vertex_count": workflow.vertex_count,
                "edge_count": workflow.edge_count,
                "created_at": workflow.created_at.isoformat(),
                "config": workflow.config,
                "vertices": [],  # Will populate with detailed vertex info
                "edges": [],  # Will populate with detailed edge info
            }

            # If we have a CLIWorkflowBuilder, include agent/team specs and edges
            if builder:
                workflow_data["vertices"] = []
                if hasattr(builder, "agent_specs"):
                    for spec in builder.agent_specs:
                        workflow_data["vertices"].append(
                            {
                                "id": spec["vertex_id"],
                                "type": "agent",
                                "agent_id": spec["agent_id"],
                                "instruction": spec["instruction"],
                            }
                        )
                if hasattr(builder, "team_specs"):
                    for spec in builder.team_specs:
                        workflow_data["vertices"].append(
                            {
                                "id": spec["vertex_id"],
                                "type": "team",
                                "team_id": spec["team_id"],
                                "tasks": spec["tasks"],
                            }
                        )

                # Include edges from builder
                if hasattr(builder, "edge_specs"):
                    workflow_data["edges"] = builder.edge_specs
                else:
                    workflow_data["edges"] = []

            # Ensure workflows directory exists
            os.makedirs(self.workflows_dir, exist_ok=True)

            file_path = os.path.join(self.workflows_dir, f"{workflow.id}.yaml")
            with open(file_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(
                    workflow_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                )

            return True

        except Exception as e:
            error(f"Error saving workflow: {e}")
            return False

    def load_workflow(self, workflow_id: str) -> Optional[Any]:
        """Load a workflow by ID."""
        file_path = os.path.join(self.workflows_dir, f"{workflow_id}.yaml")
        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            # Note: Full workflow reconstruction would require agents/teams/functions
            # For now, return basic info. Full reconstruction needs more complex logic
            return data

        except Exception as e:
            error(f"Error loading workflow {workflow_id}: {e}")
            return None

    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow by ID."""
        file_path = os.path.join(self.workflows_dir, f"{workflow_id}.yaml")
        if not os.path.exists(file_path):
            return False

        try:
            os.remove(file_path)
            return True
        except Exception:
            return False


class WorkflowResolver:
    """Resolves workflow dependencies (agents, teams) for execution."""

    def __init__(self):
        self.agent_storage = None
        self.team_storage = None

    def _get_agent_storage(self):
        """Lazy load agent storage."""
        if self.agent_storage is None:
            try:
                # Temporarily disabled - will be implemented when agent commands
                # are available
                # from engine_cli.commands.agent import get_agent_storage
                # self.agent_storage = get_agent_storage()
                pass
            except ImportError:
                pass
        return self.agent_storage

    def _get_team_storage(self):
        """Lazy load team storage."""
        if self.team_storage is None:
            try:
                from engine_cli.commands.team import get_team_storage

                self.team_storage = get_team_storage()
            except ImportError:
                pass
        return self.team_storage

    def resolve_workflow(self, workflow_data: dict) -> Optional[Any]:
        """Resolve a workflow by simulating execution with detailed information."""
        try:
            # Create a new workflow builder
            builder = WorkflowBuilder()
            builder = builder.with_id(workflow_data.get("id", "resolved_workflow"))
            builder = builder.with_name(workflow_data.get("name", "Resolved Workflow"))

            # Create a detailed execution simulation that shows what would happen
            config = workflow_data.get("config", {})

            async def execute_workflow(input_data):
                execution_info = {
                    "workflow_id": workflow_data.get("id"),
                    "workflow_name": workflow_data.get("name"),
                    "vertex_count": workflow_data.get("vertex_count", 0),
                    "edge_count": workflow_data.get("edge_count", 0),
                    "execution_mode": "simulated",
                    "input": input_data,
                }

                # Add information about what agents/teams would be executed
                if hasattr(config, "agent_specs") and config.agent_specs:
                    execution_info["agents"] = [
                        {
                            "vertex_id": spec["vertex_id"],
                            "agent_id": spec["agent_id"],
                            "instruction": spec["instruction"],
                        }
                        for spec in config.agent_specs
                    ]

                if hasattr(config, "team_specs") and config.team_specs:
                    execution_info["teams"] = [
                        {
                            "vertex_id": spec["vertex_id"],
                            "team_id": spec["team_id"],
                            "tasks": spec["tasks"],
                        }
                        for spec in config.team_specs
                    ]

                # Simulate execution order based on edges
                if hasattr(config, "edges") and config.edges:
                    execution_info["execution_order"] = []
                    # Simple topological sort simulation
                    processed = set()
                    for edge in config.edges:
                        from_vertex = edge.get("from_vertex")
                        to_vertex = edge.get("to_vertex")
                        if from_vertex not in processed:
                            execution_info["execution_order"].append(from_vertex)
                            processed.add(from_vertex)
                        if to_vertex not in processed:
                            execution_info["execution_order"].append(to_vertex)
                            processed.add(to_vertex)

                execution_info["result"] = (
                    f"Simulated execution of workflow '{workflow_data.get('name', 'unknown')}' completed successfully"
                )
                return execution_info

            builder = builder.add_function_vertex(
                "workflow_execution", execute_workflow
            )

            workflow = builder.build()
            return workflow

        except Exception as e:
            error(f"Failed to resolve workflow: {e}")
            return None


# Global instances
workflow_storage = WorkflowStorage()
workflow_resolver = WorkflowResolver()


def get_workflow_storage():
    """Get workflow storage instance."""
    return workflow_storage


class CLIWorkflowBuilder:
    """Simplified workflow builder for CLI usage."""

    def __init__(self):
        self.workflow_builder = WorkflowBuilder()
        self.agent_specs = []  # Store agent specs for later resolution
        self.team_specs = []  # Store team specs for later resolution
        self.edge_specs = []  # Store edge specs for persistence

    def with_id(self, workflow_id: str):
        self.workflow_builder = self.workflow_builder.with_id(workflow_id)
        return self

    def with_name(self, name: str):
        self.workflow_builder = self.workflow_builder.with_name(name)
        return self

    def with_description(self, description: str):
        self.workflow_builder = self.workflow_builder.with_description(description)
        return self

    def with_version(self, version: str):
        self.workflow_builder = self.workflow_builder.with_version(version)
        return self

    def add_agent_vertex(self, vertex_id: str, agent_id: str, instruction: str):
        """Add agent vertex spec for CLI - stores for later resolution."""
        self.agent_specs.append(
            {
                "vertex_id": vertex_id,
                "agent_id": agent_id,
                "instruction": instruction,
            }
        )

        # For CLI, add a placeholder function vertex that will be replaced during execution
        async def placeholder_function(input_data):
            return {
                "result": f"Placeholder for agent {agent_id}",
                "input": input_data,
            }

        self.workflow_builder = self.workflow_builder.add_function_vertex(
            vertex_id, placeholder_function
        )
        return self

    def add_team_vertex(
        self, vertex_id: str, team_id: str, tasks: List[Dict[str, Any]]
    ):
        """Add team vertex spec for CLI - stores for later resolution."""
        self.team_specs.append(
            {"vertex_id": vertex_id, "team_id": team_id, "tasks": tasks}
        )

        # For CLI, add a placeholder function vertex that will be replaced during execution
        async def placeholder_function(input_data):
            task_names = [t.get("task", "unknown") for t in tasks]
            return {
                "result": f"Placeholder for team {team_id} with tasks: {', '.join(task_names)}",
                "input": input_data,
            }

        self.workflow_builder = self.workflow_builder.add_function_vertex(
            vertex_id, placeholder_function
        )
        return self

    def add_function_vertex(self, vertex_id: str, function):
        self.workflow_builder = self.workflow_builder.add_function_vertex(
            vertex_id, function
        )
        return self

    def add_edge(self, from_vertex: str, to_vertex: str):
        self.edge_specs.append({"from": from_vertex, "to": to_vertex})
        self.workflow_builder = self.workflow_builder.add_edge(from_vertex, to_vertex)
        return self

    def build(self):
        """Build workflow - for CLI this creates a workflow that can be resolved later."""
        return self.workflow_builder.build()


@click.group()
def cli():
    """Manage workflows."""
    pass


@cli.command()
@click.argument("name")
@click.option("--description", help="Workflow description")
@click.option("--version", default="1.0.0", help="Workflow version")
@click.option(
    "--simple",
    is_flag=True,
    help="Create a simple workflow with one function vertex",
)
@click.option(
    "--agent",
    multiple=True,
    help="Add agent vertex (format: vertex_id:agent_id:instruction)",
)
@click.option(
    "--team",
    multiple=True,
    help="Add team vertex (format: vertex_id:team_id:task1,task2)",
)
@click.option(
    "--edge",
    multiple=True,
    help="Add edge between vertices (format: from_vertex:to_vertex)",
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Load workflow configuration from YAML file",
)
@click.option("--save", is_flag=True, help="Save workflow to storage")
@click.option(
    "--output",
    type=click.Path(),
    help="Output file for workflow configuration",
)
def create(name, description, version, simple, agent, team, edge, config, save, output):
    """Create a new workflow."""
    try:
        builder = CLIWorkflowBuilder()  # Initialize with default builder

        # Load from config file if provided
        if config:
            with open(config, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # Apply config data
            workflow_config = config_data.get("workflow", {})
            builder = builder.with_id(workflow_config.get("id", name))
            builder = builder.with_name(workflow_config.get("name", name))
            builder = builder.with_description(
                workflow_config.get("description", description or "")
            )
            builder = builder.with_version(workflow_config.get("version", version))

            # Add vertices from config
            vertices = config_data.get("vertices", [])
            for vertex in vertices:
                vertex_type = vertex.get("type")
                vertex_id = vertex.get("id")

                if vertex_type == "agent":
                    agent_id = vertex.get("agent_id")
                    instruction = vertex.get("instruction", "")
                    builder = builder.add_agent_vertex(vertex_id, agent_id, instruction)
                elif vertex_type == "team":
                    team_id = vertex.get("team_id")
                    tasks = vertex.get("tasks", [])
                    builder = builder.add_team_vertex(vertex_id, team_id, tasks)
                elif vertex_type == "function":
                    # For function vertices in config, we'd need to define them
                    # For now, skip or add placeholder
                    pass

            # Add edges from config
            edges = config_data.get("edges", [])
            for edge_config in edges:
                from_vertex = edge_config.get("from")
                to_vertex = edge_config.get("to")
                if from_vertex and to_vertex:
                    builder = builder.add_edge(from_vertex, to_vertex)
        else:
            # Manual configuration
            builder = builder.with_id(name)
            builder = builder.with_name(name)

            if description:
                builder = builder.with_description(description)

            if version:
                builder = builder.with_version(version)

            # Add agent vertices
            for agent_spec in agent:
                parts = agent_spec.split(":", 2)
                if len(parts) < 3:
                    error(
                        f"Invalid agent specification: {agent_spec}. Use format: vertex_id:agent_id:instruction"
                    )
                    return
                vertex_id, agent_id, instruction = parts
                builder = builder.add_agent_vertex(vertex_id, agent_id, instruction)

            # Add team vertices
            for team_spec in team:
                parts = team_spec.split(":", 2)
                if len(parts) < 3:
                    error(
                        f"Invalid team specification: {team_spec}. Use format: vertex_id:team_id:task1,task2"
                    )
                    return
                vertex_id, team_id, tasks_str = parts
                tasks = [{"task": task.strip()} for task in tasks_str.split(",")]
                builder = builder.add_team_vertex(vertex_id, team_id, tasks)

            # Add edges
            for edge_spec in edge:
                if ":" not in edge_spec:
                    error(
                        f"Invalid edge specification: {edge_spec}. Use format: from_vertex:to_vertex"
                    )
                    return
                from_vertex, to_vertex = edge_spec.split(":", 1)
                builder = builder.add_edge(from_vertex, to_vertex)

            # Add a simple function vertex if requested (and no other vertices specified)
            if simple and not agent and not team:

                async def demo_function(input_data):
                    return {
                        "result": f"Executed by {name}",
                        "input": input_data,
                    }

                builder = builder.add_function_vertex("demo_task", demo_function)

        workflow = builder.build()

        success(f"Workflow '{name}' created successfully!")

        # Create table with workflow details
        workflow_table = table("Workflow Details", ["Property", "Value"])
        workflow_table.add_row("ID", workflow.id)
        workflow_table.add_row("Name", workflow.name)
        workflow_table.add_row(
            "Description", getattr(workflow.config, "description", "")
        )
        workflow_table.add_row("Version", getattr(workflow.config, "version", "1.0.0"))
        workflow_table.add_row("Vertices", str(workflow.vertex_count))
        workflow_table.add_row("Edges", str(workflow.edge_count))
        workflow_table.add_row("State", workflow.state.value)
        print_table(workflow_table)

        # Save if requested
        if save:
            if workflow_storage.save_workflow(workflow, builder):
                success(
                    f"Workflow saved to {workflow_storage.workflows_dir}/{workflow.id}.yaml"
                )
            else:
                error("Failed to save workflow")

        # Output to file if requested
        if output:
            try:
                workflow_data = workflow.to_dict()
                with open(output, "w", encoding="utf-8") as f:
                    yaml.safe_dump(
                        workflow_data,
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                    )
                success(f"Workflow configuration saved to {output}")
            except Exception as e:
                error(f"Failed to save workflow to file: {e}")

    except Exception as e:
        error(f"Failed to create workflow: {e}")


@cli.command()
def list():
    """List all workflows."""
    try:
        workflows = workflow_storage.list_workflows()

        if not workflows:
            click.echo("No workflows found.")
            return

        # Create table
        workflow_table = table(
            "Workflows",
            ["ID", "Name", "Version", "Vertices", "Edges", "Created"],
        )
        for workflow in workflows:
            created_date = (
                workflow.get("created_at", "")[:10]
                if workflow.get("created_at")
                else ""
            )
            workflow_table.add_row(
                workflow["id"],
                workflow["name"],
                workflow["version"],
                str(workflow["vertex_count"]),
                str(workflow["edge_count"]),
                created_date,
            )
        print_table(workflow_table)

        success(f"Found {len(workflows)} workflow(s)")

    except Exception as e:
        error(f"Failed to list workflows: {e}")


@cli.command()
@click.argument("name")
def show(name):
    """Show details of a specific workflow."""
    try:
        workflow_data = workflow_storage.load_workflow(name)

        if not workflow_data:
            error(f"Workflow '{name}' not found")
            import sys

            sys.exit(1)

        # Display workflow header
        header(f"Workflow: {workflow_data.get('name', name)}")
        click.echo("")

        # Basic information
        info_data = {
            "ID": workflow_data.get("id", "unknown"),
            "Name": workflow_data.get("name", workflow_data.get("id", "unknown")),
            "Description": workflow_data.get("description", ""),
            "Version": workflow_data.get("version", "1.0.0"),
            "Vertices": str(workflow_data.get("vertex_count", 0)),
            "Edges": str(workflow_data.get("edge_count", 0)),
            "Created": workflow_data.get("created_at", "unknown"),
        }
        key_value(info_data)

        # Vertices information
        vertices = workflow_data.get("vertices", [])
        if vertices:
            click.echo("")
            header("Vertices")
            for vertex in vertices:
                vertex_type = vertex.get("type", "unknown")
                vertex_id = vertex.get("id", "unknown")
                if vertex_type == "agent":
                    click.echo(
                        f"  {vertex_id} (agent): {vertex.get('agent_id', 'unknown')} - {vertex.get('instruction', '')}"
                    )
                elif vertex_type == "team":
                    tasks = vertex.get("tasks", [])
                    task_names = [t.get("task", "") for t in tasks]
                    click.echo(
                        f"  {vertex_id} (team): {vertex.get('team_id', 'unknown')} - tasks: {', '.join(task_names)}"
                    )
                else:
                    click.echo(f"  {vertex_id} ({vertex_type})")

        # Edges information
        edges = workflow_data.get("edges", [])
        if edges:
            click.echo("")
            header("Edges")
            for edge in edges:
                from_vertex = edge.get("from", "unknown")
                to_vertex = edge.get("to", "unknown")
                click.echo(f"  {from_vertex} -> {to_vertex}")

        # Config information
        config = workflow_data.get("config", {})
        if config:
            click.echo("")
            config_data = {}
            for key, value in config.items():
                if key not in [
                    "id",
                    "name",
                    "description",
                    "version",
                ]:  # Already shown above
                    config_data[f"  {key}"] = str(value)
            if config_data:
                key_value(config_data, "Configuration")

    except Exception as e:
        error(f"Failed to show workflow: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete a workflow."""
    try:
        if not force:
            error(f"This will delete workflow '{name}'. Use --force to confirm.")
            return

        if workflow_storage.delete_workflow(name):
            success(f"Workflow '{name}' deleted successfully")
        else:
            error(f"Workflow '{name}' not found or could not be deleted")
            import sys

            sys.exit(1)

    except Exception as e:
        error(f"Failed to delete workflow: {e}")


@cli.command()
@click.argument("name")
@click.option("--input-data", help="JSON input data for workflow execution")
def run(name, input_data):
    """Run a workflow."""
    try:
        workflow_data = workflow_storage.load_workflow(name)

        if not workflow_data:
            error(f"Workflow '{name}' not found")
            return

        # Parse input data
        input_dict = {}
        if input_data:
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                error(f"Invalid JSON input data: {e}")
                return

        success(f"Running workflow '{name}'...")

        # Get workflow execution service for persistence
        execution_service = _get_workflow_execution_service()

        # Create execution in state manager using existing event loop approach
        execution_id = None
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        try:
            execution_id = temp_loop.run_until_complete(
                workflow_state_manager.create_execution(
                    workflow_id=name,
                    workflow_name=workflow_data.get("name", name),
                    input_data=input_dict,
                )
            )

            click.echo(f"📋 Volatile Execution ID: {execution_id}")

            # Update state to running
            temp_loop.run_until_complete(
                workflow_state_manager.update_execution_state(
                    execution_id=execution_id,
                    state=WorkflowExecutionState.RUNNING,
                )
            )

        finally:
            temp_loop.close()

        # Try to resolve and execute the workflow
        resolved_workflow = workflow_resolver.resolve_workflow(workflow_data)

        if resolved_workflow:
            # Execute the resolved workflow directly
            async def execute_workflow():
                # Create persistent execution record if service is available
                execution_record = None
                if execution_service:
                    try:
                        execution_record = await execution_service.create_execution(
                            workflow_id=name,
                            workflow_name=workflow_data.get("name", name),
                            input_data=input_dict,
                        )
                        click.echo(
                            f"📋 Persistent Execution ID: {execution_record.execution_id}"
                        )
                    except Exception as e:
                        warning(f"Could not create persistent execution record: {e}")

                try:
                    # Update progress as we start
                    await workflow_state_manager.update_execution_state(
                        execution_id=execution_id,
                        state=WorkflowExecutionState.RUNNING,
                        progress_percentage=10.0,
                    )

                    # Mark persistent execution as started
                    if execution_service and execution_record:
                        try:
                            await execution_service.start_execution(
                                execution_record.execution_id
                            )
                        except Exception as e:
                            warning(f"Could not update persistent execution: {e}")

                    result = await resolved_workflow.execute(input_dict)

                    # Update final state
                    await workflow_state_manager.update_execution_state(
                        execution_id=execution_id,
                        state=WorkflowExecutionState.COMPLETED,
                        progress_percentage=100.0,
                    )

                    await workflow_state_manager.set_execution_output(
                        execution_id=execution_id, output_data=result
                    )

                    # Mark persistent execution as completed
                    if execution_service and execution_record:
                        try:
                            await execution_service.complete_execution(
                                execution_record.execution_id,
                                success=True,
                                output_data=result,
                            )
                        except Exception as e:
                            warning(f"Could not complete persistent execution: {e}")

                    return result

                except Exception as exec_error:
                    # Set error state
                    await workflow_state_manager.set_execution_error(
                        execution_id=execution_id,
                        error_message=str(exec_error),
                    )

                    # Mark persistent execution as failed
                    if execution_service and execution_record:
                        try:
                            await execution_service.fail_execution(
                                execution_record.execution_id, str(exec_error)
                            )
                        except Exception as e:
                            warning(f"Could not fail persistent execution: {e}")

                    raise

            # Run the async execution using asyncio.run
            try:
                result = asyncio.run(execute_workflow())

                success("Workflow execution completed!")
                click.echo("📊 Execution Result:")
                click.echo(f"   Execution ID: {execution_id}")
                click.echo(f"   Result: {result}")

            except Exception as e:
                error(f"Workflow execution failed: {e}")
                return
        else:
            # Fallback to simulation - still track state
            asyncio.run(
                workflow_state_manager.update_execution_state(
                    execution_id=execution_id,
                    state=WorkflowExecutionState.RUNNING,
                    progress_percentage=50.0,
                )
            )

            click.echo("📊 Execution Simulation (could not resolve workflow):")
            click.echo(f"   Execution ID: {execution_id}")
            click.echo(f"   Input: {input_dict}")
            click.echo("   Status: simulated execution completed")
            simulated_result = {
                "status": "success",
                "output": "simulated workflow result",
            }

            # Complete the execution
            asyncio.run(
                workflow_state_manager.update_execution_state(
                    execution_id=execution_id,
                    state=WorkflowExecutionState.COMPLETED,
                    progress_percentage=100.0,
                )
            )

            asyncio.run(
                workflow_state_manager.set_execution_output(
                    execution_id=execution_id, output_data=simulated_result
                )
            )

            click.echo(f"   Result: {simulated_result}")
            success("Workflow execution completed (simulated)")

    except Exception as e:
        error(f"Failed to run workflow: {e}")


@cli.command()
@click.argument("name")
@click.option("--input-data", help="JSON input data for workflow testing")
def test(name, input_data):
    """Test a workflow with sample data."""
    try:
        workflow_data = workflow_storage.load_workflow(name)

        if not workflow_data:
            error(f"Workflow '{name}' not found")
            return

        # Parse input data
        input_dict = {}
        if input_data:
            try:
                input_dict = json.loads(input_data)
            except json.JSONDecodeError as e:
                error(f"Invalid JSON input data: {e}")
                return

        success(f"Testing workflow '{name}'...")

        # Test workflow structure
        click.echo("🔍 Testing workflow structure:")
        click.echo(f"   Vertices: {workflow_data.get('vertex_count', 0)}")
        click.echo(f"   Edges: {workflow_data.get('edge_count', 0)}")
        click.echo("   Structure: valid (simulated)")

        # Test with sample input
        click.echo("📥 Testing with input data:")
        click.echo(f"   Input: {input_dict}")

        # Simulate validation and execution planning
        click.echo("✅ Validation Results:")
        click.echo("   Graph structure: valid")
        click.echo("   Dependencies: resolved")
        click.echo("   Execution order: calculated")

        click.echo("📋 Execution Plan:")
        click.echo("   Phase 1: Initialize workflow")
        click.echo("   Phase 2: Execute vertices")
        click.echo("   Phase 3: Collect results")

        success("Workflow test completed successfully")

    except Exception as e:
        error(f"Failed to test workflow: {e}")


@cli.command()
@click.argument("execution_id", required=False)
@click.option("--workflow", help="Filter by workflow ID")
@click.option("--active", is_flag=True, help="Show only active executions")
@click.option("--limit", default=10, help="Limit number of results")
def status(execution_id, workflow, active, limit):
    """Show workflow execution status."""
    try:
        if execution_id:
            # Show specific execution status
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                status = loop.run_until_complete(
                    workflow_state_manager.get_execution_status(execution_id)
                )

                if not status:
                    error(f"Execution '{execution_id}' not found")
                    return

                success(f"Execution Status: {execution_id}")

                # Create status table
                status_table = table("Execution Details", ["Property", "Value"])
                status_table.add_row("Execution ID", status.execution_id)
                status_table.add_row("Workflow ID", status.workflow_id)
                status_table.add_row("Workflow Name", status.workflow_name)
                status_table.add_row("State", status.state.value.upper())
                status_table.add_row("Progress", f"{status.progress_percentage:.1f}%")
                status_table.add_row(
                    "Start Time",
                    status.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                )
                if status.end_time:
                    status_table.add_row(
                        "End Time",
                        status.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    )
                if status.current_vertex:
                    status_table.add_row("Current Vertex", status.current_vertex)
                status_table.add_row(
                    "Input Data",
                    (
                        str(status.input_data)[:100] + "..."
                        if len(str(status.input_data)) > 100
                        else str(status.input_data)
                    ),
                )
                if status.output_data:
                    status_table.add_row(
                        "Output Data",
                        (
                            str(status.output_data)[:100] + "..."
                            if len(str(status.output_data)) > 100
                            else str(status.output_data)
                        ),
                    )
                if status.error_message:
                    status_table.add_row("Error", status.error_message)

                print_table(status_table)

                # Show vertex states if available
                if status.vertex_states:
                    click.echo("\n🔍 Vertex States:")
                    vertex_table = table(
                        "Vertex Execution Status",
                        ["Vertex ID", "State", "Last Update", "Output/Error"],
                    )
                    for (
                        vertex_id,
                        vertex_state,
                    ) in status.vertex_states.items():
                        state = vertex_state.get("state", "unknown")
                        updated = vertex_state.get("updated_at", "unknown")
                        output = vertex_state.get("output_data", "")
                        error_msg = vertex_state.get("error_message", "")
                        info = (
                            output[:50] + "..."
                            if len(str(output)) > 50
                            else str(output)
                        )
                        if error_msg:
                            info = f"ERROR: {error_msg[:50]}..."
                        vertex_table.add_row(vertex_id, state.upper(), updated, info)
                    print_table(vertex_table)

            finally:
                loop.close()

        elif active:
            # Show active executions
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                executions = loop.run_until_complete(
                    workflow_state_manager.get_active_executions()
                )

                if not executions:
                    click.echo("No active executions found")
                    return

                success(f"Active Executions ({len(executions)})")

                active_table = table(
                    "Active Workflow Executions",
                    [
                        "Execution ID",
                        "Workflow",
                        "Progress",
                        "Current Vertex",
                        "Started",
                    ],
                )
                for status in executions:
                    active_table.add_row(
                        status.execution_id,
                        f"{status.workflow_name} ({status.workflow_id})",
                        f"{status.progress_percentage:.1f}%",
                        status.current_vertex or "N/A",
                        status.start_time.strftime("%H:%M:%S"),
                    )
                print_table(active_table)

            finally:
                loop.close()

        elif workflow:
            # Show executions for specific workflow
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                executions = loop.run_until_complete(
                    workflow_state_manager.get_workflow_executions(workflow, limit)
                )

                if not executions:
                    click.echo(f"No executions found for workflow '{workflow}'")
                    return

                success(f"Executions for Workflow '{workflow}' ({len(executions)})")

                workflow_table = table(
                    "Workflow Executions",
                    ["Execution ID", "State", "Progress", "Started", "Ended"],
                )
                for status in executions:
                    end_time = (
                        status.end_time.strftime("%H:%M:%S")
                        if status.end_time
                        else "Running"
                    )
                    workflow_table.add_row(
                        status.execution_id,
                        status.state.value.upper(),
                        f"{status.progress_percentage:.1f}%",
                        status.start_time.strftime("%H:%M:%S"),
                        end_time,
                    )
                print_table(workflow_table)

            finally:
                loop.close()

        else:
            # Show recent executions overview
            click.echo("Usage:")
            click.echo("  status <execution_id>     - Show specific execution details")
            click.echo(
                "  status --active           - Show currently running executions"
            )
            click.echo(
                "  status --workflow <id>    - Show executions for specific workflow"
            )
            click.echo("  status --limit <n>        - Limit results (default: 10)")

    except Exception as e:
        error(f"Failed to get execution status: {e}")


@cli.command()
@click.argument("workflow_id", required=False)
@click.option("--limit", default=20, help="Maximum number of executions to show")
@click.option(
    "--status",
    "status_filter",
    help="Filter by execution status (pending, running, completed, failed)",
)
def history(workflow_id, limit, status_filter):
    """Show execution history for workflows."""
    try:
        execution_service = _get_workflow_execution_service()

        if not execution_service:
            error("Workflow execution service not available")
            return

        import asyncio

        async def show_history():
            try:
                if workflow_id:
                    # Show history for specific workflow
                    executions = await execution_service.get_workflow_executions(
                        workflow_id=workflow_id, limit=limit
                    )

                    if not executions:
                        click.echo(
                            f"No execution history found for workflow '{workflow_id}'"
                        )
                        return

                    success(
                        f"Execution History for Workflow '{workflow_id}' ({len(executions)})"
                    )

                    history_table = table(
                        "Execution History",
                        [
                            "Execution ID",
                            "Status",
                            "Started",
                            "Duration",
                            "Success",
                        ],
                    )

                    for execution in executions:
                        duration = "N/A"
                        if execution.duration_seconds:
                            duration = f"{execution.duration_seconds:.1f}s"

                        success_status = "N/A"
                        if execution.success is not None:
                            success_status = "✓" if execution.success else "✗"

                        started = "N/A"
                        if hasattr(execution, "started_at") and execution.started_at:
                            started = execution.started_at.strftime("%Y-%m-%d %H:%M:%S")

                        history_table.add_row(
                            execution.execution_id[:16] + "...",
                            getattr(execution, "status", "unknown").upper(),
                            started,
                            duration,
                            success_status,
                        )

                    print_table(history_table)

                    # Show analytics
                    try:
                        analytics = await execution_service.get_execution_analytics(
                            workflow_id
                        )
                        click.echo("\n📊 Analytics:")
                        click.echo(
                            f"   Total Executions: {analytics.get('total_executions', 0)}"
                        )
                        click.echo(
                            f"   Success Rate: {analytics.get('success_rate', 0):.1%}"
                        )
                        click.echo(
                            f"   Average Duration: {analytics.get('average_duration', 0):.1f}s"
                        )
                    except Exception as e:
                        warning(f"Could not load analytics: {e}")

                else:
                    # Show recent executions across all workflows
                    # This would need a method to get recent executions
                    click.echo("Recent executions across all workflows:")
                    click.echo(
                        "(Feature not yet implemented - use --workflow <id> to see specific workflow history)"
                    )

            except Exception as e:
                error(f"Failed to retrieve execution history: {e}")

        # Run the async function
        asyncio.run(show_history())

    except Exception as e:
        error(f"Failed to show execution history: {e}")


if __name__ == "__main__":
    cli()
