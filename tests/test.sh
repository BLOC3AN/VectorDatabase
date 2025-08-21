#!/bin/bash

# vLLM Endpoint Testing Script
# ============================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 vLLM Endpoint Testing Suite${NC}"
echo "=================================="
echo ""

# Check if Python script exists
if [ ! -f "test_all_endpoints_complete.py" ]; then
    echo "❌ Test script not found!"
    exit 1
fi

# Parse arguments
case "${1:-full}" in
    "quick"|"-q"|"--quick")
        echo -e "${YELLOW}Running quick health checks...${NC}"
        python3 test_all_endpoints_complete.py --quick
        ;;
    "verbose"|"-v"|"--verbose")
        echo -e "${YELLOW}Running full tests with verbose output...${NC}"
        python3 test_all_endpoints_complete.py --verbose
        ;;
    "full"|""|"-f"|"--full")
        echo -e "${YELLOW}Running comprehensive tests...${NC}"
        python3 test_all_endpoints_complete.py
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [quick|verbose|full|help]"
        echo ""
        echo "Options:"
        echo "  quick     - Run only basic health checks"
        echo "  verbose   - Run full tests with detailed output"
        echo "  full      - Run comprehensive tests (default)"
        echo "  help      - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 quick     # Quick health check"
        echo "  $0 verbose   # Full test with details"
        echo "  $0           # Standard comprehensive test"
        exit 0
        ;;
    *)
        echo "❌ Unknown option: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}✅ Testing completed successfully!${NC}"
else
    echo -e "⚠️  Some tests failed. Check the output above for details."
fi

exit $exit_code
