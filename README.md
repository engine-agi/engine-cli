# Engine CLI

[![PyPI version](https://badge.fury.io/py/engine-cli.svg)](https://pypi.org/project/engine-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**Engine Framework CLI** - Command-line interface for the AI Agent Orchestration System.

## 🚀 Features

- **Complete CLI**: Commands for all 6 pillars (Agents, Teams, Workflows, Tools, Protocols, Book)
- **Rich Interface**: Beautiful terminal UI with colors and progress bars
- **Interactive Mode**: REPL for interactive usage
- **Auto-completion**: Smart command completion
- **Configuration**: YAML/JSON config support

## 📦 Installation

```bash
pip install engine-cli
```

Or install with core:
```bash
pip install engine-agi[cli]
```

## 🏗️ Architecture

```
engine/
└── cli/
    ├── commands/
    │   ├── agent.py      # Agent management
    │   ├── team.py       # Team coordination
    │   ├── workflow.py   # Workflow orchestration
    │   ├── tool.py       # Tool integrations
    │   ├── protocol.py   # Protocol commands
    │   ├── book.py       # Memory system
    │   └── project.py    # Project management
    ├── main.py           # CLI entry point
    └── interactive.py    # REPL mode
```

## 🔧 Usage

```bash
# Show help
engine --help

# Create an agent
engine agent create --name "my-agent" --model "claude-3.5-sonnet"

# List all agents
engine agent list

# Start interactive mode
engine interactive

# Show workflow status
engine workflow status --id "wf-123"
```

## 📚 Commands

### Agent Commands
- `engine agent create` - Create new agent
- `engine agent list` - List all agents
- `engine agent update` - Update agent configuration
- `engine agent delete` - Delete agent

### Team Commands
- `engine team create` - Create new team
- `engine team add-member` - Add agent to team
- `engine team list` - List all teams

### Workflow Commands
- `engine workflow create` - Create new workflow
- `engine workflow run` - Execute workflow
- `engine workflow status` - Check workflow status

## ⚙️ Configuration

Create `~/.engine/config.yaml`:

```yaml
api:
  base_url: "http://localhost:8000"
  timeout: 30

defaults:
  model: "claude-3.5-sonnet"
  stack: ["python", "web"]
```

## 📚 Documentation

- [CLI Manual](https://engine-agi.github.io/engine-cli/)
- [Getting Started](https://engine-agi.github.io/engine-cli/getting-started)
- [Examples](https://github.com/engine-agi/engine-examples)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Part of the Engine Framework** | [engine-agi](https://github.com/engine-agi)