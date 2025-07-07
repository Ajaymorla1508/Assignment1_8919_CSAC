# 🔐 Flask Auth0 Secure App with Azure Monitoring

This project demonstrates how to secure a Python Flask web app using Auth0 and monitor authenticated user activity via Azure Monitor and KQL.

Built as part of **CST8919 – Assignment 1: Securing and Monitoring an Authenticated Flask App**.

---

## 🚀 Features

- Auth0 Single Sign-On (SSO)
- `/login`, `/callback`, `/logout`, and protected `/protected` route
- Structured logging for:
  - Successful logins
  - Access to protected route
  - Unauthorized access attempts
- Logs forwarded to Azure Monitor (Log Analytics)
- KQL-based detection of excessive `/protected` access
- Email alerts for suspicious behavior (via Azure Alerts)

---

## 🔧 Setup Instructions

### 🛠️ 1. Auth0 Setup
- Create a new application in [Auth0 Dashboard](https://manage.auth0.com/)
- **Allowed Callback URLs**:
http://localhost:5000/callback
https://ajay-flask-auth0-secure-app.azurewebsites.net/callback

- **Allowed Logout URLs**:
- https://ajay-flask-auth0-secure-app.azurewebsites.net

- Add your credentials to `.env` (see `.env.example`)

### 🔧 2. Azure Deployment
- Deployed to Azure App Service:  
`https://ajay-flask-auth0-secure-app.azurewebsites.net`
- AppService console logs forwarded to Log Analytics Workspace
- App settings include:
- `APP_ENV=production`
- `LOG_LEVEL=info`

---

## 📊 Monitoring & Alerts

### ✅ Logging Format
In `app.py`, logs are emitted as:
```python
app.logger.info(f"DEBUG user object: {user_info}")
```

## KQL Query for AppServiceConsoleLogs

```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(15m)
| where ResultDescription has "DEBUG user object:"
| parse ResultDescription with * "'email': '" email:string "'," * "'sub': '" user_id:string "'"
| summarize access_count = count() by user_id, email
| where access_count > 10
| project user_id, email, access_count
```
### Azure Alert Rule Configuration
Condition: Result count > 0
Frequency: Every 5 minutes
Severity: 3 (Low)
Notification: Email via Action Group

## 🧪 Test Script
You can simulate route hits with:
```python
for i in {1..12}; do
  curl -s https://ajay-flask-auth0-secure-app.azurewebsites.net/protected > /dev/null
done
```
### test-app.http

### Access protected route (unauthorized)
GET https://ajay-flask-auth0-secure-app.azurewebsites.net/protected

### Access protected route (authorized, manual browser login required)
GET https://ajay-flask-auth0-secure-app.azurewebsites.net/protected

### File Structure
├── app.py
├── requirements.txt
├── .env.example
├── test-app.http
└── README.md

---
## Demo Video

[Watch the 5-minute demo on YouTube](https://www.youtube.com/watch?v=hAxia1WSjkw)

---
## Reflection:

What worked well: Integration between Flask, Auth0, and Azure logging was smooth. The alerting logic worked as expected after tuning the KQL.

Improvements: Would improve token-based route access and move logs to a structured JSON format for easier parsing

---

## Author
Ajay Morla


