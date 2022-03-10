import os
import numpy as np
from skimage.feature import SIFT
from skimage.io import imread
from skimage.color import rgb2gray
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt


root = "/mnt/c/Users/fedex/Documents/Notes/UniPi_CSMaster_AI/IntelligentSystemsforPatternRecognition/assignments/midterm1/imgdataset/"
#directories = [root + "img_1/", root + "img_2/", root + "img_3/", root + "img_4/"]
directories = [root + "img_1/"]
sift = SIFT()

for dir in directories:
    for file in os.listdir(os.fsencode(dir)):
        print("\r" + str(file), end="")
        img = rgb2gray(imread(dir + os.fsdecode(file)))
        sift.detect_and_extract(img)

print("")
print("descriptors: " + str(sift.descriptors.shape))
plt.imshow(plt.imread(directories[0] + "1_11_s.bmp"))
# plot the centroids
plt.scatter(
    sift.keypoints[:, 1], sift.keypoints[:, 0],
    label='keypoints'
)
plt.legend(scatterpoints=1)
plt.grid()
plt.show()
plt.savefig("keypoints.png")

kmeans = KMeans(n_clusters=25, init="random", n_init=10, max_iter=500, tol=1e-05, random_state=42)
y_km = kmeans.fit(sift.keypoints)

plt.clf()
plt.imshow(plt.imread(directories[0] + "1_11_s.bmp"))
# plot the centroids
plt.scatter(
    kmeans.cluster_centers_[:, 1], kmeans.cluster_centers_[:, 0],
    s=100, marker='*',
    label='centroids'
)
plt.legend(scatterpoints=1)
plt.grid()
plt.show()
plt.savefig("test.png")
