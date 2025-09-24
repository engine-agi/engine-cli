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
- **⚡ Performance Optimized**: < 2s startup time with lazy loading and smart caching

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

## 📚 Documentation

### 📖 Complete CLI Manual
For comprehensive documentation including all commands, examples, and troubleshooting:

- **[Documentation Index](docs/index.md)** - Complete documentation overview and navigation
- **[CLI Manual](docs/README.md)** - Complete command reference with examples
- **[Practical Examples](docs/examples.md)** - Real-world usage scenarios and tutorials
- **[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- **[Unix Man Pages](../../docs/man/)** - Traditional Unix manual pages (`man engine`)
- **[Interactive Help](#usage)** - Built-in help system (`engine --help`)
- **[Examples Repository](../../engine-examples/)** - Practical usage examples

### 🚀 Quick Examples

```bash
# Get started quickly
engine --help

# Create and manage agents
engine agent create --name "code-reviewer" --model "claude-3.5-sonnet"
engine agent list

# Work with teams and workflows
engine team create --name "dev-team"
engine workflow run --id "my-workflow"

# Monitor system status
engine status
engine advanced monitor
```

### 🔧 Troubleshooting

Common issues and solutions:

```bash
# Enable verbose output for debugging
engine --verbose [command]

# Check configuration
engine config show

# View system status
engine status

# Get detailed help
engine [command] --help
```

For detailed troubleshooting guides, see the **[Troubleshooting Guide](docs/troubleshooting.md)**.

## Features

- **Agent Management**: Create, configure, and manage AI agents
- **Team Coordination**: Build and manage agent teams with different coordination strategies
- **Workflow Execution**: Run Pregel-based workflows with real-time monitoring
- **Tool Integration**: Manage external tool integrations (APIs, CLI tools, MCP)
- **Protocol System**: Configure agent behavior protocols
- **Memory System**: Manage hierarchical memory with semantic search
- **Rich Terminal UI**: Beautiful, interactive command-line interface

## 🛠️ Development

This package depends on `engine-core` for the core framework functionality.

### 📋 Development Setup

```bash
# Clone the repository
git clone https://github.com/engine-agi/engine-cli.git
cd engine-cli

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks (recommended)
pre-commit install
```

### 🔧 Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to ensure code quality and consistency. The following hooks are automatically configured:

- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting with Black profile
- **Trailing Whitespace**: Removes trailing whitespace
- **End of File**: Ensures files end with a newline
- **Large Files**: Prevents accidentally committing large files

**The hooks run automatically on every commit.** If they fail, your commit will be blocked until the issues are fixed.

To run hooks manually on all files:
```bash
pre-commit run --all-files
```

To run hooks on staged files only:
```bash
pre-commit run
```

### 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=engine_cli --cov-report=html

# Run specific test file
pytest tests/unit/test_agent.py

# Run integration tests
pytest tests/integration/
```

### 📦 Building

```bash
# Build package
poetry build

# Or with pip
python -m build
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
