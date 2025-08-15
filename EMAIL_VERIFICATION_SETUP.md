
# 📧 JobRite Email Verification Setup Guide

Your JobRite app has email verification fully implemented, but emails aren't being sent because it's using the console backend (emails only show in server logs).

## 🚀 Quick Fix Options

### Option 1: Use Gmail SMTP (Recommended)

1. **Create a Gmail App Password:**
   - Go to your Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate an app password for "JobRite"

2. **Update your Render environment variables:**
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=JobRite Team <your-email@gmail.com>
   ```

### Option 2: Use SendGrid (Free tier available)

1. **Sign up for SendGrid** (free tier: 100 emails/day)
2. **Get your API key**
3. **Update Render environment variables:**
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey
   EMAIL_HOST_PASSWORD=your-sendgrid-api-key
   DEFAULT_FROM_EMAIL=JobRite Team <noreply@yourdomain.com>
   ```

### Option 3: Use Mailgun (Free tier available)

1. **Sign up for Mailgun** (free tier: 5,000 emails/month)
2. **Get your SMTP credentials**
3. **Update Render environment variables:**
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.mailgun.org
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-mailgun-username
   EMAIL_HOST_PASSWORD=your-mailgun-password
   DEFAULT_FROM_EMAIL=JobRite Team <noreply@yourdomain.com>
   ```

## 🔧 How to Update Render Environment Variables

1. **Go to your Render dashboard**
2. **Select your JobRite service**
3. **Go to Environment tab**
4. **Add/Update the email variables above**
5. **Deploy your service**

## ✅ Testing Email Verification

After updating the email configuration:

1. **Register a new user** on your live site
2. **Check your email** (and spam folder)
3. **Click the verification link**
4. **Complete profile setup**

## 🚨 Current Status

- ✅ Email verification system: **Fully implemented**
- ✅ Email templates: **Professional and ready**
- ✅ Database models: **Working**
- ✅ Views and URLs: **Complete**
- ❌ Email sending: **Needs SMTP configuration**

## 📧 What Users Currently See

When users register, they see:
- "Please check your email to verify your account"
- But emails go to server logs instead of their inbox

## 🎯 After Email Setup

Users will receive beautiful HTML emails with:
- Welcome message
- Verification button
- Security information
- Professional JobRite branding

Choose one of the options above and your email verification will work perfectly!
