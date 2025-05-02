import requests
from django.conf import settings
from datetime import datetime

def send_otp_via_kaveneghar(phone, otp):
    try:
        url = f"https://api.kavenegar.com/v1/{settings.KAVEHNEGAR_API_KEY}/verify/lookup.json"
        
        params = {
            'receptor': phone,
            'template': settings.KAVEHNEGAR_OTP_TEMPLATE,
            'token': otp,
            'type': 'sms'
        }
        
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        return True
    except Exception as e:
        print(f"Error in sending OTP via Kavenegar: {e}")
        return False