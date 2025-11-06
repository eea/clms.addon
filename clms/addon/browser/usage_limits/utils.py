"""Utility functions for Usage Limits Monitor"""
import requests

from clms.downloadtool.api.services.cdse.cdse_integration import (
    get_token, get_portal_config)


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
