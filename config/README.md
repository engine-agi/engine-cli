# Engine CLI Configuration

This directory contains CLI-specific configuration files.

## Files

### `cli-config.yaml`
Contains CLI-specific settings that are not shared with other Engine Framework components:

- **CLI Interface**: Colors, interactivity, table styles
- **Command Defaults**: Default values for agent, team, workflow, book commands
- **Output Formatting**: JSON/YAML formatting preferences
- **Local Storage**: Directory paths for saving local data
- **CLI Features**: Auto-complete, syntax highlighting, rich output

## Usage

The CLI automatically loads this configuration. You can override settings using:
- Command-line flags
- Environment variables
- Custom config file (via `--config` flag)

## Global vs CLI-Specific

- **Global configs** (in `engine-infra/config/`): Shared across all components (CI/CD, Docker, environment)
- **CLI-specific configs** (this file): Only affect CLI behavior and defaults