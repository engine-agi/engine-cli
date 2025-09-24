# Engine CLI Documentation Index

## 📚 Documentation Overview

Welcome to the Engine CLI documentation! This repository contains comprehensive documentation for the Engine Framework Command Line Interface.

## 📖 Documentation Files

### Core Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[CLI Manual](README.md)** | Complete command reference with syntax, options, and examples | All users |
| **[Practical Examples](examples.md)** | Real-world usage scenarios, tutorials, and best practices | Beginners to Advanced |
| **[Troubleshooting Guide](troubleshooting.md)** | Common issues, error resolution, and diagnostic procedures | Developers, DevOps |

### Quick Access Links

- 🚀 **[Get Started](README.md#quick-start)** - First steps with Engine CLI
- 🧠 **[Agent Management](README.md#agent-management)** - Creating and managing AI agents
- 👥 **[Team Coordination](README.md#team-management)** - Building and managing agent teams
- ⚡ **[Workflow Execution](README.md#workflow-management)** - Running Pregel-based workflows
- 🔧 **[Tool Integration](README.md#tool-management)** - Managing external integrations
- 📋 **[Protocol System](README.md#protocol-management)** - Configuring agent behaviors
- 📚 **[Memory Management](README.md#book-management)** - Hierarchical memory system
- ⚙️ **[Configuration](README.md#configuration-management)** - CLI and system configuration
- 🔍 **[Troubleshooting](troubleshooting.md)** - Solving common problems
- 💡 **[Examples](examples.md)** - Practical usage scenarios

## 🎯 User Guides

### For Beginners
1. **[Installation & Setup](README.md#installation)**
2. **[Quick Start Guide](README.md#quick-start)**
3. **[Basic Examples](examples.md#getting-started-examples)**
4. **[Interactive Mode](README.md#interactive-mode)**

### For Developers
1. **[Agent Creation](examples.md#agent-management-examples)**
2. **[Workflow Building](examples.md#workflow-management-examples)**
3. **[Team Management](examples.md#team-management-examples)**
4. **[Tool Integration](examples.md#tool-integration-examples)**

### For DevOps/Administrators
1. **[Configuration Management](examples.md#configuration-management-examples)**
2. **[Monitoring & Logging](examples.md#monitoring-and-logging)**
3. **[Backup & Recovery](examples.md#backup-and-recovery)**
4. **[Troubleshooting](troubleshooting.md)**

## 📋 Command Categories

### Core Commands
- **Project**: `project create`, `project list`, `project show`
- **Agent**: `agent create`, `agent execute`, `agent list`, `agent show`
- **Team**: `team create`, `team add-agent`, `team execute`, `team status`
- **Workflow**: `workflow create`, `workflow run`, `workflow add-vertex`, `workflow add-edge`

### Advanced Commands
- **Tool**: `tool install`, `tool configure`, `tool test`
- **Protocol**: `protocol create`, `protocol add-command`
- **Book**: `book create`, `book add-page`, `book search`
- **Config**: `config init`, `config set`, `config show`, `config export`

### System Commands
- **Status**: `status`, `advanced health`
- **Monitoring**: `advanced monitor`, `advanced logs`
- **Maintenance**: `advanced backup`, `advanced services`

## 🔧 Quick Reference

### Most Used Commands

```bash
# Getting started
engine config init                    # Initialize configuration
engine status                         # Check system status
engine --help                         # Get help

# Agent operations
engine agent create NAME --model MODEL # Create agent
engine agent list                     # List agents
engine agent execute AGENT TASK       # Execute task

# Team operations
engine team create NAME               # Create team
engine team add-agent TEAM AGENT      # Add agent to team
engine team execute TEAM TASK         # Execute team task

# Workflow operations
engine workflow create NAME           # Create workflow
engine workflow run WORKFLOW          # Execute workflow

# Configuration
engine config show                    # Show current config
engine config set KEY VALUE           # Set config value
```

### Global Options

```bash
engine [OPTIONS] COMMAND [ARGS]

Options:
  --help          Show help and exit
  --version       Show version
  --verbose, -v   Verbose output
  --quiet, -q     Suppress output
  --config FILE   Config file path
  --project ID    Project context
  --format FORMAT Output format (json, yaml, table)
```

## 🚨 Troubleshooting Quick Start

### Common Issues
- **Command not found**: `pip install --upgrade engine-cli`
- **Config not found**: `engine config init`
- **Connection refused**: Check API server status
- **Permission denied**: Fix file permissions

### Debug Mode
```bash
# Enable verbose output
engine --verbose [command]

# Check logs
engine advanced logs --level error

# Validate configuration
engine config validate
```

For detailed troubleshooting, see **[Troubleshooting Guide](troubleshooting.md)**.

## 📖 Learning Path

### Level 1: Basics (15 minutes)
1. [Installation](README.md#installation)
2. [Quick Start](README.md#quick-start)
3. [Basic Commands](examples.md#getting-started-examples)

### Level 2: Core Features (30 minutes)
1. [Agent Management](examples.md#agent-management-examples)
2. [Team Coordination](examples.md#team-management-examples)
3. [Workflow Execution](examples.md#workflow-management-examples)

### Level 3: Advanced Usage (45 minutes)
1. [Tool Integration](examples.md#tool-integration-examples)
2. [Protocol System](examples.md#protocol-management-examples)
3. [Memory Management](examples.md#book-memory-management-examples)

### Level 4: Production (60+ minutes)
1. [Configuration Management](examples.md#configuration-management-examples)
2. [Monitoring & Maintenance](examples.md#monitoring-and-logging)
3. [Backup & Recovery](examples.md#backup-and-recovery)
4. [Troubleshooting](troubleshooting.md)

## 🔗 Related Documentation

- **[Engine Core Documentation](../../Doc/)** - Framework architecture and concepts
- **[API Documentation](../../docs/api-openapi.yaml)** - REST API reference
- **[Examples Repository](../../engine-examples/)** - Code examples and templates
- **[Web Dashboard](../../engine-web/)** - GUI interface documentation

## 📞 Support

### Getting Help
- **Built-in Help**: `engine --help` or `engine [command] --help`
- **Interactive Mode**: `engine interactive` for guided usage
- **Documentation**: This documentation repository
- **Community**: GitHub Issues and Discussions

### Professional Support
- **Enterprise Support**: Commercial licensing available
- **Custom Deployments**: Professional services offered
- **Training**: Official training and certification programs

---

## 📋 Checklist for New Users

- [ ] **Installation**: Engine CLI installed and accessible
- [ ] **Configuration**: `engine config init` completed
- [ ] **First Agent**: Created your first agent successfully
- [ ] **Basic Commands**: Familiar with core commands
- [ ] **Documentation**: Know where to find help and examples

**Next Steps**: Try the [practical examples](examples.md) to see Engine CLI in action!

---

*Last updated: December 2024*
*Engine CLI Version: 1.0.0*
