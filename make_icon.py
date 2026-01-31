from PIL import Image

img = Image.open("assets/quick duka.png")
img.save(
    "assets/duka_icon.ico",
    sizes=[(16,16),(32,32),(48,48),(256,256)]
)
