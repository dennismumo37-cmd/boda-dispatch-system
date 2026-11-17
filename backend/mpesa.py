import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime

# Replace these with your keys from developer.safaricom.co.ke
CONSUMER_KEY = "AG9nQERGOH6vFBiG2nxSznzpXGGakHwqfSG3oyurZXkSquER"
CONSUMER_SECRET = "cG5A34RE1fBcYwgAXSHvznsAyNqYHDlKw4YU76025tGQJcAxuxedl9ec4hUcz9Gl"
SHORTCODE = "174379"  # Safaricom Sandbox Paybill
PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2c21a830ce1a595c8284e6f6b609a722"

def get_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    return response.json().get("access_token")

def trigger_stk_push(phone_number: str, amount: int):
    """Sends an M-Pesa PIN prompt to the user's phone (e.g. phone_number='254712345678')"""
    token = get_access_token()
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(password_str.encode()).decode("utf-8")

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://your-domain.com/mpesa-callback",
        "AccountReference": "BodaStage",
        "TransactionDesc": "Daily Rider Fee or Trip Payment"
    }
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)
    return response.json()