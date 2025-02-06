"""
Patch collective.volto.formsupport validate_attachments to include
our custom validation in case of image file uploaded.
"""
# -*- coding: utf-8 -*-

from PIL import Image
from collective.volto.formsupport import _
from collective.volto.formsupport.restapi.services.submit_form.post import (
    SubmitPost)
from logging import getLogger
from zExceptions import BadRequest
from zope.i18n import translate
import base64
import io
import math
import os

ALLOWED_IMAGE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/jpg",
    "image/gif",
    "image/svg+xml",
    "image/tif",
    "image/tiff",
    "image/bmp",
}


def validate_image_attachment(attachment):
    """Check if the file is really an image"""
    try:
        file_data = base64.b64decode(attachment["data"])
        img = Image.open(io.BytesIO(file_data))
        img.verify()

        return True
    except Exception:
        raise ValueError("Invalid image file")


def our_validate_attachments(self):
    """Form validation of attached files"""
    # Our customization:
    attachments = self.form_data.get("attachments", {})
    for attachment in attachments.values():
        # If a file pretends to be an image, then verify that it really is
        content_type = attachment.get("content-type", "").lower()
        if content_type in ALLOWED_IMAGE_MIME_TYPES:
            validate_image_attachment(attachment)

    # Original code:  vvv
    attachments_limit = os.environ.get("FORM_ATTACHMENTS_LIMIT", "")
    if not attachments_limit:
        return
    attachments = self.form_data.get("attachments", {})
    attachments_len = 0
    for attachment in attachments.values():
        data = attachment.get("data", "")
        attachments_len += (len(data) * 3) / 4 - data.count("=", -2)
    if attachments_len > float(attachments_limit) * pow(1024, 2):
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(attachments_len, 1024)))
        p = math.pow(1024, i)
        s = round(attachments_len / p, 2)
        uploaded_str = "{} {}".format(s, size_name[i])
        raise BadRequest(
            translate(
                _(
                    "attachments_too_big",
                    default="Attachments too big. You upload ${uploaded_str},"
                    " but limit is ${max} MB. Try to compress files.",
                    mapping={
                        "max": attachments_limit,
                        "uploaded_str": uploaded_str,
                    },
                ),
                context=self.request,
            )
        )


SubmitPost.validate_attachments = our_validate_attachments
log = getLogger(__name__)

log.info(
    "Patch collective.volto.formsupport validate_attachments to include"
    " our custom validation in case of image file uploaded."
)
