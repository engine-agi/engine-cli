# Engine CLI

Command Line Interface for the Engine Framework - AI Agent Orchestration System.

## Installation

```bash
pip install engine-cli
```

## Usage

```bash
# Show help
engine --help

# Create a new agent
engine agent create --name "my-agent" --model "claude-3.5-sonnet"

# List all agents
engine agent list

# Create a team
engine team create --name "dev-team" --leader "agent-1"

# Start a workflow
engine workflow run --id "workflow-1"
```

## Features

- **Agent Management**: Create, configure, and manage AI agents
- **Team Coordination**: Build and manage agent teams with different coordination strategies
- **Workflow Execution**: Run Pregel-based workflows with real-time monitoring
- **Tool Integration**: Manage external tool integrations (APIs, CLI tools, MCP)
- **Protocol System**: Configure agent behavior protocols
- **Memory System**: Manage hierarchical memory with semantic search
- **Rich Terminal UI**: Beautiful, interactive command-line interface

## Development

This package depends on `engine-core` for the core framework functionality.

```bash
# Install in development mode
poetry install

# Run tests
poetry run pytest

# Build package
poetry build
```

## License

MIT License - see LICENSE file for details.