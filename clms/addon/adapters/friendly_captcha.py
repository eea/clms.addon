"""Friendly Captcha support"""
from collective.volto.formsupport.captcha import CaptchaSupport
import requests
from plone import api


class FriendlyCaptchaSupport(CaptchaSupport):
    name = "friendly_captcha"

    def __init__(self, context, request):
        super().__init__(context, request)
        self.settings = {}

    def isEnabled(self):
        return True

    def serialize(self):
        public_key = api.portal.get_registry_record(
            "clms.addon.friendly_captcha.public_key", default="missing-config"
        )

        return {
            "provider": "friendly_captcha",
            "site_key": public_key,
            "id": "friendly_captcha",
            "title": "Friendly Captcha",
        }

    def verify(self, data):
        private_key = api.portal.get_registry_record(
            "clms.addon.friendly_captcha.private_key", default="missing-config"
        )

        token = data.get("token")
        url = "https://api.friendlycaptcha.com/api/v1/siteverify"
        secret = private_key
        payload = {"secret": secret, "solution": token}

        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"HTTP error occurred: {e}")
            return False

        result = response.json()

        return result.get("success", False)
