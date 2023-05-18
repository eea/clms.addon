def scaleSingleFrame(
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
            image = image.convert("P")

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