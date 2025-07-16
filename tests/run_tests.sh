#!/bin/bash
# Test runner script for HeatPumpHQ MCP Server

set -e

echo "🧪 HeatPumpHQ MCP Server Test Runner"
echo "====================================="

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first."
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing dependencies..."
uv sync

# Function to run tests
run_test() {
    local env=$1
    local name=$2
    echo ""
    echo "🔬 Running $name tests..."
    echo "--------------------------------"
    
    if uv run python test_e2e.py --env $env --output "test-results-$env.json"; then
        echo "✅ $name tests passed!"
    else
        echo "❌ $name tests failed!"
        return 1
    fi
}

# Parse command line arguments
ENV=${1:-"both"}

case $ENV in
    "local")
        run_test "local" "Local Development"
        ;;
    "production")
        run_test "production" "Production"
        ;;
    "both")
        echo "🔄 Running tests against both environments..."
        
        # Test local first (if backend is running)
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            run_test "local" "Local Development"
        else
            echo "⚠️  Local backend not running, skipping local tests"
        fi
        
        # Test production
        run_test "production" "Production"
        ;;
    *)
        echo "Usage: $0 [local|production|both]"
        echo "  local      - Test against local development backend"
        echo "  production - Test against production backend"
        echo "  both       - Test against both (default)"
        exit 1
        ;;
esac

echo ""
echo "🎉 Test run complete!"
echo "📄 Check test-results-*.json for detailed results"