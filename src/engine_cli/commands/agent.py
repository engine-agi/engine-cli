"""Agent management commands."""
import click
from typing import Optional, List
from datetime import datetime
import os
import yaml
import json

# Import Rich formatting
from engine_cli.formatting import success, error, header, key_value, table, print_table

# Import new Book-based storage
from engine_cli.storage.agent_book_storage import AgentBookStorage


class AgentStorage:
    """Simple agent storage manager."""
    
    def __init__(self):
        self.agents_dir = os.path.join(os.getcwd(), "agents")
        os.makedirs(self.agents_dir, exist_ok=True)
    
    def list_agents(self) -> List[dict]:
        """List all saved agents."""
        agents = []
        if os.path.exists(self.agents_dir):
            for file in os.listdir(self.agents_dir):
                if file.endswith('.yaml'):
                    try:
                        with open(os.path.join(self.agents_dir, file), 'r') as f:
                            agent_data = yaml.safe_load(f)
                            if agent_data:
                                agents.append(agent_data)
                    except Exception:
                        continue
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get agent by ID."""
        agent_file = os.path.join(self.agents_dir, f"{agent_id}.yaml")
        if os.path.exists(agent_file):
            try:
                with open(agent_file, 'r') as f:
                    return yaml.safe_load(f)
            except Exception:
                return None
        return None
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete agent by ID."""
        agent_file = os.path.join(self.agents_dir, f"{agent_id}.yaml")
        if os.path.exists(agent_file):
            try:
                os.remove(agent_file)
                return True
            except Exception:
                return False
        return False


# Global storage instances
agent_storage = AgentStorage()  # Legacy storage for backward compatibility
agent_book_storage = AgentBookStorage()  # New Book-based storage


@click.group()
def cli():
    """Manage AI agents."""
    pass


@cli.command()
@click.argument("name")
@click.option("--model", default="claude-3.5-sonnet", help="AI model to use")
@click.option("--speciality", help="Agent speciality")
@click.option("--persona", help="Agent behavioral characteristics")
@click.option("--stack", help="Technology stack (comma-separated)")
@click.option("--tools", multiple=True, help="Available tools (can be used multiple times)")
@click.option("--protocol", help="Agent protocol ID")
@click.option("--workflow", help="Agent workflow ID")
@click.option("--book", help="Agent memory book ID")
@click.option("--save", is_flag=True, help="Save agent to storage")
@click.option("--output", type=click.Path(), help="Output file for agent configuration")
def create(name, model, speciality, persona, stack, tools, protocol, workflow, book, save, output):
    """Create a new AI agent with all 11 configurable modules."""
    try:
        from engine_core import AgentBuilder

        builder = AgentBuilder()
        builder = builder.with_id(name)
        builder = builder.with_name(name)
        builder = builder.with_model(model)

        if speciality:
            builder = builder.with_speciality(speciality)

        if persona:
            builder = builder.with_persona(persona)

        if stack:
            # Split by comma and strip whitespace
            stack_list = [s.strip() for s in stack.split(',')]
            builder = builder.with_stack(stack_list)

        if tools:
            builder = builder.with_tools(list(tools))

        if protocol:
            builder = builder.with_protocol(protocol)

        if workflow:
            builder = builder.with_workflow(workflow)

        if book:
            builder = builder.with_book(book)

        agent = builder.build()

        success(f"Agent '{name}' created successfully!")

        # Display agent details
        agent_info = {
            "ID": agent.id,
            "Name": agent.name or name,
            "Model": agent.model,
        }

        if agent.speciality:
            agent_info["Speciality"] = agent.speciality

        if agent.persona:
            agent_info["Persona"] = agent.persona

        if agent.stack:
            agent_info["Stack"] = ', '.join(agent.stack)

        if agent.tools:
            agent_info["Tools"] = ', '.join(agent.tools)

        if agent.protocol:
            agent_info["Protocol"] = agent.protocol

        if agent.workflow:
            agent_info["Workflow"] = agent.workflow

        if agent.book:
            agent_info["Book"] = agent.book

        key_value(agent_info, "Agent Details")

        # Save agent if requested
        if save or output:
            agent_data = {
                "id": agent.id,
                "name": agent.name,
                "model": agent.model,
                "speciality": agent.speciality,
                "persona": agent.persona,
                "stack": agent.stack,
                "tools": agent.tools,
                "protocol": agent.protocol,
                "workflow": agent.workflow,
                "book": agent.book,
                "created_at": str(datetime.now())
            }

            if output:
                # Use legacy YAML format for custom output path
                import yaml
                output_path = output
                with open(output_path, 'w') as f:
                    yaml.dump(agent_data, f, default_flow_style=False)
                success(f"Agent configuration saved to: {output_path}")
            else:
                # Use new Book-based storage
                if agent_book_storage.save_agent(agent_data):
                    success(f"Agent '{name}' saved using Book system")
                else:
                    error("Failed to save agent using Book system")

    except ImportError:
        error("Engine Core not available. Please install engine-core first.")
    except Exception as e:
        error(f"Error creating agent: {e}")


@cli.command()
@click.option("--format", type=click.Choice(['table', 'json', 'yaml']), default='table', help="Output format")
def list(format):
    """List all saved agents."""
    try:
        # Try new Book-based storage first
        agents = agent_book_storage.list_agents()

        # If no agents found in Book storage, try legacy storage
        if not agents:
            agents = agent_storage.list_agents()

        if not agents:
            click.echo("No agents found. Create one with: engine agent create <name>")
            return

        if format == 'json':
            click.echo(json.dumps(agents, indent=2))
        elif format == 'yaml':
            click.echo(yaml.dump(agents, default_flow_style=False))
        else:
            # Table format
            from engine_cli.formatting import table, print_table
            agent_table = table("Agents", ["ID", "Name", "Model", "Speciality", "Stack"])

            for agent in agents:
                stack = ', '.join(agent.get('stack', [])) if agent.get('stack') else ''
                agent_table.add_row(
                    agent.get('id', ''),
                    agent.get('name', ''),
                    agent.get('model', ''),
                    agent.get('speciality', ''),
                    stack
                )

            print_table(agent_table)
            success(f"Found {len(agents)} agent(s)")

    except Exception as e:
        error(f"Error listing agents: {e}")


@cli.command()
@click.argument("name")
@click.option("--format", type=click.Choice(['table', 'json', 'yaml']), default='table', help="Output format")
def show(name, format):
    """Show details of a specific agent."""
    try:
        # Try new Book-based storage first
        agent = agent_book_storage.get_agent(name)

        # If not found, try legacy storage
        if not agent:
            agent = agent_storage.get_agent(name)

        if not agent:
            error(f"Agent '{name}' not found")
            import sys
            sys.exit(1)

        if format == 'json':
            click.echo(json.dumps(agent, indent=2))
        elif format == 'yaml':
            click.echo(yaml.dump(agent, default_flow_style=False))
        else:
            # Table format - show as key-value pairs
            agent_info = {
                "ID": agent.get('id', ''),
                "Name": agent.get('name', ''),
                "Model": agent.get('model', ''),
            }
            
            if agent.get('speciality'):
                agent_info["Speciality"] = agent['speciality']
            
            if agent.get('persona'):
                agent_info["Persona"] = agent['persona']
            
            if agent.get('stack'):
                agent_info["Stack"] = ', '.join(agent['stack'])
            
            if agent.get('tools'):
                agent_info["Tools"] = ', '.join(agent['tools'])
            
            if agent.get('protocol'):
                agent_info["Protocol"] = agent['protocol']
            
            if agent.get('workflow'):
                agent_info["Workflow"] = agent['workflow']
            
            if agent.get('book'):
                agent_info["Book"] = agent['book']
            
            if agent.get('created_at'):
                agent_info["Created"] = agent['created_at']
            
            key_value(agent_info, f"Agent: {name}")

    except Exception as e:
        error(f"Error showing agent: {e}")


@cli.command()
@click.argument("name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(name, force):
    """Delete an agent."""
    try:
        # Check if agent exists (try both storages)
        agent = agent_book_storage.get_agent(name) or agent_storage.get_agent(name)
        if not agent:
            error(f"Agent '{name}' not found")
            import sys
            sys.exit(1)

        if not force:
            click.echo(f"⚠ This will permanently delete agent '{name}'.")
            if not click.confirm("Do you want to continue?"):
                click.echo("Operation cancelled.")
                return

        # Try to delete from Book storage first, then legacy storage
        deleted = agent_book_storage.delete_agent(name) or agent_storage.delete_agent(name)

        if deleted:
            success(f"Agent '{name}' deleted successfully")
        else:
            error(f"Failed to delete agent '{name}'")

    except Exception as e:
        error(f"Error deleting agent: {e}")
@click.command()
@click.argument("name")
@click.argument("task")
@click.option("--async", "async_exec", is_flag=True, help="Execute asynchronously")
def execute(name, task, async_exec):
    """Execute a task with a specific agent."""
    try:
        # Load agent from storage (try Book storage first)
        agent_data = agent_book_storage.get_agent(name) or agent_storage.get_agent(name)
        if not agent_data:
            error(f"Agent '{name}' not found")
            return

        # Rebuild agent from stored data
        from engine_core import AgentBuilder
        
        builder = AgentBuilder()
        builder = builder.with_id(agent_data['id'])
        if agent_data.get('name'):
            builder = builder.with_name(agent_data['name'])
        builder = builder.with_model(agent_data.get('model', 'claude-3.5-sonnet'))
        
        if agent_data.get('speciality'):
            builder = builder.with_speciality(agent_data['speciality'])
        
        if agent_data.get('persona'):
            builder = builder.with_persona(agent_data['persona'])
        
        if agent_data.get('stack'):
            builder = builder.with_stack(agent_data['stack'])
        
        if agent_data.get('tools'):
            builder = builder.with_tools(agent_data['tools'])
        
        if agent_data.get('protocol'):
            builder = builder.with_protocol(agent_data['protocol'])
        
        if agent_data.get('workflow'):
            builder = builder.with_workflow(agent_data['workflow'])
        
        if agent_data.get('book'):
            builder = builder.with_book(agent_data['book'])
        
        agent = builder.build()
        
        # Execute task
        import asyncio
        
        async def run_task():
            click.echo(f"🤖 Executing task with agent '{name}'...")
            result = await agent.execute(task)
            
            duration = (result.end_time - result.start_time).total_seconds() if result.end_time else 0
            click.echo(f"✅ Task completed in {duration:.2f}s")
            click.echo(f"📄 Response: {result.messages[-1].content if result.messages else 'No response'}")
            
            return result
        
        if async_exec:
            # Run in background (this is simplified - in real implementation would use proper async handling)
            import threading
            
            def run_async():
                asyncio.run(run_task())
            
            thread = threading.Thread(target=run_async)
            thread.start()
            success(f"Task started asynchronously with agent '{name}'")
        else:
            # Run synchronously
            asyncio.run(run_task())
            
    except ImportError:
        error("Engine Core not available. Please install engine-core first.")
    except Exception as e:
        error(f"Error executing task: {e}")
