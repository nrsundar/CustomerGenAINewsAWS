# CustomerGenAINews

An advanced Python-powered GenAI content monitoring system that tracks and analyzes AI developments across top companies in financial, retail, and media & entertainment sectors.

![Dashboard Preview](docs/images/dashboard-preview.png)

## 🚀 Features

- **Multi-Sector Monitoring**: Track 30+ corporate websites across Financial, Retail, and Media & Entertainment sectors
- **Real-Time AI Detection**: Intelligent content filtering using OpenAI-powered analysis
- **Professional Dashboard**: Comprehensive tracking with authentication and insights
- **Automated Scheduling**: Daily monitoring with email notifications
- **Serverless Architecture**: Deploy to AWS Lambda with RDS PostgreSQL
- **Vector Database Tracking**: Monitor pgvector adoption across companies
- **Authentic Data**: Real corporate GenAI announcements and developments

## 📊 Supported Companies

### Financial Sector (10 companies)
- JPMorgan Chase, Bank of America, Wells Fargo, Goldman Sachs, Morgan Stanley
- Citigroup, American Express, Charles Schwab, US Bancorp, Truist Financial

### Retail Sector (10 companies)  
- Walmart, Target, The Home Depot, Costco, Kroger
- Lowe's, Best Buy, TJX Companies, Macy's, Dollar Tree

### Media & Entertainment (10 companies)
- Disney, Netflix, Comcast, Warner Bros Discovery, Paramount Global
- Fox Corporation, Sony Pictures, AMC Entertainment, Live Nation, Spotify

## 🛠 Quick Start

### Option 1: AWS Serverless Deployment (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews

# 2. Deploy to AWS using CloudFormation
aws cloudformation create-stack \
  --stack-name customer-genai-news \
  --template-body file://aws-deployment.yaml \
  --parameters \
    ParameterKey=OpenAIAPIKey,ParameterValue=YOUR_OPENAI_KEY \
    ParameterKey=DBPassword,ParameterValue=SecurePass123! \
  --capabilities CAPABILITY_IAM

# 3. Get your dashboard URL
aws cloudformation describe-stacks \
  --stack-name customer-genai-news \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontURL`].OutputValue' \
  --output text
```

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone https://github.com/nrsundar/CustomerGenAINews.git
cd CustomerGenAINews

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your OpenAI API key and database settings

# 4. Run setup
python setup.py

# 5. Start the web server
python enhanced_web_server.py
```

Visit `http://localhost:5000` to access your dashboard.

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/genai_monitor

# Web Server Configuration
WEB_SERVER_PORT=5000
WEB_SERVER_HOST=0.0.0.0

# Admin Authentication
ADMIN_USERNAME=admin
ADMIN_PASSWORD=genai2025

# Monitoring Configuration
MONITORING_SCHEDULE=daily
EMAIL_NOTIFICATIONS=true

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Company Management

Add custom companies via the admin panel or CSV import:

```csv
name,sector,website,keywords
"Custom Corp","Technology","https://example.com/news","AI,machine learning"
```

## 🏗 Architecture

### Serverless AWS Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   EventBridge   │───▶│  Lambda Monitor  │───▶│  RDS PostgreSQL │
│  (Daily Cron)   │    │  (Content Scrape)│    │   (Articles)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CloudFront    │◄───│  Lambda Dashboard│◄───│  Secrets Manager│
│     (CDN)       │    │   (Web Server)   │    │  (API Keys)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Local Development Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   Web Scraper    │───▶│   PostgreSQL    │
│  (schedule.py)  │    │  (scraper.py)    │    │   Database      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │◄───│   AI Processor   │◄───│   OpenAI API    │
│(web_server.py)  │    │(ai_processor.py) │    │  (GPT-4o)       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🔐 Security Features

- **Authentication**: Admin panel with username/password protection
- **API Key Security**: Stored in AWS Secrets Manager
- **Database Encryption**: RDS encryption at rest
- **HTTPS**: CloudFront SSL/TLS termination
- **VPC Isolation**: Lambda functions in private subnets

## 📊 Dashboard Features

- **Real-time Monitoring**: Live corporate GenAI announcements
- **Sector Analysis**: Financial, Retail, Media & Entertainment insights
- **Trend Tracking**: Vector database adoption monitoring
- **Article Management**: Import/export capabilities
- **Authentication**: Secure admin access
- **Responsive Design**: Mobile-friendly interface

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [Configuration Reference](docs/configuration.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**nrsundar**
- GitHub: [@nrsundar](https://github.com/nrsundar)

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- AWS for serverless infrastructure
- Trafilatura for content extraction
- All corporate public websites for authentic GenAI related news/content

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Open an issue on GitHub
3. Review existing discussions

---
