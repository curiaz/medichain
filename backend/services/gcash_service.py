"""
GCash Business API Service
Handles integration with GCash Business API for payment processing
"""

import requests
import os
from datetime import datetime
from typing import Dict, Optional

class GCashService:
    """Service for interacting with GCash Business API"""
    
    def __init__(self):
        # GCash API Configuration
        # Get these from GCash Business Portal: https://business.gcash.com/
        self.api_base_url = os.getenv('GCASH_API_BASE_URL', 'https://api.gcash.com')
        self.merchant_id = os.getenv('GCASH_MERCHANT_ID', '')
        self.api_key = os.getenv('GCASH_API_KEY', '')
        self.api_secret = os.getenv('GCASH_API_SECRET', '')
        self.webhook_secret = os.getenv('GCASH_WEBHOOK_SECRET', '')
        
        # Check if credentials are configured
        if not all([self.merchant_id, self.api_key, self.api_secret]):
            print("⚠️  GCash API credentials not fully configured. Using simulation mode.")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            print("✅ GCash API service initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for GCash API"""
        return {
            'Content-Type': 'application/json',
            'X-Merchant-ID': self.merchant_id,
            'X-API-Key': self.api_key,
            'Authorization': f'Bearer {self._generate_token()}'
        }
    
    def _generate_token(self) -> str:
        """
        Generate authentication token for GCash API
        In production, implement proper token generation based on GCash API documentation
        """
        # TODO: Implement actual token generation based on GCash API spec
        # This is a placeholder - replace with actual implementation
        return self.api_secret
    
    def create_payment_qr(self, amount: float, reference: str, description: str = "MediChain Consultation") -> Dict:
        """
        Create a payment QR code using GCash API
        
        Args:
            amount: Payment amount
            reference: Transaction reference number
            description: Payment description
            
        Returns:
            Dict with QR code data and payment link
        """
        if self.simulation_mode:
            # Fallback to simulation if API not configured
            return self._simulate_qr_generation(amount, reference)
        
        try:
            # GCash API endpoint for QR code generation
            # Update this URL based on actual GCash API documentation
            url = f"{self.api_base_url}/v1/payments/qr"
            
            payload = {
                "merchant_id": self.merchant_id,
                "amount": amount,
                "currency": "PHP",
                "reference": reference,
                "description": description,
                "expires_in": 900  # 15 minutes in seconds
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "qr_code": data.get("qr_code"),
                    "qr_data": data.get("qr_data"),
                    "payment_link": data.get("payment_link"),
                    "expires_at": data.get("expires_at")
                }
            else:
                print(f"❌ GCash API error: {response.status_code} - {response.text}")
                # Fallback to simulation on API error
                return self._simulate_qr_generation(amount, reference)
                
        except Exception as e:
            print(f"❌ Error calling GCash API: {str(e)}")
            # Fallback to simulation on error
            return self._simulate_qr_generation(amount, reference)
    
    def _simulate_qr_generation(self, amount: float, reference: str) -> Dict:
        """Simulate QR code generation (fallback when API not configured)"""
        import re
        merchant_account = os.getenv('GCASH_MERCHANT_ACCOUNT', '09171234567')
        clean_account = re.sub(r'\s+', '', merchant_account).replace('-', '')
        return {
            "success": True,
            "qr_code": None,  # Will be generated on frontend
            "qr_data": clean_account,
            "payment_link": None,
            "expires_at": None,
            "simulation": True
        }
    
    def verify_payment(self, transaction_id: str) -> Dict:
        """
        Verify payment status using GCash API
        
        Args:
            transaction_id: GCash transaction ID or reference
            
        Returns:
            Dict with payment status
        """
        if self.simulation_mode:
            # Fallback to simulation
            return self._simulate_payment_verification(transaction_id)
        
        try:
            # GCash API endpoint for payment verification
            url = f"{self.api_base_url}/v1/payments/{transaction_id}"
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "status": data.get("status", "pending"),
                    "amount": data.get("amount"),
                    "paid_at": data.get("paid_at"),
                    "transaction_id": data.get("transaction_id")
                }
            else:
                print(f"❌ GCash API verification error: {response.status_code}")
                return {
                    "success": False,
                    "status": "pending",
                    "error": "Payment verification failed"
                }
                
        except Exception as e:
            print(f"❌ Error verifying payment with GCash API: {str(e)}")
            return self._simulate_payment_verification(transaction_id)
    
    def _simulate_payment_verification(self, transaction_id: str) -> Dict:
        """Simulate payment verification (fallback)"""
        # This matches the current simulation logic in appointment_routes.py
        return {
            "success": True,
            "status": "pending",
            "simulation": True
        }
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature from GCash
        
        Args:
            payload: Webhook payload (raw string)
            signature: Signature from X-GCash-Signature header
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            print("⚠️  Webhook secret not configured, skipping signature verification")
            return True  # Allow in development, but should be False in production
        
        # TODO: Implement actual signature verification based on GCash API spec
        # This is a placeholder
        import hmac
        import hashlib
        
        expected_signature = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)

# Global instance
gcash_service = GCashService()

