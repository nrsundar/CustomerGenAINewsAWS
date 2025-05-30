# Installation Guide - CustomerGenAINews

This guide covers multiple installation methods for the CustomerGenAINews monitoring system.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key (required for content analysis)
- PostgreSQL database (recommended) or SQLite for development

## Method 1: Local Development Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements-github.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Required: OPENAI_API_KEY
# Optional: DATABASE_URL, email settings
```

### Step 5: Setup Database

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS (with Homebrew):
brew install postgresql

# Create database
sudo -u postgres createdb genai_monitor
sudo -u postgres createuser genaiuser

# Set password for user
sudo -u postgres psql -c "ALTER USER genaiuser PASSWORD 'your_password';"
```

#### SQLite (Development)
```bash
# No setup needed, database file will be created automatically
# Update .env file:
DATABASE_URL=sqlite:///genai_monitor.db
```

### Step 6: Run Initial Setup

```bash
python setup.py
```

### Step 7: Start the Application

```bash
# Start web server
python enhanced_web_server.py

# In another terminal, start monitoring (optional)
python run_scheduler.py
```

Visit `http://localhost:5000` to access the dashboard.

## Method 2: Docker Deployment

### Prerequisites
- Docker and Docker Compose installed

### Step 1: Clone and Configure

```bash
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews

# Copy and edit environment file
cp .env.example .env
# Add your OpenAI API key to .env
```

### Step 2: Deploy with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at `http://localhost:5000`.

## Method 3: AWS Serverless Deployment

### Prerequisites
- AWS CLI configured
- AWS account with appropriate permissions

### Step 1: Prepare Parameters

Gather these values before deployment:
- OpenAI API key
- Database password (8+ characters)
- Admin credentials

### Step 2: Deploy CloudFormation Stack

```bash
# Deploy using AWS CLI
aws cloudformation create-stack \
  --stack-name customer-genai-news \
  --template-body file://aws-deployment.yaml \
  --parameters \
    ParameterKey=OpenAIAPIKey,ParameterValue=YOUR_OPENAI_KEY \
    ParameterKey=DBPassword,ParameterValue=SecurePass123! \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

### Step 3: Get Dashboard URL

```bash
# Get CloudFront URL
aws cloudformation describe-stacks \
  --stack-name customer-genai-news \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
  --output text
```

## Verification

### Check Installation

```bash
# Test database connection
python -c "from database import DatabaseManager; db = DatabaseManager(); db.connect(); print('Database connected successfully')"

# Test OpenAI API
python -c "from ai_processor import AIProcessor; from config import Config; ai = AIProcessor(Config()); print('AI processor initialized successfully')"

# Test web scraping
python -c "from scraper import WebScraper; from config import Config; scraper = WebScraper(Config()); print('Web scraper initialized successfully')"
```

### Access Dashboard

1. Open your browser to the application URL
2. Navigate to `/admin` for admin panel
3. Default credentials: admin / genai2025

## Troubleshooting

### Common Issues

**Database Connection Errors**
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Verify database exists
psql -h localhost -U genaiuser -d genai_monitor -c "\dt"
```

**OpenAI API Errors**
```bash
# Test API key
python -c "
import openai
openai.api_key = 'your-api-key'
try:
    openai.models.list()
    print('OpenAI API key is valid')
except:
    print('OpenAI API key is invalid')
"
```

**Permission Errors**
```bash
# Fix file permissions
chmod +x setup.py
chmod +x run_scheduler.py
```

### Getting Help

1. Check the [troubleshooting guide](troubleshooting.md)
2. Review application logs in the `logs/` directory
3. Open an issue on GitHub with error details

## Next Steps

After successful installation:

1. Configure your company list in the admin panel
2. Test monitoring with a single company
3. Set up automated scheduling
4. Configure email notifications (optional)

See the [Configuration Reference](configuration.md) for detailed customization options.