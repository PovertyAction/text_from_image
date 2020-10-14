# Improting Image class from PIL module
from PIL import Image
import os

def crop_php(image_path):
    im = Image.open(os.path.abspath(image_path))
    # img = img.convert("RGB")

    # Size of the image in pixels (size of orginal image)
    # (This is not mandatory)
    width, height = im.size

    # Setting the points for cropped image
    left = 50
    top = 500
    right = 300
    bottom = 570

    # Cropped image of above dimension
    # (It will not change orginal image)
    im1 = im.crop((left, top, right, bottom))

    # Shows the image in image viewer
    return im1


if __name__ == '__main__':
     crop_image('.\\test\\09-20-20_CC0D084782C5.JPG')
