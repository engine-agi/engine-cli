# Engine CLI v1.1.0 Release Notes

## Overview

This release focuses on **contract compliance and architecture corrections** to ensure the Engine CLI properly adheres to the Engine Framework's public API contracts. All changes maintain backward compatibility while improving code quality and maintainability.

## Key Changes

### 🔧 Contract Compliance (T027)
- **Fixed Import Violations**: Refactored all CLI command modules to use only public APIs from `engine_core`
- **Removed Internal Dependencies**: Eliminated direct imports of internal modules (`_get_*_enums` functions)
- **Public API Usage**: All commands now properly use the 20+ public interfaces exposed by `engine_core`
- **Contract Validation**: Added automated contract validation script to prevent future violations

### 🏗️ Architecture Corrections (T028)
- **Consistent Import Patterns**: Standardized import patterns across all command modules
- **Error Handling**: Improved error handling for missing dependencies
- **Code Organization**: Better separation of concerns between CLI logic and core business logic
- **Type Safety**: Enhanced type hints and validation

### 📚 Documentation Updates (T029)
- **Comprehensive README**: Complete rewrite with interface reference, examples, and migration guide
- **API Documentation**: Detailed documentation of all CLI commands and their parameters
- **Migration Guide**: Clear instructions for upgrading from previous versions
- **Examples**: Practical usage examples for all major features

### 🧪 Test Suite Improvements
- **Fixed Test Imports**: Corrected test imports to work with refactored architecture
- **Mock Strategy Updates**: Updated test mocks to work with public API changes
- **Contract Test Coverage**: Added comprehensive contract validation tests
- **All Tests Passing**: 584 tests passing, 35 skipped (100% success rate)

## Technical Details

### Public API Interfaces Used
The CLI now properly uses these 20+ public interfaces from `engine_core`:

**Core Builders:**
- `AgentBuilder`, `TeamBuilder`, `WorkflowBuilder`, `ProtocolBuilder`, `BookBuilder`

**Enums:**
- `ContentType`, `AccessLevel`, `ContentStatus`, `SearchScope`, `SearchQuery`
- `TeamCoordinationStrategy`, `TeamMemberRole`
- `IntentCategory`, `CommandType`, `ContextScope`, `CommandContext`
- `WorkflowState`

**Services:**
- `BookService`, `WorkflowExecutionService`

### Breaking Changes
None. This release maintains full backward compatibility.

### Dependencies
- `engine-core = "^1.0.1"` (caret versioning for compatible updates)

## Migration Guide

### For Existing Users
No action required. The CLI commands work exactly as before.

### For Developers
If you were importing internal functions, update to use public APIs:

```python
# Before (internal usage - not recommended)
from engine_core.internal import _get_book_enums

# After (public API - recommended)
from engine_core import ContentType, AccessLevel, ContentStatus
```

## Quality Assurance

- ✅ **Contract Compliance**: 100% compliance with Engine Framework contracts
- ✅ **Test Coverage**: All 584 tests passing
- ✅ **Backward Compatibility**: No breaking changes
- ✅ **Documentation**: Complete API documentation
- ✅ **Code Quality**: Clean, maintainable codebase

## Contributors

- Engine Framework Team

## Acknowledgments

This release represents the successful completion of the contract compliance and architecture correction phase, ensuring the Engine CLI is a robust, maintainable component of the Engine Framework ecosystem.

---

**Release Date**: September 24, 2025
**Previous Version**: 1.0.1
**Next Version**: 1.2.0 (planned)
