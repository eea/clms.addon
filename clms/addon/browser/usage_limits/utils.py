"""Utility functions for Usage Limits Monitor"""
from plone import api
import requests


def get_portal_config():
    """Get CDSE and S3 bucket configuration from the portal catalog"""
    return {
        'token_url': api.portal.get_registry_record(
            "clms.downloadtool.cdse_config_controlpanel.token_url"
        ),
        'client_id': api.portal.get_registry_record(
            "clms.downloadtool.cdse_config_controlpanel.client_id"
        ),
        'client_secret': api.portal.get_registry_record(
            "clms.downloadtool.cdse_config_controlpanel.client_secret"
        ),
        'account_id': api.portal.get_registry_record(
            "clms.downloadtool.cdse_config_controlpanel.account_id"
        ),
    }


def get_token():
    """Get token for CDSE"""
    config = get_portal_config()
    token_response = requests.post(config['token_url'], data={
        "grant_type": "client_credentials",
        "client_id": config['client_id'],
        "client_secret": config['client_secret']
    })

    token = token_response.json().get("access_token")
    if not token:
        raise RuntimeError("Failed to obtain token.")
    print("Token acquired successfully.")

    return token


def get_customer_account_id():
    """Get customer account id for CDSE"""
    token = get_token()
    config = get_portal_config()

    customer_account_id = requests.get(
        f"https://sh.dataspace.copernicus.eu/ims/projects/{config['account_id']}/info",
        headers={"Authorization": f"Bearer {token}"})

    return customer_account_id.json().get("customerAccount")["id"]


def get_usage():
    """Get usage limits for CDSE"""
    token = get_token()
    customer_id = get_customer_account_id()

    usage_limits = requests.get(
        f"https://sh.dataspace.copernicus.eu/api/v1/accounting/usage?customerAccountId={customer_id}",
        headers={"Authorization": f"Bearer {token}"})

    return usage_limits.json()
