# -*- coding: utf-8 -*-
import json
import random
import string

import plone.protect.interfaces
from AccessControl import getSecurityManager
from Acquisition import aq_parent
from collective.volto.formsupport.restapi.services.submit_form.post import \
    SubmitPost
from eea.meeting.browser.views import add_subscriber
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import alsoProvides


class Register(SubmitPost):
    """register the form submit"""
    def reply(self):
        if self.context.portal_type != "AnonymousForm":
            return super(Register, self).reply()
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection
            )
        subscribers = aq_parent(self.context).get("subscribers")
        anonymous_registration_allowed = self.anonymous_registration_allowed()
        if not anonymous_registration_allowed:
            self.request.response.setStatus(400)
            result = {
                "message": "Anonymous registration not allowed",
            }
            return result

        props = self.anonymous_registration_dict()
        if not props:
            self.request.response.setStatus(400)
            result = {
                "message": "Error getting anonymous user data",
            }
            return result

        try:
            self.validate(
                subscribers,
                anonymous_id=props["id"],
            )
        except Exception as e:
            self.request.response.setStatus(400)
            result = {
                "message": str(e),
            }
            return result

        try:
            add_subscriber(subscribers, **props)
        except Exception as e:
            self.request.response.setStatus(400)
            result = {
                "message": str(e),
            }
            return result

        self.request.response.setStatus(201)
        result = {
            "message": "You have succesfully registered to this meeting",
        }
        return result

    def validate(self, subscribers, anonymous_id=None):
        """validate"""
        if not subscribers:
            raise Exception("Can't find subscribers directory")
        if not self.context.can_register():
            raise Exception("Registration not allowed")
        if self.context.is_registered(uid=anonymous_id):
            raise Exception("User already registered")

    def anonymous_registration_allowed(self):
        """allowed anonymous registration"""
        eea_meeting = aq_parent(self.context)
        return eea_meeting.allow_anonymous_registration

    def get_body_data(self):
        """get body data"""
        data = json_body(self.request)
        return data

    def anonymous_registration_dict(self):
        """anonymous registration as dict"""
        try:
            data = self.get_body_data()
            anonymous_fullname = ""
            anonymous_email = ""
            fields = data.get("data")
            for field in fields:
                if (
                    "field_custom_id" in field and
                    field.get("field_custom_id") == "email"
                ):
                    anonymous_email = field.get("value", None)
                elif (
                    "field_custom_id" in field and
                    field.get("field_custom_id") == "fullname"
                ):
                    anonymous_fullname = field.get("value", None)

            uid = self.randomStringDigits()
            if anonymous_email and anonymous_fullname:
                props = dict(
                    title=anonymous_fullname,
                    id=uid,
                    userid=uid,
                    email=anonymous_email,
                    reimbursed=False,
                    role="other",
                    anonymous_extra_data=json.dumps(data),
                )
                return props
            else:
                return {}
        except:
            return {}

    def randomStringDigits(self, stringLength=8):
        """Generate a random string of letters and digits"""
        lettersAndDigits = string.ascii_letters + string.digits
        return "".join(
            random.choice(lettersAndDigits) for i in range(stringLength)
        )

    def filter_parameters(self):
        """
        do not send attachments and gdpr fields.
        """
        skip_fields = [
            x.get("field_id", "")
            for x in self.block.get("subblocks", [])
            if x.get("field_type", "") == "attachment" or
            x.get("field_custom_id", "") == "gdpr"
        ]
        return [
            x
            for x in self.form_data.get("data", [])
            if x.get("field_id", "") not in skip_fields
        ]
