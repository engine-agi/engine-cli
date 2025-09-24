"""Configuration management commands."""

from pathlib import Path

import click

from engine_cli.config import (
    config_manager,
    create_default_config,
    get_config_value,
    load_config,
    save_config,
    set_config_value,
    show_config,
)
from engine_cli.formatting import error, header, info, key_value, success


@click.group()
def cli():
    """Manage Engine CLI configuration."""
    pass


@cli.command()
@click.option(
    "--file", "-f", "config_file", type=click.Path(), help="Configuration file to load"
)
def show(config_file):
    """Show current configuration."""
    try:
        if config_file:
            config_manager.load_config(config_file)
        show_config()
    except Exception as e:
        error(f"Failed to show configuration: {e}")


@cli.command()
@click.argument("key")
@click.argument("value")
@click.option(
    "--file",
    "-f",
    "config_file",
    type=click.Path(),
    help="Configuration file to update",
)
def set(key, value, config_file):
    """Set a configuration value."""
    try:
        # Load current config
        if config_file:
            config = load_config(config_file)
        else:
            config = load_config()

        # Set the value
        set_config_value(key, value)

        # Save the config
        save_config(config, config_file)

        success(f"Configuration updated: {key} = {value}")

    except Exception as e:
        error(f"Failed to set configuration: {e}")


@cli.command()
@click.argument("key")
def get(key):
    """Get a configuration value."""
    try:
        value = get_config_value(key)
        if value is not None:
            click.echo(f"{key}: {value}")
        else:
            info(f"Configuration key '{key}' not found")
    except Exception as e:
        error(f"Failed to get configuration: {e}")


@cli.command()
@click.option(
    "--file",
    "-f",
    "config_file",
    type=click.Path(),
    help="Configuration file to create",
)
@click.option(
    "--force", "-y", is_flag=True, help="Overwrite existing configuration file"
)
def init(config_file, force):
    """Create default configuration file."""
    try:
        if config_file:
            config_path = Path(config_file)
        else:
            config_path = Path.home() / ".engine" / "config.yaml"

        if config_path.exists() and not force:
            error(f"Configuration file already exists: {config_path}")
            info("Use --force to overwrite existing file")
            return

        # Create default configuration
        config = create_default_config(config_path)

        success(f"Default configuration created at: {config_path}")

        # Show the created configuration
        header("Created Configuration")
        key_value(config.dict(), "Default Settings")

    except Exception as e:
        error(f"Failed to create configuration: {e}")


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file):
    """Validate configuration file."""
    try:
        config = load_config(config_file)
        success(f"Configuration file is valid: {config_file}")

        # Show summary
        config_data = config.dict()
        sections = [k for k, v in config_data.items() if v]
        info(f"Active sections: {', '.join(sections)}")

    except Exception as e:
        error(f"Configuration validation failed: {e}")
        return 1


@cli.command()
@click.option(
    "--file", "-f", "config_file", type=click.Path(), help="Configuration file to edit"
)
def edit(config_file):
    """Edit configuration file in default editor."""
    try:
        if config_file:
            config_path = Path(config_file)
        else:
            # Find existing config file
            for path in config_manager.config_paths:
                if path.exists():
                    config_path = path
                    break
            else:
                error("No configuration file found. Use 'config init' to create one.")
                return

        if not config_path.exists():
            error(f"Configuration file not found: {config_path}")
            return

        # Open in editor
        import os
        import subprocess

        editor = os.environ.get("EDITOR", "nano")
        try:
            subprocess.run([editor, str(config_path)], check=True)
            success(f"Configuration edited: {config_path}")
        except subprocess.CalledProcessError:
            error(f"Editor '{editor}' not found or failed")
            info("Set EDITOR environment variable to change editor")

    except Exception as e:
        error(f"Failed to edit configuration: {e}")


@cli.command()
def paths():
    """Show configuration file search paths."""
    from engine_cli.formatting import list_items

    header("Configuration File Search Paths")
    info("Files are loaded in order of precedence (first found wins):")

    paths_info = []
    for i, path in enumerate(config_manager.config_paths, 1):
        exists = "✓" if path.exists() else "✗"
        paths_info.append(f"{i}. {exists} {path}")

    list_items(paths_info, bullet="")

    header("Environment Variables")
    info(f"Environment variables with prefix '{config_manager.env_prefix}' are loaded")
    info("Examples: ENGINE_API_BASE_URL, ENGINE_DEBUG, ENGINE_LOG_LEVEL")


@cli.command()
@click.argument("section", required=False)
def reset(section):
    """Reset configuration to defaults."""
    try:
        if section:
            # Reset specific section
            default_config = create_default_config()
            current_config = load_config()

            if hasattr(default_config, section):
                setattr(current_config, section, getattr(default_config, section))
                success(f"Section '{section}' reset to defaults")
            else:
                error(f"Unknown configuration section: {section}")
                return
        else:
            # Reset entire configuration
            default_config = create_default_config()
            current_config = default_config
            success("Entire configuration reset to defaults")

        # Save the updated config
        save_config(current_config)

    except Exception as e:
        error(f"Failed to reset configuration: {e}")
