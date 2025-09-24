#!/bin/bash
# Engine CLI Release Script v1.0.1
# This script handles the corrected release after incomplete v1.0.0

set -e

echo "🚀 Engine CLI v1.0.1 Release Script"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src/engine_cli" ]; then
    print_error "Not in engine-cli directory. Please run from engine-cli root."
    exit 1
fi

print_status "Starting release process for v1.0.1"

# Check git status
if [ -n "$(git status --porcelain)" ]; then
    print_warning "Working directory not clean. Uncommitted changes found."
    git status --short
    echo
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Release cancelled by user."
        exit 1
    fi
fi

# Verify tag exists
if ! git tag -l | grep -q "v1.0.1"; then
    print_error "Tag v1.0.1 not found. Please create it first."
    exit 1
fi

print_status "Tag v1.0.1 verified"

# Clean previous builds
print_status "Cleaning previous builds"
rm -rf dist/
rm -rf build/

# Build package
print_status "Building package v1.0.1"
poetry build

if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi

print_status "Package built successfully"

# Verify package contents
print_status "Verifying package contents"
tar -tzf dist/engine_cli-1.0.1.tar.gz | head -20

# Test package installation (optional)
read -p "Test local installation? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Testing local installation"
    pip install --force-reinstall dist/engine_cli-1.0.1-py3-none-any.whl

    if [ $? -eq 0 ]; then
        print_status "Local installation successful"

        # Quick functionality test
        print_status "Running quick functionality test"
        engine --version
        engine --help | head -5
        engine agent --help | head -3
        engine advanced cache status || true

        print_status "Functionality test completed"
    else
        print_error "Local installation failed"
        exit 1
    fi
fi

# Upload to PyPI
print_warning "Ready to upload to PyPI"
echo "This will upload engine-cli v1.0.1 to PyPI"
echo "Package files:"
ls -la dist/
echo

read -p "Proceed with PyPI upload? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Uploading to PyPI..."

    if poetry publish; then
        print_status "Successfully published to PyPI!"
        print_status "Release v1.0.1 completed!"
        echo
        echo "📦 Package URL: https://pypi.org/project/engine-cli/1.0.1/"
        echo "📋 Release Notes:"
        echo "  - Complete CLI documentation (T046)"
        echo "  - Performance optimizations (T047)"
        echo "  - Lazy loading and smart caching"
        echo "  - Startup time < 2s (achieved: ~0.35s)"
    else
        print_error "PyPI upload failed"
        echo "Please check your PyPI credentials and try again."
        echo "You can also upload manually using twine:"
        echo "  pip install twine"
        echo "  twine upload dist/*"
        exit 1
    fi
else
    print_warning "PyPI upload cancelled"
    echo "You can upload manually later with:"
    echo "  poetry publish"
    echo "or"
    echo "  twine upload dist/*"
fi

print_status "Release script completed"
echo
echo "🎉 Engine CLI v1.0.1 is ready!"
echo "   This corrects the incomplete v1.0.0 release."
