#!/usr/bin/env python3
"""
Contract Validation Script for Engine CLI
Validates compliance with multirepo contracts defined in contract.md

This script checks that the Engine CLI uses only public APIs from engine-core,
following the contract specifications.
"""

import os
import sys
import re
import ast
import importlib.util
from pathlib import Path
from typing import Set, List, Dict, Tuple


class ContractValidator:
    """Validates contract compliance between Engine CLI and Engine Core."""

    def __init__(self, cli_root: Path, core_root: Path):
        self.cli_root = cli_root
        self.core_root = core_root
        self.violations: List[str] = []
        self.warnings: List[str] = []

        # Public interfaces from engine-core __init__.py
        self.public_interfaces = self._load_public_interfaces()

        # Forbidden import patterns
        self.forbidden_patterns = [
            r'from engine_core\.core\.',  # Direct internal imports
            r'import engine_core\.core\.',  # Direct internal imports
        ]

    def _load_public_interfaces(self) -> Set[str]:
        """Load public interfaces from engine-core __init__.py"""
        init_file = self.core_root / "src" / "engine_core" / "__init__.py"

        if not init_file.exists():
            self.violations.append(f"Engine core __init__.py not found: {init_file}")
            return set()

        try:
            spec = importlib.util.spec_from_file_location("engine_core", init_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get __all__ if it exists
                if hasattr(module, '__all__'):
                    return set(module.__all__)
                else:
                    self.warnings.append("engine-core __init__.py has no __all__ defined")
                    return set()
            else:
                self.violations.append(f"Could not load engine-core __init__.py")
                return set()
        except Exception as e:
            self.violations.append(f"Error loading engine-core __init__.py: {e}")
            return set()

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in CLI source"""
        src_dir = self.cli_root / "src"
        if not src_dir.exists():
            self.violations.append(f"CLI src directory not found: {src_dir}")
            return []

        return list(src_dir.rglob("*.py"))

    def _check_file_imports(self, file_path: Path) -> None:
        """Check imports in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for forbidden import patterns
            for pattern in self.forbidden_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    for match in matches:
                        self.violations.append(
                            f"FORBIDDEN IMPORT in {file_path}: {match}"
                        )

            # Parse AST to check imports more precisely
            tree = ast.parse(content, filename=str(file_path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('engine_core.core.'):
                        # This is a violation - using internal modules
                        imported_items = [alias.name for alias in node.names]
                        self.violations.append(
                            f"INTERNAL IMPORT in {file_path}: "
                            f"from {node.module} import {', '.join(imported_items)}"
                        )

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('engine_core.core.'):
                            self.violations.append(
                                f"INTERNAL IMPORT in {file_path}: import {alias.name}"
                            )

        except Exception as e:
            self.warnings.append(f"Error parsing {file_path}: {e}")

    def _check_public_interface_usage(self) -> None:
        """Check that only public interfaces are used"""
        # This is a basic check - in a real implementation, you'd want
        # more sophisticated analysis of what's actually used vs imported

        # For now, just check that __version__ is accessible
        try:
            spec = importlib.util.spec_from_file_location(
                "engine_core",
                self.core_root / "src" / "engine_core" / "__init__.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if not hasattr(module, '__version__'):
                    self.violations.append("__version__ not exported from engine-core")
                else:
                    version = module.__version__
                    if not isinstance(version, str) or not version:
                        self.warnings.append(f"__version__ is not a valid string: {version}")

        except Exception as e:
            self.violations.append(f"Error checking __version__: {e}")

    def validate(self) -> bool:
        """Run all validation checks"""
        print("🔍 Validating Engine CLI contract compliance...")
        print(f"📁 CLI root: {self.cli_root}")
        print(f"📁 Core root: {self.core_root}")
        print(f"🔓 Public interfaces: {sorted(self.public_interfaces)}")
        print()

        # Check public interface availability
        self._check_public_interface_usage()

        # Find and check all Python files
        python_files = self._find_python_files()
        print(f"📄 Found {len(python_files)} Python files to check")

        for file_path in python_files:
            self._check_file_imports(file_path)

        # Report results
        print()
        print("📊 VALIDATION RESULTS")
        print("=" * 50)

        if self.violations:
            print(f"❌ VIOLATIONS FOUND: {len(self.violations)}")
            for violation in self.violations:
                print(f"  - {violation}")
        else:
            print("✅ NO VIOLATIONS FOUND")

        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  - {warning}")

        print()
        return len(self.violations) == 0


def main():
    """Main entry point"""
    # Determine paths
    script_dir = Path(__file__).parent.parent.parent  # .github/scripts/validate_contracts.py -> engine-cli/
    cli_root = script_dir
    core_root = cli_root.parent / "engine-core"  # Assume engine-core is sibling

    if not core_root.exists():
        print(f"❌ Engine core not found at {core_root}")
        print("This script should be run from engine-cli/.github/scripts/")
        sys.exit(1)

    # Run validation
    validator = ContractValidator(cli_root, core_root)
    success = validator.validate()

    if success:
        print("🎉 CONTRACT VALIDATION PASSED")
        sys.exit(0)
    else:
        print("💥 CONTRACT VALIDATION FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()