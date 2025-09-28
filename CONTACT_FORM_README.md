# MediChain Contact Form Setup Guide

## 📧 Contact Form Implementation

The MediChain platform includes a fully functional contact form that sends emails to `medichain173@gmail.com` using Gmail SMTP.

## 🔧 Setup Instructions

### 1. Gmail Configuration

1. **Enable 2-Step Verification** on the Gmail account (`medichain173@gmail.com`)
   - Go to [Google Account Settings](https://myaccount.google.com/)
   - Navigate to Security > 2-Step Verification

2. **Generate App Password**
   - In Security settings, go to App Passwords
   - Select "Mail" and "Other (Custom name)"
   - Name it "MediChain Contact Form" 
   - Copy the 16-character password (format: `abcd efgh ijkl mnop`)

3. **Configure Environment Variables**
   ```bash
   # Add to backend/.env file
   GMAIL_USER=medichain173@gmail.com
   GMAIL_APP_PASSWORD=your-16-character-app-password-without-spaces
   ```

### 2. Backend Setup

The backend is already configured with:
- Flask route: `POST /contact`
- Email validation and sanitization
- Error handling for SMTP issues
- Success/failure response messages

### 3. Frontend Features

The contact form includes:
- Real-time form validation
- Loading states during submission
- Success/error message display  
- Form reset after successful submission
- Consistent placeholder fonts matching design

## 📝 Form Fields

- **Name** (required): User's full name
- **Email** (required): Valid email address with pattern validation
- **Phone** (optional): User's phone number
- **Subject** (required): Message subject line
- **Message** (required): Message content with proper textarea styling

## 🔒 Security Features

- Email address validation using regex patterns
- SMTP authentication error handling
- Input sanitization and validation
- Error message standardization
- Secure environment variable storage

## 📧 Email Template

When a form is submitted, an email is sent to `medichain173@gmail.com` with:

```
Subject: New Contact Form Submission – [User Subject]

New Contact Form Submission

Date: 2025-09-28 10:30:45

Name: [User Name]
Email: [User Email]  
Phone: [User Phone or 'Not provided']
Subject: [User Subject]

Message:
[User Message Content]

---
This message was sent from the MediChain contact form.
Reply directly to this email to respond to [User Name] at [User Email].
```

## 🚀 Testing

To test the contact form:

1. **Start Backend Server**
   ```bash
   python backend/app.py
   ```

2. **Start Frontend**
   ```bash
   npm start
   ```

3. **Submit Test Message**
   - Navigate to the Contact Us section
   - Fill out all required fields
   - Click Submit
   - Check for success message and email delivery

## 🔍 Troubleshooting

### Common Issues:

1. **"Email service configuration error"**
   - Check `.env` file has correct Gmail credentials
   - Verify app password is generated and copied correctly
   - Restart backend server after updating `.env`

2. **"Email authentication failed"**
   - Verify 2-Step Verification is enabled on Gmail
   - Regenerate app password if needed
   - Check for typos in credentials

3. **SMTP connection errors**
   - Check internet connection
   - Verify Gmail SMTP settings (smtp.gmail.com:587)
   - Check firewall/antivirus blocking SMTP

### Debug Steps:

1. Check backend server logs for detailed error messages
2. Verify environment variables are loaded correctly  
3. Test with different email addresses
4. Check Gmail account for any security alerts

## 📱 Mobile Responsiveness

The contact form is fully responsive and includes:
- Proper font sizing on mobile devices
- Consistent placeholder styling
- Touch-friendly input fields
- Optimized spacing and layout

## 🎨 Styling Features

- Consistent Inter font family across all form elements
- Matching placeholder fonts with other inputs
- Success/error message styling with proper colors
- Professional form layout with proper spacing
- Hover and focus states for better UX

---

✅ **Status**: Fully functional and production-ready
📧 **Destination**: medichain173@gmail.com  
🔧 **Technology**: Flask + Gmail SMTP + React Frontend