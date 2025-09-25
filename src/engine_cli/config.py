"""Configuration system for Engine CLI."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, ValidationError, validator

from engine_cli.formatting import error, info, success, warning


class EngineConfig(BaseModel):
    """Main configuration model for Engine CLI."""

    # Core settings
    core: Dict[str, Any] = Field(
        default_factory=dict, description="Core engine settings"
    )

    # CLI settings
    cli: Dict[str, Any] = Field(
        default_factory=dict, description="CLI-specific settings"
    )

    # API settings
    api: Dict[str, Any] = Field(
        default_factory=dict, description="API connection settings"
    )

    # Database settings
    database: Dict[str, Any] = Field(
        default_factory=dict, description="Database configuration"
    )

    # Logging settings
    logging: Dict[str, Any] = Field(
        default_factory=dict, description="Logging configuration"
    )

    # Agent defaults
    agent_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default agent settings"
    )

    # Team defaults
    team_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default team settings"
    )

    # Workflow defaults
    workflow_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default workflow settings"
    )

    # Tool defaults
    tool_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default tool settings"
    )

    # Protocol defaults
    protocol_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default protocol settings"
    )

    # Book defaults
    book_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default book settings"
    )

    # Project defaults
    project_defaults: Dict[str, Any] = Field(
        default_factory=dict, description="Default project settings"
    )

    # Monitoring settings
    monitoring: Dict[str, Any] = Field(
        default_factory=dict, description="Monitoring configuration"
    )

    class Config:
        """Pydantic configuration."""

        validate_assignment = True
        extra = "allow"  # Allow extra fields for extensibility

    @validator("core")
    def validate_core_config(cls, v):
        """Validate core configuration."""
        if not isinstance(v, dict):
            raise ValueError("Core config must be a dictionary")
        return v

    @validator("api")
    def validate_api_config(cls, v):
        """Validate API configuration."""
        if not isinstance(v, dict):
            raise ValueError("API config must be a dictionary")

        # Validate URL format if present
        if "base_url" in v:
            url = v["base_url"]
            if not (url.startswith("http://") or url.startswith("https://")):
                raise ValueError("API base_url must start with http:// or https://")

        return v

    @validator("database")
    def validate_database_config(cls, v):
        """Validate database configuration."""
        if not isinstance(v, dict):
            raise ValueError("Database config must be a dictionary")

        # Validate database URL if present
        if "url" in v:
            url = v["url"]
            if not (
                url.startswith("postgresql://")
                or url.startswith("sqlite://")
                or url.startswith("mysql://")
            ):
                warning(f"Database URL format may be invalid: {url}")

        return v


@dataclass
class ConfigManager:
    """Configuration manager for Engine CLI."""

    # Configuration file paths (in order of precedence)
    config_paths: List[Path] = field(
        default_factory=lambda: [
            Path.home() / ".engine" / "config.yaml",  # Global config
            Path.home() / ".engine" / "config.json",  # Global config (JSON)
            Path.cwd() / ".engine.yaml",  # Local config
            Path.cwd() / ".engine.json",  # Local config (JSON)
            Path.cwd() / "engine.yaml",  # Project config
            Path.cwd() / "engine.json",  # Project config (JSON)
        ]
    )

    # Environment variable prefix
    env_prefix: str = "ENGINE_"

    # Current configuration
    _config: Optional[EngineConfig] = None
    _config_file: Optional[Path] = None

    def __post_init__(self):
        """Initialize configuration manager."""
        self.ensure_config_dir()

    def ensure_config_dir(self):
        """Ensure configuration directory exists."""
        config_dir = Path.home() / ".engine"
        config_dir.mkdir(exist_ok=True)

    def load_config(
        self, config_file: Optional[Union[str, Path]] = None
    ) -> EngineConfig:
        """Load configuration from file and environment variables."""
        if config_file:
            config_file = Path(config_file)
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            self._config_file = config_file
            config = self._load_from_file(config_file)
            # Always merge environment variables
            config = self._merge_env_vars(config)
            self._config = config
            return config

        # Try to load from default locations
        for path in self.config_paths:
            if path.exists():
                try:
                    self._config_file = path
                    config = self._load_from_file(path)
                    # Merge with environment variables
                    config = self._merge_env_vars(config)
                    self._config = config
                    return config
                except Exception as e:
                    warning(f"Failed to load config from {path}: {e}")
                    continue

        # No config file found, create default config
        config = self.create_default_config()
        config = self._merge_env_vars(config)
        self._config = config
        return config

    def _load_from_file(self, file_path: Path) -> EngineConfig:
        """Load configuration from a specific file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    data = yaml.safe_load(f) or {}
                elif file_path.suffix == ".json":
                    data = json.load(f)
                else:
                    raise ValueError(
                        f"Unsupported config file format: {file_path.suffix}"
                    )

            # Validate and create config
            config = EngineConfig(**data)
            return config

        except ValidationError as e:
            error(f"Configuration validation error in {file_path}:")
            for error_detail in e.errors():
                error(f"  {error_detail['loc'][0]}: {error_detail['msg']}")
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {file_path}: {e}")

    def _merge_env_vars(self, config: EngineConfig) -> EngineConfig:
        """Merge environment variables into configuration."""
        env_vars = self._get_env_vars()

        # Set values using dot notation directly on config
        for key, value in env_vars.items():
            keys = key.split(".")
            self._set_nested_value(config.__dict__, keys, value)

        return config

    def _get_env_vars(self) -> Dict[str, str]:
        """Get all environment variables with the ENGINE_ prefix."""
        env_vars = {}
        prefix_len = len(self.env_prefix)

        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix: ENGINE_API_BASE_URL -> API_BASE_URL
                config_key = key[prefix_len:]
                # Split into section and field: API_BASE_URL -> ['API', 'BASE_URL']
                parts = config_key.split("_", 1)
                if len(parts) == 2:
                    section, field = parts
                    # Convert to dot notation: API + BASE_URL -> api.base_url
                    section = section.lower()
                    field = (
                        field.lower()
                    )  # Keep underscores as-is, don't convert to dots
                    full_key = f"{section}.{field}"
                    env_vars[full_key] = value

        return env_vars

    def _set_nested_value(
        self, config_dict: Dict[str, Any], keys: List[str], value: Any
    ):
        """Set a nested value in the configuration dictionary."""
        if len(keys) == 1:
            # Convert string values to appropriate types
            if isinstance(value, str):
                if value.lower() in ("true", "false"):
                    value = value.lower() == "true"
                elif value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    try:
                        value = float(value)
                    except ValueError:
                        pass  # Keep as string

            config_dict[keys[0]] = value
        else:
            if keys[0] not in config_dict:
                config_dict[keys[0]] = {}
            elif not isinstance(config_dict[keys[0]], dict):
                config_dict[keys[0]] = {}

            self._set_nested_value(config_dict[keys[0]], keys[1:], value)

    def save_config(
        self,
        config: EngineConfig,
        file_path: Optional[Union[str, Path]] = None,
    ):
        """Save configuration to file."""
        if file_path is None:
            file_path = self._config_file or (Path.home() / ".engine" / "config.yaml")

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = config.dict()

            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.suffix in [".yaml", ".yml"]:
                    yaml.dump(data, f, default_flow_style=False, indent=2)
                elif file_path.suffix == ".json":
                    json.dump(data, f, indent=2)
                else:
                    raise ValueError(
                        f"Unsupported config file format: {file_path.suffix}"
                    )

            success(f"Configuration saved to {file_path}")
            self._config_file = file_path

        except Exception as e:
            error(f"Failed to save configuration to {file_path}: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value."""
        if self._config is None:
            self.load_config()

        keys = key.split(".")
        value = self._config.__dict__

        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default

    def set(self, key: str, value: Any):
        """Set a configuration value."""
        if self._config is None:
            self.load_config()

        keys = key.split(".")
        self._set_nested_value(self._config.__dict__, keys, value)

    def show_config(self):
        """Display current configuration."""
        from engine_cli.formatting import header, key_value

        if self._config is None:
            self.load_config()

        if self._config is None:
            error("No configuration loaded")
            return

        header("Current Configuration")

        # Show config file location
        if self._config_file:
            info(f"Config file: {self._config_file}")

        # Show configuration sections
        config_data = self._config.dict()
        for section, values in config_data.items():
            if values:  # Only show non-empty sections
                key_value(values, f"{section.title()} Settings")

    def create_default_config(
        self, file_path: Optional[Union[str, Path]] = None
    ) -> EngineConfig:
        """Create a default configuration."""
        default_config = EngineConfig(
            core={"version": "1.0.1", "debug": False, "log_level": "INFO"},
            cli={"interactive": True, "colors": True, "history_size": 1000},
            api={
                "base_url": "http://localhost:8000",
                "timeout": 30,
                "retries": 3,
            },
            database={
                "url": "sqlite:///engine.db",
                "pool_size": 10,
                "max_overflow": 20,
            },
            logging={
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "engine.log",
            },
            agent_defaults={
                "model": "claude-3.5-sonnet",
                "temperature": 0.7,
                "max_tokens": 4096,
            },
            monitoring={
                "enabled": True,
                "metrics_port": 9090,
                "health_check_interval": 30,
            },
        )

        if file_path:
            self.save_config(default_config, file_path)

        return default_config


# Global configuration manager instance
config_manager = ConfigManager()


def load_config(
    config_file: Optional[Union[str, Path]] = None,
) -> EngineConfig:
    """Load configuration (convenience function)."""
    return config_manager.load_config(config_file)


def save_config(config: EngineConfig, file_path: Optional[Union[str, Path]] = None):
    """Save configuration (convenience function)."""
    config_manager.save_config(config, file_path)


def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value (convenience function)."""
    return config_manager.get(key, default)


def set_config_value(key: str, value: Any):
    """Set configuration value (convenience function)."""
    config_manager.set(key, value)


def show_config():
    """Show current configuration (convenience function)."""
    config_manager.show_config()


def create_default_config(
    file_path: Optional[Union[str, Path]] = None,
) -> EngineConfig:
    """Create default configuration (convenience function)."""
    return config_manager.create_default_config(file_path)
