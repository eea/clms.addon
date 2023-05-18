"""
Patch the image scale generation not to convert to image to a web Palette
"""
# -*- coding: utf-8 -*-
from logging import getLogger

import PIL.Image
from plone.scale import scale
from plone.scale.scale import scalePILImage


def own_scaleSingleFrame(
    image,
    width,
    height,
    mode,
    format_,
    quality,
    direction,
):
    image = scalePILImage(image, width, height, mode, direction=direction)

    # convert to simpler mode if possible
    colors = image.getcolors(maxcolors=256)
    if image.mode not in ("P", "L") and colors:
        if format_ == "JPEG":
            # check if it's all grey
            if all(rgb[0] == rgb[1] == rgb[2] for c, rgb in colors):
                image = image.convert("L")
        elif format_ in ("PNG", "GIF"):
            # When left emptye, the palette parameter takes the
            # PIL.Image.Palette.WEB value
            # which creates quality loss with some PNG files
            image = image.convert("P", palette=PIL.Image.Palette.ADAPTIVE)

    if image.mode == "RGBA" and format_ == "JPEG":
        extrema = dict(zip(image.getbands(), image.getextrema()))
        if extrema.get("A") == (255, 255):
            # no alpha used, just change the mode, which causes the alpha band
            # to be dropped on save
            image.mode = "RGB"
        else:
            # switch to PNG, which supports alpha
            format_ = "PNG"

    return image, format_


scale.scaleSingleFrame = own_scaleSingleFrame
log = getLogger(__name__)
log.info(
    "Patched plone.scale.scale.scaleImage not to convert PNG and GIF files to"
    " a web palette"
)
