# Engine CLI

[![PyPI version](https://badge.fury.io/py/engine-cli.svg)](https://pypi.org/project/engine-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/engine-cli.svg)](https://pypi.org/project/engine-cli/)
[![License](https://img.shields.io/badge/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Tests](https://github.com/engine-agi/engine-cli/actions/workflows/tests.yml/badge.svg)](https://github.com/engine-agi/engine-cli/actions)

**Engine Framework CLI** - Command Line Interface for AI Agent Orchestration System

A powerful terminal interface for managing AI agents, teams, workflows, and orchestration systems. Built on top of the Engine Core framework with rich terminal UI and comprehensive command coverage.

## ✨ Features

- **🧠 Agent Management**: Create, configure, and manage AI agents from command line
- **👥 Team Coordination**: Build and manage agent teams with advanced coordination strategies
- **⚡ Workflow Execution**: Run Pregel-based workflows with real-time monitoring
- **🔧 Tool Integration**: Manage external integrations (APIs, CLI tools, MCP)
- **📋 Protocol System**: Configure agent behavior protocols and commands
- **📚 Memory Management**: Hierarchical memory system with semantic search
- **🎨 Rich Terminal UI**: Beautiful, interactive command-line interface with colors and tables
- **🚀 Production Ready**: Comprehensive error handling and validation

## 📦 Installation

### 🚀 Quick Install (Recommended)

```bash
pip install engine-cli
```

**That's it!** Engine CLI v1.0.0 is now available on PyPI and ready to use.

### 📋 Requirements

- **Python**: 3.11 or higher
- **Engine Core**: Automatically installed as dependency
- **Optional**: Rich terminal for enhanced UI (automatically included)

### 🔧 Alternative Installation Methods

```bash
# From source (development)
git clone https://github.com/engine-agi/engine-cli.git
cd engine-cli
pip install -e .

# With development dependencies
pip install -e ".[dev]"
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

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

### 📋 Dual Licensing

**Engine Framework** uses a dual licensing model:

- **AGPL-3.0**: For open-source usage, community contributions, and non-commercial projects
- **Commercial License**: For enterprise deployments, proprietary integrations, and commercial products

### 📞 Commercial Licensing

For commercial usage or if you need a different license:
- Contact: [licensing@engine-framework.com](mailto:licensing@engine-framework.com)
- Enterprise features and support available
- Custom deployment options

See the [LICENSE](LICENSE) file and [LICENSE-COMMERCIAL](LICENSE-COMMERCIAL) for details.