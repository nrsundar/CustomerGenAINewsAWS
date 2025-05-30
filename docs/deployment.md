# Deployment Guide - CustomerGenAINews

Complete deployment instructions for all supported platforms.

## 🚀 AWS Serverless Deployment (Recommended)

### Cost: $21-28/month | Setup Time: 15 minutes

AWS serverless architecture provides enterprise-grade reliability with automatic scaling.

#### Prerequisites
- AWS account with administrative access
- AWS CLI installed and configured
- OpenAI API key

#### Quick Deployment

```bash
# 1. Download aws-deployment.yaml from the repository
# 2. Deploy using CloudFormation
aws cloudformation create-stack \
  --stack-name customer-genai-news \
  --template-body file://aws-deployment.yaml \
  --parameters \
    ParameterKey=OpenAIAPIKey,ParameterValue=sk-your_actual_key \
    ParameterKey=DBPassword,ParameterValue=SecurePassword123! \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 3. Monitor deployment
aws cloudformation wait stack-create-complete \
  --stack-name customer-genai-news

# 4. Get your dashboard URL
aws cloudformation describe-stacks \
  --stack-name customer-genai-news \
  --query 'Stacks[0].Outputs'
```

#### What Gets Created
- **RDS PostgreSQL**: Secure database for your articles
- **Lambda Functions**: Monitoring and dashboard serving
- **CloudFront CDN**: Global access to your dashboard
- **EventBridge**: Daily monitoring schedule
- **Secrets Manager**: Secure API key storage
- **VPC**: Isolated network environment

#### Post-Deployment
1. Access your dashboard via the CloudFront URL
2. Login with admin credentials (admin/genai2025)
3. Monitor runs automatically at 8 AM UTC daily

## 🐳 Docker Deployment

### Cost: Variable | Setup Time: 10 minutes

Perfect for VPS hosting or local development environments.

#### Prerequisites
- Docker and Docker Compose installed
- 2GB+ RAM recommended

#### Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews

# 2. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key

# 3. Deploy with Docker Compose
docker-compose up -d

# 4. Verify deployment
docker-compose ps
docker-compose logs web
```

#### Services
- **web**: Main application server
- **db**: PostgreSQL database
- **scheduler**: Automated monitoring

#### Management Commands
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
git pull
docker-compose build
docker-compose up -d

# Backup database
docker-compose exec db pg_dump -U genaiuser genaimonitor > backup.sql

# Stop all services
docker-compose down
```

## 💻 Local Development

### Cost: $0 (infrastructure) | Setup Time: 5 minutes

Best for development and testing.

#### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for testing)

#### Setup Steps

```bash
# 1. Clone and setup
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements-github.txt

# 3. Configure
cp .env.example .env
# Edit .env with your settings

# 4. Initialize database
python setup.py

# 5. Start application
python enhanced_web_server.py
```

#### Development Commands
```bash
# Run monitoring manually
python main.py

# Start scheduler
python run_scheduler.py

# Run specific components
python scraper.py  # Test web scraping
python ai_processor.py  # Test AI analysis
```

## ☁️ Cloud Platform Alternatives

### Heroku Deployment

```bash
# 1. Install Heroku CLI
# 2. Create Heroku app
heroku create your-app-name

# 3. Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# 4. Set environment variables
heroku config:set OPENAI_API_KEY=your_key
heroku config:set ADMIN_PASSWORD=your_password

# 5. Deploy
git push heroku main
```

### Google Cloud Run

```bash
# 1. Build container
docker build -t gcr.io/PROJECT_ID/customer-genai-news .

# 2. Push to registry
docker push gcr.io/PROJECT_ID/customer-genai-news

# 3. Deploy to Cloud Run
gcloud run deploy customer-genai-news \
  --image gcr.io/PROJECT_ID/customer-genai-news \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Container Instances

```bash
# 1. Create resource group
az group create --name CustomerGenAINews --location eastus

# 2. Deploy container
az container create \
  --resource-group CustomerGenAINews \
  --name customer-genai-news \
  --image your-registry/customer-genai-news \
  --dns-name-label customer-genai-news \
  --ports 5000
```

## 🔧 Configuration Management

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for content analysis |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection string |
| `ADMIN_USERNAME` | No | admin | Admin panel username |
| `ADMIN_PASSWORD` | No | genai2025 | Admin panel password |
| `WEB_SERVER_PORT` | No | 5000 | Web server port |
| `MONITORING_SCHEDULE` | No | daily | Monitoring frequency |

### Database Configuration

#### PostgreSQL (Recommended)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
```

#### SQLite (Development)
```env
DATABASE_URL=sqlite:///genai_monitor.db
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Application health
curl http://your-domain/health

# Database connection
python -c "from database import DatabaseManager; DatabaseManager().connect()"

# API connectivity
python -c "from ai_processor import AIProcessor; from config import Config; AIProcessor(Config()).is_genai_related('test')"
```

### Log Management

#### AWS CloudWatch (Serverless)
- Logs automatically collected
- View in AWS Console → CloudWatch → Log Groups

#### Docker Deployment
```bash
# View application logs
docker-compose logs web

# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f
```

#### Local Development
- Logs saved to `logs/` directory
- Configure log level in `.env`: `DEBUG_MODE=true`

### Backup Strategies

#### Database Backup
```bash
# PostgreSQL
pg_dump -h host -U user database > backup.sql

# Restore
psql -h host -U user database < backup.sql
```

#### Configuration Backup
- Backup `.env` file
- Export company data from admin panel
- Save custom configuration files

## 🔐 Security Considerations

### Production Checklist

- [ ] Change default admin credentials
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL
- [ ] Restrict database access
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Backup encryption

### Firewall Configuration

```bash
# Allow web traffic
ufw allow 80
ufw allow 443

# Restrict database access
ufw deny 5432
# Only allow from application servers
```

## 🚨 Troubleshooting

### Common Deployment Issues

**CloudFormation Stack Creation Failed**
```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name customer-genai-news

# Common causes:
# - Invalid OpenAI API key
# - Insufficient AWS permissions
# - Resource limit exceeded
```

**Docker Container Won't Start**
```bash
# Check container logs
docker-compose logs web

# Common causes:
# - Missing environment variables
# - Database connection failed
# - Port already in use
```

**Local Application Errors**
```bash
# Check Python dependencies
pip list

# Verify database connection
python -c "from database import DatabaseManager; DatabaseManager().connect()"

# Test configuration
python setup.py
```

### Getting Support

1. Check logs for specific error messages
2. Verify all environment variables are set
3. Test individual components
4. Open GitHub issue with:
   - Deployment method used
   - Error messages
   - Environment details

## 🎯 Next Steps

After successful deployment:

1. **Configure Companies**: Add your target companies in admin panel
2. **Test Monitoring**: Run manual monitoring to verify setup
3. **Schedule Automation**: Ensure daily monitoring is working
4. **Monitor Costs**: Track AWS/hosting costs
5. **Scale as Needed**: Adjust resources based on usage

Choose the deployment method that best fits your needs and infrastructure requirements!