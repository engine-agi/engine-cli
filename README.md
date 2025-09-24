# Engine CLI

[![PyPI version](https://badge.fury.io/py/engine-cli.svg)](https://pypi.org/project/engine-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/engine-cli.svg)](https://pypi.org/project/engine-cli/)
[![License](https://img.shields.io/b    .build())
```

### 🎯 Practical Examples

#### **Complete Agent Setup**
```python
from engine_core import AgentBuilder, BookBuilder, ProtocolBuilder

# Create project memory book
book = (BookBuilder()
    .with_id("project-book")
    .add_chapter("1", "Requirements")
    .add_page("1", "1.1", "User Stories", content="As a user...")
    .enable_semantic_search()
    .build())

# Create analysis protocol
protocol = (ProtocolBuilder()
    .with_id("analysis-protocol")
    .with_name("Analysis First")
    .with_supported_intents([IntentCategory.ANALYSIS])
    .with_default_scope(ContextScope.PROJECT)
    .build())

# Create agent with full configuration
agent = (AgentBuilder()
    .with_id("senior-architect")
    .with_name("Senior Software Architect")
    .with_model("claude-3.5-sonnet")
    .with_speciality("System Architecture & Design")
    .with_persona("Experienced architect focused on scalable, maintainable systems")
    .with_stack(["python", "typescript", "aws", "kubernetes"])
    .with_tools(["github", "jira", "slack"])
    .with_protocol("analysis-protocol")
    .with_book("project-book")
    .build())
```

#### **Team Development Workflow**
```python
from engine_core import TeamBuilder, WorkflowBuilder, TeamCoordinationStrategy

# Create development team
team = (TeamBuilder()
    .with_id("backend-team")
    .with_name("Backend Development Team")
    .add_member("architect", TeamMemberRole.LEADER)
    .add_member("senior-dev", TeamMemberRole.MEMBER)
    .add_member("junior-dev", TeamMemberRole.MEMBER)
    .with_coordination_strategy(TeamCoordinationStrategy.HIERARCHICAL)
    .build())

# Create TDD workflow
workflow = (WorkflowBuilder()
    .with_id("tdd-pipeline")
    .add_vertex("analyze", agent_id="architect")
    .add_vertex("implement", agent_id="senior-dev")
    .add_vertex("test", agent_id="junior-dev")
    .add_vertex("review", agent_id="architect")
    .add_edge("analyze", "implement")
    .add_edge("implement", "test")
    .add_edge("test", "review")
    .build())
```

#### **Memory System with Search**
```python
from engine_core import BookBuilder, ContentType, AccessLevel, SearchScope

# Create comprehensive project memory
book = (BookBuilder()
    .with_id("full-project-book")
    .add_chapter("1", "Architecture")
    .add_page("1", "1.1", "System Overview",
             content="Microservices architecture with event-driven design")
    .add_page("1", "1.2", "API Design",
             content="RESTful APIs with OpenAPI 3.0 specification")

    .add_chapter("2", "Implementation")
    .add_page("2", "2.1", "Database Schema",
             content="PostgreSQL with optimized indexing strategy")
    .add_content("2.1", "schema.sql", ContentType.CODE,
                "CREATE TABLE users (...)", AccessLevel.INTERNAL)

    .enable_semantic_search()
    .build())

# Search examples
architecture_docs = book.search("microservices", SearchScope.CHAPTER)
api_specs = book.search("RESTful", SearchScope.BOOK)
code_examples = book.search("CREATE TABLE", SearchScope.PAGE)
```

#### **Protocol-Based Agent Behavior**
```python
from engine_core import ProtocolBuilder, IntentCategory, CommandType

# Create comprehensive development protocol
dev_protocol = (ProtocolBuilder()
    .with_id("full-dev-protocol")
    .with_name("Complete Development Protocol")
    .with_supported_intents([
        IntentCategory.ANALYSIS,
        IntentCategory.CREATION,
        IntentCategory.REVIEW,
        IntentCategory.OPTIMIZATION
    ])
    .with_supported_command_types([
        CommandType.TASK_EXECUTION,
        CommandType.CODE_GENERATION,
        CommandType.REVIEW_REQUEST
    ])
    .with_default_scope(ContextScope.PROJECT)
    .with_strict_validation(True)
    .with_max_context_size(100000)  # 100KB context limit
    .build())

# Use protocol in agent
agent = (AgentBuilder()
    .with_id("protocol-agent")
    .with_protocol("full-dev-protocol")
    .build())
```

### 🔒 Contract Compliance/License-AGPL%203.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
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

## 🔧 Engine Core Integration

Engine CLI integrates with **Engine Core** through well-defined public APIs. The CLI uses only public interfaces, ensuring clean separation and contract compliance.

### 📋 Public Interfaces

The following Engine Core interfaces are available for programmatic use:

#### **Core Builders**
- `AgentBuilder` - Create and configure AI agents
- `TeamBuilder` - Build coordinated agent teams
- `WorkflowBuilder` - Construct Pregel-based workflows
- `BookBuilder` - Manage hierarchical memory systems
- `ProtocolBuilder` - Define agent behavior protocols
- `ToolBuilder` - Configure external tool integrations

#### **Core Services**
- `WorkflowEngine` - Execute and monitor workflows
- `ToolExecutor` - Run external tools and integrations

#### **Enums & Types**
- `WorkflowState` - Workflow execution states (IDLE, EXECUTING, COMPLETED, etc.)
- `TeamCoordinationStrategy` - Team coordination modes (HIERARCHICAL, COLLABORATIVE, etc.)
- `TeamMemberRole` - Agent roles within teams (LEADER, MEMBER, etc.)
- `ContentType` - Memory content types (TEXT, MARKDOWN, CODE, etc.)
- `AccessLevel` - Content access levels (PUBLIC, INTERNAL, RESTRICTED, etc.)
- `ContentStatus` - Content lifecycle (DRAFT, PUBLISHED, ARCHIVED, etc.)
- `SearchScope` - Search boundaries (BOOK, CHAPTER, PAGE, etc.)
- `IntentCategory` - Agent intent types (ANALYSIS, CREATION, etc.)
- `CommandType` - Protocol command types
- `ContextScope` - Context boundaries (GLOBAL, LOCAL, etc.)

### 💡 Usage Examples

```python
from engine_core import AgentBuilder, WorkflowBuilder, WorkflowState

# Create an agent
agent = (AgentBuilder()
    .with_id("my-agent")
    .with_model("claude-3.5-sonnet")
    .with_stack(["python", "typescript"])
    .build())

# Build a workflow
workflow = (WorkflowBuilder()
    .with_id("my-workflow")
    .add_vertex("task1", agent_id="my-agent")
    .add_edge("task1", "task2")
    .build())

# Check workflow status
if workflow.state == WorkflowState.COMPLETED:
    print("Workflow finished successfully!")
```

### � Interface Reference

#### **AgentBuilder**
```python
from engine_core import AgentBuilder

agent = (AgentBuilder()
    .with_id("agent-001")
    .with_name("Senior Developer")
    .with_model("claude-3.5-sonnet")
    .with_speciality("Full-Stack Development")
    .with_persona("Experienced, methodical developer")
    .with_stack(["python", "react", "postgresql"])
    .with_tools(["github", "vscode"])
    .with_protocol("analysis_first")
    .with_workflow("tdd_workflow")
    .with_book("project_memory")
    .build())
```

#### **TeamBuilder**
```python
from engine_core import TeamBuilder, TeamCoordinationStrategy, TeamMemberRole

team = (TeamBuilder()
    .with_id("dev-team")
    .with_name("Development Team")
    .add_member("agent-001", TeamMemberRole.LEADER)
    .add_member("agent-002", TeamMemberRole.MEMBER)
    .with_coordination_strategy(TeamCoordinationStrategy.HIERARCHICAL)
    .build())
```

#### **WorkflowBuilder**
```python
from engine_core import WorkflowBuilder, WorkflowEngine

workflow = (WorkflowBuilder()
    .with_id("code-review-pipeline")
    .add_vertex("analysis", agent_id="senior-dev")
    .add_vertex("implementation", agent_id="backend-dev")
    .add_vertex("testing", agent_id="qa-engineer")
    .add_edge("analysis", "implementation")
    .add_edge("implementation", "testing")
    .build())

# Execute workflow
engine = WorkflowEngine()
result = await engine.execute_workflow(workflow)
```

#### **BookBuilder (Memory System)**
```python
from engine_core import BookBuilder, ContentType, AccessLevel, SearchScope

book = (BookBuilder()
    .with_id("project-memory")
    .add_chapter("1", "Architecture")
    .add_page("1", "1.1", "Tech Stack", content="...")
    .add_content("1.1", "database-schema", ContentType.CODE,
                "SQL schema definitions", AccessLevel.INTERNAL)
    .enable_semantic_search()
    .build())

# Search content
results = book.search("authentication", SearchScope.BOOK)
```

#### **ProtocolBuilder**
```python
from engine_core import ProtocolBuilder, IntentCategory, ContextScope

protocol = (ProtocolBuilder()
    .with_id("analysis-protocol")
    .with_name("Analysis First Protocol")
    .with_supported_intents([IntentCategory.ANALYSIS, IntentCategory.REVIEW])
    .with_default_scope(ContextScope.PROJECT)
    .with_strict_validation(True)
    .build())
```

#### **ToolBuilder**
```python
from engine_core import ToolBuilder
from engine_core.models.tool import ToolType

tool = (ToolBuilder()
    .with_id("github-integration")
    .with_name("GitHub API Tool")
    .with_description("GitHub repository management")
    .with_type(ToolType.API)
    .with_config({"token": "ghp_...", "repo": "owner/repo"})
    .build())
```

### �🔒 Contract Compliance

Engine CLI follows strict multirepo contracts:
- ✅ **Package Contracts**: Correct dependency management (`engine-core = "^1.0.1"`)
- ✅ **API Contracts**: Uses only public interfaces (no internal imports)
- ✅ **Data Contracts**: Standardized JSON/YAML formats
- ✅ **Version Contracts**: Semantic versioning compliance

For detailed contract specifications, see [contract.md](../../tasks/contract.md).

### 🚀 Migration Guide

#### **Upgrading from Internal APIs**

If you were using internal Engine Core APIs, here's how to migrate:

**❌ Before (Internal APIs - Not Supported):**
```python
# DON'T DO THIS - Internal APIs
from engine_core.core.agents.agent_builder import AgentBuilder
from engine_core.core.workflows.workflow_engine import WorkflowState
from engine_core.core.teams.team_builder import TeamCoordinationStrategy
```

**✅ After (Public APIs - Recommended):**
```python
# DO THIS - Public APIs
from engine_core import (
    AgentBuilder, WorkflowBuilder, TeamBuilder,
    WorkflowState, TeamCoordinationStrategy, TeamMemberRole,
    WorkflowEngine
)
```

#### **Version Compatibility**

- **Engine CLI v1.0.1** requires **Engine Core v1.0.1+**
- **Engine CLI v1.1.0** requires **Engine Core v1.1.0+** (upcoming)
- Use caret versioning: `engine-core = "^1.0.1"`

#### **Breaking Changes in v1.1.0**

1. **Removed Internal Imports**: All internal API usage removed
2. **Expanded Public APIs**: 20+ public interfaces now available
3. **Enhanced Validation**: Strict contract compliance enforced
4. **Improved Performance**: Optimized lazy loading and caching

#### **Migration Checklist**

- [ ] Update `engine-core` dependency to `^1.0.1`
- [ ] Replace internal imports with public APIs
- [ ] Update enum usage to use public constants
- [ ] Test with new validation (`validate_contracts.py`)
- [ ] Update CI/CD to include contract validation

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
# Test comment
