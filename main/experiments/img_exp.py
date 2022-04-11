from PIL import Image

im = Image.open('locator.png', 'r')
pix = im.load()
print(pix[0, 0])
print(pix[1889, 0])
print(pix[0, 1416])
print(pix[1889, 1416])
print(im.size)