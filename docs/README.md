# Engine CLI Documentation

## Overview

The Engine CLI (`engine`) is a comprehensive command-line interface for managing AI agents, teams, workflows, and all framework components. Built with Typer and Rich for an excellent user experience.

## Documentation

This documentation is organized as follows:

- **[CLI Manual](README.md)** - Complete command reference (this document)
- **[Practical Examples](examples.md)** - Real-world usage examples and scenarios
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues and solutions

For quick start examples, see the [Practical Examples](examples.md). For help with issues, refer to the [Troubleshooting Guide](troubleshooting.md).

## Installation

```bash
# Install from PyPI
pip install engine-cli

# Or install from source
pip install -e .
```

## Quick Start

```bash
# Initialize configuration
engine config init

# Create your first agent
engine agent create code-reviewer \
  --model claude-3.5-sonnet \
  --stack python javascript \
  --speciality "Code Quality Analysis"

# List all agents
engine agent list

# Start interactive mode
engine interactive
```

## Global Options

All commands support these global options:

```bash
engine [OPTIONS] COMMAND [ARGS]

Global Options:
  --help          Show help message and exit
  --version       Show version information
  --verbose, -v   Enable verbose output
  --quiet, -q     Suppress non-error output
  --config FILE   Path to configuration file
  --project ID    Project context for commands
  --format FORMAT Output format (json, yaml, table)
```

## Commands

### Project Management

#### Create Project
```bash
engine project create NAME [OPTIONS]

Options:
  --description TEXT  Project description
  --template TEXT     Project template to use

Examples:
  engine project create my-project --description "My AI project"
```

#### List Projects
```bash
engine project list [OPTIONS]

Options:
  --format FORMAT  Output format (table, json, yaml)

Examples:
  engine project list
  engine project list --format json
```

#### Project Details
```bash
engine project show PROJECT_ID [OPTIONS]

Examples:
  engine project show my-project
```

### Agent Management

#### Create Agent
```bash
engine agent create NAME [OPTIONS]

Options:
  --model TEXT         AI model to use
  --stack TEXT         Technology stack (can be used multiple times)
  --speciality TEXT    Agent speciality
  --persona TEXT       Agent persona description
  --tools TEXT         Tools to equip (can be used multiple times)
  --protocol TEXT      Protocol to use
  --workflow TEXT      Default workflow
  --book TEXT          Memory book to use

Examples:
  engine agent create senior-dev \
    --model claude-3.5-sonnet \
    --stack python react postgresql \
    --speciality "Full-Stack Development" \
    --persona "Experienced developer with 10+ years"
```

#### List Agents
```bash
engine agent list [OPTIONS]

Options:
  --project TEXT  Filter by project
  --format FORMAT Output format

Examples:
  engine agent list
  engine agent list --project my-project --format json
```

#### Execute Agent
```bash
engine agent execute AGENT_ID TASK [OPTIONS]

Options:
  --context TEXT   Additional context
  --async          Execute asynchronously
  --timeout INT    Execution timeout in seconds

Examples:
  engine agent execute senior-dev "Review this pull request"
  engine agent execute senior-dev "Fix the bug in user authentication" --async
```

### Team Management

#### Create Team
```bash
engine team create NAME [OPTIONS]

Options:
  --description TEXT  Team description
  --leader TEXT       Leader agent ID
  --members TEXT      Team members (can be used multiple times)
  --strategy TEXT     Coordination strategy

Examples:
  engine team create dev-team \
    --description "Development team" \
    --leader senior-dev \
    --members junior-dev qa-engineer \
    --strategy hierarchical
```

#### List Teams
```bash
engine team list [OPTIONS]

Examples:
  engine team list
```

### Workflow Management

#### Create Workflow
```bash
engine workflow create NAME [OPTIONS]

Options:
  --description TEXT  Workflow description
  --vertices TEXT     Workflow vertices (JSON format)
  --edges TEXT        Workflow edges (JSON format)

Examples:
  engine workflow create code-review \
    --description "Code review workflow" \
    --vertices '[{"id": "analysis", "agent": "senior-dev"}, {"id": "review", "agent": "qa-engineer"}]' \
    --edges '[{"from": "analysis", "to": "review"}]'
```

#### Execute Workflow
```bash
engine workflow run WORKFLOW_ID [OPTIONS]

Options:
  --input TEXT     Input data for workflow
  --async          Execute asynchronously
  --monitor        Enable real-time monitoring

Examples:
  engine workflow run code-review --input "PR #123" --monitor
```

### Tool Management

#### List Tools
```bash
engine tool list [OPTIONS]

Examples:
  engine tool list
```

#### Configure Tool
```bash
engine tool configure TOOL_NAME [OPTIONS]

Examples:
  engine tool configure github --token "your-token"
```

### Protocol Management

#### List Protocols
```bash
engine protocol list [OPTIONS]

Examples:
  engine protocol list
```

#### Create Protocol
```bash
engine protocol create NAME [OPTIONS]

Options:
  --description TEXT  Protocol description
  --commands TEXT     Protocol commands (JSON format)

Examples:
  engine protocol create analysis-first \
    --description "Analysis first approach" \
    --commands '{"analyze": "Analyze requirements first", "implement": "Then implement"}'
```

### Book Management

#### Create Book
```bash
engine book create NAME [OPTIONS]

Options:
  --description TEXT  Book description
  --chapters TEXT     Initial chapters (JSON format)

Examples:
  engine book create project-memory \
    --description "Project knowledge base" \
    --chapters '{"1": {"title": "Architecture", "content": "System overview"}}'
```

#### Search Book
```bash
engine book search BOOK_ID QUERY [OPTIONS]

Examples:
  engine book search project-memory "authentication patterns"
```

### Configuration Management

#### Initialize Config
```bash
engine config init [OPTIONS]

Options:
  --force    Overwrite existing configuration
  --path TEXT Custom config path

Examples:
  engine config init
  engine config init --force
```

#### Show Configuration
```bash
engine config show [OPTIONS]

Options:
  --format FORMAT Output format

Examples:
  engine config show
  engine config show --format json
```

#### Get Config Value
```bash
engine config get KEY [OPTIONS]

Examples:
  engine config get database.url
  engine config get api.base_url
```

#### Set Config Value
```bash
engine config set KEY VALUE [OPTIONS]

Examples:
  engine config set database.url "postgresql://localhost:5432/engine"
  engine config set api.base_url "http://localhost:8000"
```

#### Validate Configuration
```bash
engine config validate [OPTIONS]

Options:
  --file TEXT  Config file to validate

Examples:
  engine config validate
  engine config validate --file custom-config.yaml
```

### Advanced Commands

#### Monitor System
```bash
engine advanced monitor [OPTIONS]

Options:
  --watch     Watch mode for continuous monitoring
  --json      Output in JSON format
  --interval INT Update interval in seconds

Examples:
  engine advanced monitor
  engine advanced monitor --watch --interval 5
  engine advanced monitor --json
```

#### Health Check
```bash
engine advanced health [OPTIONS]

Examples:
  engine advanced health
```

#### Bulk Operations
```bash
engine advanced bulk agents PATTERN [OPTIONS]

Options:
  --action TEXT  Action to perform (start, stop, restart)
  --dry-run      Show what would be done without executing

Examples:
  engine advanced bulk agents "dev-*" --action start
  engine advanced bulk agents "*" --action stop --dry-run
```

#### Config Operations
```bash
# Export configuration
engine advanced config-ops export OUTPUT_FILE [OPTIONS]

# Import configuration
engine advanced config-ops import INPUT_FILE [OPTIONS]

Options:
  --format FORMAT  Configuration format (yaml, json)
  --merge          Merge with existing config instead of replacing

Examples:
  engine advanced config-ops export backup.yaml
  engine advanced config-ops import backup.yaml --merge
```

### Status Commands

#### System Status
```bash
engine status [OPTIONS]

Options:
  --detailed  Show detailed status information
  --json      Output in JSON format

Examples:
  engine status
  engine status --detailed --json
```

## Interactive Mode

The Engine CLI includes an interactive mode with auto-completion and command history:

```bash
engine interactive
```

Features:
- Command auto-completion
- History navigation
- Syntax highlighting
- Context-aware help

## Configuration

The CLI uses a YAML configuration file located at `~/.engine/config.yaml` by default.

### Configuration Sections

```yaml
# Core settings
core:
  debug: false
  log_level: INFO
  version: "1.0.0"

# CLI settings
cli:
  file: engine.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  level: INFO

# Agent defaults
agent_defaults:
  max_tokens: 4096
  model: claude-3.5-sonnet
  temperature: 0.7

# API settings
api:
  base_url: "http://localhost:8000"
  timeout: 30

# Database settings
database:
  url: "postgresql://localhost:5432/engine"
  pool_size: 10

# Monitoring settings
monitoring:
  enabled: true
  health_check_interval: 30
  metrics_port: 9090
```

## Environment Variables

The CLI supports configuration via environment variables with the `ENGINE_` prefix:

```bash
export ENGINE_DEBUG=true
export ENGINE_LOG_LEVEL=DEBUG
export ENGINE_DATABASE_URL="postgresql://localhost:5432/engine"
export ENGINE_API_BASE_URL="http://localhost:8000"
```

## Troubleshooting

### Common Issues

#### Configuration Not Found
```bash
# Initialize configuration
engine config init

# Or specify custom config path
engine --config /path/to/config.yaml [command]
```

#### Connection Refused
```bash
# Check API server status
engine advanced health

# Verify configuration
engine config show
```

#### Permission Denied
```bash
# Check file permissions
ls -la ~/.engine/

# Reinitialize configuration
engine config init --force
```

### Debug Mode

Enable verbose output for troubleshooting:

```bash
# Enable verbose mode
engine --verbose [command]

# Set debug environment
export ENGINE_LOG_LEVEL=DEBUG
engine [command]
```

### Getting Help

```bash
# General help
engine --help

# Command-specific help
engine agent --help
engine config --help

# Interactive help
engine interactive --tutorial
```

## Examples

### Complete Workflow Example

```bash
# 1. Initialize project
engine project create ai-assistant --description "AI Assistant Project"

# 2. Create agents
engine agent create architect \
  --model claude-3.5-sonnet \
  --stack python typescript \
  --speciality "System Architecture"

engine agent create developer \
  --model claude-3.5-sonnet \
  --stack python react postgresql \
  --speciality "Full-Stack Development"

# 3. Create team
engine team create dev-team \
  --leader architect \
  --members developer \
  --strategy hierarchical

# 4. Create workflow
engine workflow create development \
  --description "Software development workflow" \
  --vertices '[{"id": "design", "agent": "architect"}, {"id": "implement", "agent": "developer"}]' \
  --edges '[{"from": "design", "to": "implement"}]'

# 5. Execute workflow
engine workflow run development --input "Build a user authentication system"

# 6. Monitor progress
engine advanced monitor --watch
```

### Configuration Management Example

```bash
# Initialize configuration
engine config init

# Set database connection
engine config set database.url "postgresql://user:pass@localhost:5432/engine"

# Set API endpoint
engine config set api.base_url "https://api.engine-framework.com"

# Verify configuration
engine config show

# Export configuration backup
engine advanced config-ops export config-backup.yaml
```

## Contributing

When adding new CLI commands:

1. **Follow naming conventions**: Use consistent command and option names
2. **Add comprehensive help**: Include descriptions, examples, and option details
3. **Handle errors gracefully**: Provide clear error messages and suggestions
4. **Support output formats**: JSON, YAML, and table formats
5. **Add examples**: Include practical usage examples
6. **Test thoroughly**: Unit tests and integration tests
7. **Update documentation**: Keep this manual up to date

## License

Engine Framework CLI is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
