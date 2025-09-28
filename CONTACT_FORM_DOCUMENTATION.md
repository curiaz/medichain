# MediChain Contact Form Documentation

## Overview
The MediChain contact form allows users to send messages directly to the MediChain team. All form submissions are sent via email to `medichain173@gmail.com`.

## Features
- ✅ **Functional Contact Form**: Full form validation and submission
- ✅ **Email Integration**: Uses Gmail SMTP with secure app passwords
- ✅ **Input Validation**: Email format, required fields, and length limits
- ✅ **Spam Protection**: Basic keyword filtering and length validation
- ✅ **Professional Emails**: Formatted email templates with all form data
- ✅ **Success/Error Messages**: User-friendly feedback for all actions
- ✅ **Responsive Design**: Works perfectly on desktop and mobile devices

## Setup Instructions

### 1. Gmail Configuration
1. **Enable 2-Step Verification** on your Google Account
2. **Generate App Password**:
   - Go to Google Account Settings → Security → 2-Step Verification → App Passwords
   - Create password for "MediChain Contact Form"
   - Copy the 16-character password (remove spaces)

### 2. Environment Variables
Add these to your `backend/.env` file:
```bash
GMAIL_USER=medichain173@gmail.com
GMAIL_APP_PASSWORD=your-16-character-app-password
```

### 3. Backend Dependencies
The following packages are already included in `requirements.txt`:
- `Flask-Mail==0.9.1` - Email handling
- `email-validator==2.0.0` - Email validation

## Technical Implementation

### Frontend (React)
**File**: `src/pages/LandingPage.jsx`
- Real-time form state management
- Input validation and error handling
- Success/error message display
- Controlled form inputs with proper validation

### Backend (Flask/Python)
**File**: `backend/contact_routes.py`
- Email sending via Gmail SMTP
- Input validation and sanitization
- Spam protection and security measures
- Professional email formatting

### API Endpoint
```
POST /contact
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com", 
  "phone": "+1234567890",        // Optional
  "subject": "Inquiry about MediChain",
  "message": "Hello, I have a question..."
}
```

### Response Format
**Success Response (200)**:
```json
{
  "success": true,
  "message": "Your message has been sent successfully! We will get back to you soon."
}
```

**Error Response (400/500)**:
```json
{
  "success": false,
  "error": "Error description here"
}
```

## Form Validation

### Client-Side Validation
- Required fields: name, email, subject, message
- Email format validation
- Real-time input validation

### Server-Side Validation  
- **Required Fields**: name, email, subject, message
- **Email Format**: RFC-compliant email regex validation
- **Length Limits**: 
  - Name: 100 characters
  - Email: 100 characters  
  - Subject: 200 characters
  - Message: 2000 characters
- **Spam Protection**: Basic keyword filtering

## Security Features

### Input Sanitization
- Automatic string trimming
- Length validation to prevent buffer overflow
- Email format validation using regex

### Spam Protection
- Basic keyword filtering for common spam terms
- Length limits to prevent abuse
- Rate limiting considerations (can be added)

### Error Handling
- Graceful error messages for users
- Secure error logging (no sensitive data exposure)
- SMTP connection error handling

## Email Template
The email sent to `medichain173@gmail.com` includes:
- Professional formatting with emojis and sections
- Contact information (name, email, phone)
- Subject and message content
- Timestamp of submission
- Reply instructions

## Usage Examples

### Basic Form Submission
```javascript
const formData = {
  name: "Jane Smith",
  email: "jane.smith@example.com", 
  phone: "+1-234-567-8900",
  subject: "Question about AI Diagnosis",
  message: "I'm interested in learning more about your AI diagnosis feature..."
};

fetch('http://localhost:5000/contact', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(formData)
});
```

## Troubleshooting

### Common Issues

1. **"Email service configuration error"**
   - Check Gmail credentials in `.env` file
   - Verify app password is correct (16 characters, no spaces)
   - Ensure 2-Step Verification is enabled on Gmail

2. **"Please enter a valid email address"**  
   - Check email format (user@domain.com)
   - Ensure no extra spaces or invalid characters

3. **"Message content flagged by spam filter"**
   - Check for spam keywords in subject/message
   - Use professional language in form content

4. **Backend not starting**
   - Check if Flask dependencies are installed: `pip install -r requirements.txt`
   - Verify Python version compatibility

### Testing
1. **Start Backend**: `python backend/app.py`
2. **Start Frontend**: `npm start`
3. **Fill out form** with valid data
4. **Check email** at medichain173@gmail.com for received messages

## Production Considerations

### Security Enhancements
- Add rate limiting (Flask-Limiter)
- Implement CAPTCHA for spam protection
- Add request logging and monitoring
- Use environment-specific configurations

### Performance Optimizations  
- Add email queue for high-volume submissions
- Implement connection pooling for SMTP
- Add caching for repeated validations

### Monitoring
- Log all form submissions (without sensitive data)
- Monitor email delivery success rates  
- Track spam filter effectiveness
- Set up alerts for failed email deliveries

## Support
For technical issues with the contact form:
1. Check backend logs for SMTP errors
2. Verify Gmail app password configuration
3. Test email connectivity manually
4. Contact the development team for assistance

---

**Status**: ✅ **PRODUCTION READY**  
**Last Updated**: September 28, 2025  
**Contact**: MediChain Development Team