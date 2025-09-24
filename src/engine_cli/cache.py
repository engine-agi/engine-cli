"""CLI Performance Cache - Cache system for CLI commands and modules."""
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


class CLICache:
    """Cache system for CLI performance optimization."""

    def __init__(self, cache_dir: Optional[str] = None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".engine" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.commands_cache_file = (
            self.cache_dir / "commands.json"
        )
        self.modules_cache_file = self.cache_dir / "modules.json"

    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of a file for cache invalidation."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (FileNotFoundError, OSError):
            return ""

    def _load_cache(self, cache_file: Path) -> Dict[str, Any]:
        """Load cache from file."""
        try:
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
        return {}

    def _save_cache(self, cache_file: Path, data: Dict[str, Any]) -> None:
        """Save cache to file."""
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def get_command_info(self, command_name: str) -> Optional[Dict[str, Any]]:
        """Get cached command information."""
        cache = self._load_cache(self.commands_cache_file)
        return cache.get(command_name)

    def set_command_info(self, command_name: str, info: Dict[str, Any]) -> None:
        """Cache command information."""
        cache = self._load_cache(self.commands_cache_file)
        cache[command_name] = info
        self._save_cache(self.commands_cache_file, cache)

    def get_module_hash(self, module_name: str) -> Optional[str]:
        """Get cached module hash."""
        cache = self._load_cache(self.modules_cache_file)
        return cache.get(f"{module_name}_hash")

    def set_module_hash(self, module_name: str, file_hash: str) -> None:
        """Cache module hash."""
        cache = self._load_cache(self.modules_cache_file)
        cache[f"{module_name}_hash"] = file_hash
        self._save_cache(self.modules_cache_file, cache)

    def is_module_changed(self, module_name: str, module_file: str) -> bool:
        """Check if module file has changed since last cache."""
        cached_hash = self.get_module_hash(module_name)
        current_hash = self._get_file_hash(module_file)
        return cached_hash != current_hash

    def clear_cache(self) -> None:
        """Clear all caches."""
        try:
            if self.commands_cache_file.exists():
                self.commands_cache_file.unlink()
            if self.modules_cache_file.exists():
                self.modules_cache_file.unlink()
        except OSError:
            pass


# Global cache instance
cli_cache = CLICache()
