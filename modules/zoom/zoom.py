from PIL import Image


def get_img_center(img):
    w, h = img.size
    return (int(w / 2), int(h / 2))


# zoom image
def img_zoom_center(img, zoom):
    w, h = img.size
    x, y = get_img_center(img)

    zoom2 = zoom * 2
    left = x - (w / zoom2)
    upper = y - (h / zoom2)
    right = x + (w / zoom2)
    lower = y + (h / zoom2)

    img_cropped = img.crop((left, upper, right, lower))
    img_resized = img_cropped.resize((w, h), Image.LANCZOS)

    return img_resized
