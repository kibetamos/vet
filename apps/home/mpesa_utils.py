# mpesa_utils.py
import requests, base64, datetime
from django.conf import settings

def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def get_password(timestamp):
    # BusinessShortCode + Passkey + Timestamp base64 encoded
    data = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    return base64.b64encode(data.encode()).decode()

from django_daraja.mpesa.core import MpesaClient

def send_stk_push(phone, amount, account_reference, transaction_desc, callback_url):
    client = MpesaClient()
    return client.stk_push(
        phone_number=phone,
        amount=amount,
        account_reference=account_reference,
        transaction_desc=transaction_desc,
        callback_url=callback_url
    )
