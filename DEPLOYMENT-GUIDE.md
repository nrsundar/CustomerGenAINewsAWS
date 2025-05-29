# GenAI Monitor - AWS Serverless Deployment Guide

## 🚀 Complete AWS Migration in 3 Steps

This CloudFormation template will deploy your GenAI monitoring system with:
- **RDS PostgreSQL** for your authentic Bank of America & Goldman Sachs articles  
- **Lambda functions** for monitoring and dashboard serving
- **CloudFront CDN** for global dashboard access
- **EventBridge** for automated daily monitoring
- **Secrets Manager** for secure API key storage

**Estimated Monthly Cost: $21-28**

---

## Step 1: Prepare Parameters

Before deployment, gather these values:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `OpenAIAPIKey` | Your OpenAI API key | `sk-...` |
| `AdminUsername` | Admin panel username | `admin` |
| `AdminPassword` | Admin panel password | `genai2025` |
| `DBUsername` | Database username | `genaiuser` |
| `DBPassword` | Database password (8+ chars) | `SecurePass123!` |

---

## Step 2: Deploy via AWS CLI

```bash
# 1. Download the template
# Save aws-deployment.yaml to your local machine

# 2. Deploy the stack
aws cloudformation create-stack \
  --stack-name genai-monitor \
  --template-body file://aws-deployment.yaml \
  --parameters \
    ParameterKey=OpenAIAPIKey,ParameterValue=YOUR_OPENAI_KEY \
    ParameterKey=AdminUsername,ParameterValue=admin \
    ParameterKey=AdminPassword,ParameterValue=genai2025 \
    ParameterKey=DBUsername,ParameterValue=genaiuser \
    ParameterKey=DBPassword,ParameterValue=SecurePass123! \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 3. Monitor deployment progress
aws cloudformation describe-stacks \
  --stack-name genai-monitor \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus'
```

---

## Step 3: Deploy via AWS Console

1. **Open AWS CloudFormation Console**
   - Go to https://console.aws.amazon.com/cloudformation/
   - Select your preferred region (e.g., us-east-1)

2. **Create Stack**
   - Click "Create stack" → "With new resources"
   - Choose "Upload a template file"
   - Upload `aws-deployment.yaml`
   - Click "Next"

3. **Configure Parameters**
   - Stack name: `genai-monitor`
   - Fill in all parameters from Step 1
   - Click "Next"

4. **Configure Options**
   - Leave defaults, scroll to bottom
   - Check "I acknowledge that AWS CloudFormation might create IAM resources"
   - Click "Create stack"

5. **Wait for Completion**
   - Monitor the "Events" tab
   - Status will change to "CREATE_COMPLETE" (10-15 minutes)

---

## 📊 Post-Deployment URLs

After successful deployment, you'll get these URLs:

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard (Global)** | `https://[cloudfront-id].cloudfront.net` | Main dashboard access |
| **API Gateway** | `https://[api-id].execute-api.us-east-1.amazonaws.com/prod` | Direct API access |

---

## 🔧 Next Steps: Code Migration

Once infrastructure is deployed, I'll help you:

1. **Package your Python code** for Lambda deployment
2. **Migrate your authentic articles** from current database
3. **Update Lambda functions** with your monitoring logic
4. **Configure automated scheduling** for daily monitoring

---

## 💰 Cost Breakdown

| Service | Monthly Cost |
|---------|--------------|
| RDS PostgreSQL (t3.micro) | $13-15 |
| Lambda executions | $3-5 |
| CloudFront CDN | $2-3 |
| S3 storage | $1-2 |
| EventBridge + Secrets | $1 |
| **Total** | **$21-28** |

---

## 🚨 Important Notes

- **Data Preservation**: Your authentic Bank of America & Goldman Sachs articles will be migrated safely
- **Zero Downtime**: Current system continues running during migration
- **Scalability**: Handles traffic spikes automatically
- **Security**: Enterprise-grade with encrypted storage

---

## ⚡ Quick Deployment Commands

For fastest deployment via AWS CLI:

```bash
# Replace YOUR_OPENAI_KEY with your actual key
aws cloudformation create-stack \
  --stack-name genai-monitor \
  --template-body file://aws-deployment.yaml \
  --parameters \
    ParameterKey=OpenAIAPIKey,ParameterValue=YOUR_OPENAI_KEY \
    ParameterKey=DBPassword,ParameterValue=SecurePass123! \
  --capabilities CAPABILITY_IAM
```

Ready to deploy? Choose your preferred method (CLI or Console) and let me know when the CloudFormation stack is complete!