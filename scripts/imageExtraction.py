import skimage
import matplotlib.pyplot as plt
from PIL import Image
from shapely.geometry import Point, Polygon
import numpy as np

testFiles = ["Miner's Boots", "Carpenter's Boots", "Paladin's Boots", "Paladin's Gauntlets",
             "Snowman Hands", "Miner's Mitts"]

for file in testFiles:
    fullImage = skimage.io.imread(f"../data/{file}.png")
    img = Image.fromarray(fullImage)
    w, h = img.size
    zoom = 4
    fullImage = np.array(img.resize((zoom*w, zoom*h), Image.LANCZOS))
    image = fullImage[..., 0]
    fix, ax = plt.subplots()
    contours = skimage.measure.find_contours(image, level=150)
    poly = None
    maxindex = -1
    areamax = -1
    dis = 0.3
    for i in range(len(contours)):
        poly = Polygon(contours[i]).buffer(distance=dis)
        if poly.contains(Point(image.shape[0]/2, image.shape[1]/2)) and not \
                (poly.contains(Point(zoom*5, image.shape[1]/2))
                 and poly.contains(Point(image.shape[0]/2 - zoom*5, image.shape[1]/2))
                 and poly.contains(Point(image.shape[0]/2, zoom*5))
                 and poly.contains(Point(image.shape[0]/2, image.shape[1]/2 - zoom*5))):
            if poly.area > areamax:
                areamax = poly.area
                maxindex = i
    contour = contours[maxindex]
    poly = Polygon(contour).buffer(distance=dis)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            p = Point(i, j)
            if not poly.contains_properly(p):
                fullImage[i][j] = (255, 255, 255, 0)

    finished = Image.fromarray(fullImage).resize((w, h), Image.LANCZOS)
    ax.imshow(finished)
    finished.save(f"../data/{file}_processed.png")
