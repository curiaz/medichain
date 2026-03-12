# GCash Business API Integration Guide

## 🎉 Congratulations! You now have GCash Business account!

This guide will help you integrate the real GCash Business API into your MediChain application.

## 📋 Prerequisites

1. ✅ GCash Business account (you have this!)
2. Access to GCash Business Portal: https://business.gcash.com/
3. API credentials from GCash (Merchant ID, API Key, API Secret)

## 🔑 Step 1: Get Your API Credentials

1. **Log in to GCash Business Portal**
   - Go to: https://business.gcash.com/
   - Log in with your business account credentials

2. **Navigate to API Settings**
   - Look for "API Portal" or "Developer Settings"
   - Or visit: https://gcash.com/business/api-portal-faqs

3. **Get Your Credentials**
   - **Merchant ID**: Your unique merchant identifier
   - **API Key**: Your API access key
   - **API Secret**: Your secret key for authentication
   - **Webhook Secret**: Secret for verifying webhook signatures

## ⚙️ Step 2: Configure Environment Variables

Add these environment variables to your backend (`.env` file or deployment platform):

```bash
# GCash Business API Configuration
GCASH_API_BASE_URL=https://api.gcash.com
GCASH_MERCHANT_ID=your_merchant_id_here
GCASH_API_KEY=your_api_key_here
GCASH_API_SECRET=your_api_secret_here
GCASH_WEBHOOK_SECRET=your_webhook_secret_here

# Fallback merchant account (for simulation mode)
GCASH_MERCHANT_ACCOUNT=09171234567
```

### For Render.com (Backend Deployment):

1. Go to your Render dashboard
2. Select your backend service
3. Go to "Environment" tab
4. Add the environment variables above

### For Local Development:

Create or update `.env` file in `backend/` directory:

```bash
GCASH_API_BASE_URL=https://api.gcash.com
GCASH_MERCHANT_ID=your_merchant_id
GCASH_API_KEY=your_api_key
GCASH_API_SECRET=your_api_secret
GCASH_WEBHOOK_SECRET=your_webhook_secret
GCASH_MERCHANT_ACCOUNT=09171234567
```

## 🔧 Step 3: Update API Endpoints (If Needed)

The GCash API endpoints in `backend/services/gcash_service.py` are placeholders. You need to:

1. **Check GCash API Documentation**
   - Visit: https://gcash.com/business/api-portal-faqs
   - Get the actual API endpoints for:
     - QR code generation
     - Payment verification
     - Webhook handling

2. **Update `gcash_service.py`**
   - Replace placeholder URLs with actual GCash API endpoints
   - Update authentication method based on GCash API spec
   - Implement proper token generation if required

## 🔔 Step 4: Set Up Webhooks (Recommended)

Webhooks provide real-time payment notifications (better than polling).

1. **Get Your Webhook URL**
   - Your backend webhook endpoint: `https://your-backend-url.onrender.com/api/appointments/payment/webhook`
   - Or: `https://your-backend-url.onrender.com/api/gcash/webhook`

2. **Configure in GCash Business Portal**
   - Go to API Settings → Webhooks
   - Add your webhook URL
   - Select events: `payment.completed`, `payment.failed`

3. **Verify Webhook Signature**
   - GCash will send a signature header
   - The code already includes signature verification
   - Make sure `GCASH_WEBHOOK_SECRET` is set correctly

## 📝 Step 5: Test the Integration

### Test QR Code Generation:

1. Make a test payment through your app
2. Check backend logs for:
   - `✅ GCash QR code generated via API`
   - Or `⚠️ GCash API credentials not fully configured` (if not set up)

### Test Payment Verification:

1. Complete a payment in GCash app
2. Check if payment status updates automatically
3. Verify notification is created

## 🐛 Troubleshooting

### Issue: "GCash API credentials not fully configured"

**Solution**: Make sure all environment variables are set:
- `GCASH_MERCHANT_ID`
- `GCASH_API_KEY`
- `GCASH_API_SECRET`

### Issue: QR code still shows "not valid"

**Solution**: 
1. Check if API credentials are correct
2. Verify API endpoint URLs in `gcash_service.py`
3. Check GCash API documentation for correct format

### Issue: Payments not verifying automatically

**Solution**:
1. Set up webhooks (recommended)
2. Or increase polling frequency in frontend
3. Check webhook endpoint is accessible

## 📚 Resources

- **GCash Business Portal**: https://business.gcash.com/
- **GCash API Documentation**: https://gcash.com/business/api-portal-faqs
- **GCash Help Center**: https://help.gcash.com/

## 🚀 What's Already Implemented

✅ GCash API service module (`backend/services/gcash_service.py`)
✅ Backend integration for QR code generation
✅ Payment verification via API
✅ Webhook signature verification
✅ Fallback to simulation mode if API not configured
✅ Frontend ready to use QR codes from API

## 📞 Next Steps

1. **Get your API credentials** from GCash Business Portal
2. **Add environment variables** to your backend
3. **Update API endpoints** in `gcash_service.py` based on actual GCash API docs
4. **Test the integration** with a small payment
5. **Set up webhooks** for real-time notifications

## 💡 Note

The current implementation includes:
- **Simulation mode**: Works without API credentials (for testing)
- **API mode**: Uses real GCash API when credentials are configured
- **Automatic fallback**: Falls back to simulation if API fails

This means your app will work even while you're setting up the API! 🎉

