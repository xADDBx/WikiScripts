import skimage
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon

testFiles = ["Miner's Boots", "Carpenter's Boots", "Paladin's Boots", "Paladin's Gauntlets",
             "Snowman Hands", "Miner's Mitts"]
testFiles = testFiles[2:]

for file in testFiles:
    fullImage = skimage.io.imread(f"../data/{file}.png")
    image = fullImage[..., 0]
    fix, ax = plt.subplots()
    contours = skimage.measure.find_contours(image, level=150)
    indexes = []
    poly = None
    areamin = -1
    for i in range(len(contours)):
        poly = Polygon(contours[i]).buffer(distance=-0.5)
        if poly.contains(Point(image.shape[0]/2, image.shape[1]/2)) \
                and not poly.contains(Point(10, image.shape[1]/2)):
            indexes.append(i)
            if areamin == -1 or poly.area < areamin:
                areamin = poly.area
    for i in indexes:
        poly = Polygon(contours[i]).buffer(distance=-0.5)
        if poly.area == areamin:
            contour = contours[i]
            break

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            p = Point(i, j)
            if not poly.contains_properly(p):
                fullImage[i][j] = (255, 255, 255, 0)

    # ax.imshow(fullImage)
    # ax.plot(contour[:, 1], contour[:, 0], linewidth=2)
    # plt.show()
    skimage.io.imsave(f"../data/{file}_processed.png", fullImage)
    # break
