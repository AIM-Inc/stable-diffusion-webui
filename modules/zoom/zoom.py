from PIL import Image


def get_img_center(img):
    w, h = img.size
    return (int(w / 2), int(h / 2))


def calculate_zoom(zoom):
    if zoom < 0:
        adjusted_zoom = ((zoom + 100) / 200) - 0.5 * -1
    else:
        adjusted_zoom = (zoom / 100) + 1

    return adjusted_zoom


# zoom image
def img_zoom_center(img, zoom):
    w, h = img.size
    x, y = get_img_center(img)

    zoom2 = calculate_zoom(zoom)

    left = x - (w / zoom2)
    upper = y - (h / zoom2)
    right = x + (w / zoom2)
    lower = y + (h / zoom2)

    img_cropped = img.crop((left, upper, right, lower))
    img_resized = img_cropped.resize((w, h), Image.LANCZOS)

    return img_resized
