#!/bin/bash

# CustomerGenAINews - Automated Setup Script
# This script automates the initial setup process

set -e  # Exit on any error

echo "🚀 CustomerGenAINews - Automated Setup Starting..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.11+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
            print_success "Python $PYTHON_VERSION detected"
        else
            print_error "Python 3.11+ required. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.11+"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    if [ -f "requirements-github.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements-github.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements-github.txt not found"
        exit 1
    fi
}

# Copy environment template
setup_environment() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Environment template copied to .env"
            print_warning "Please edit .env file with your OpenAI API key and other settings"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_warning ".env file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs data web
    print_success "Directories created"
}

# Check for required environment variables
check_environment() {
    print_status "Checking environment configuration..."
    source .env 2>/dev/null || true
    
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "sk-your_openai_api_key_here" ]; then
        print_warning "OpenAI API key not configured in .env file"
        print_warning "Please edit .env and add your OpenAI API key"
    else
        print_success "OpenAI API key configured"
    fi
}

# Test database connection
test_database() {
    print_status "Testing database connection..."
    if python3 -c "
from database import DatabaseManager
try:
    db = DatabaseManager()
    db.connect()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
        print_success "Database connection test passed"
    else
        print_warning "Database connection test failed - this is normal for first setup"
        print_status "Running database setup..."
        python3 setup.py
    fi
}

# Run initial setup
run_setup() {
    print_status "Running initial application setup..."
    if python3 setup.py; then
        print_success "Application setup completed"
    else
        print_error "Application setup failed"
        exit 1
    fi
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your OpenAI API key"
    echo "2. Start the web server: python3 enhanced_web_server.py"
    echo "3. Access dashboard: http://localhost:5000"
    echo "4. Login to admin panel: http://localhost:5000/admin"
    echo "   Default credentials: admin / genai2025"
    echo ""
    echo "For automated monitoring, run: python3 run_scheduler.py"
    echo ""
    echo "See docs/installation.md for detailed instructions"
}

# Main execution
main() {
    echo "CustomerGenAINews - GenAI Content Monitoring System"
    echo "=================================================="
    
    check_python
    create_venv
    activate_venv
    install_dependencies
    setup_environment
    create_directories
    check_environment
    test_database
    run_setup
    
    show_next_steps
}

# Run main function
main "$@"