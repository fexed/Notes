import os
import numpy as np
from skimage.feature import SIFT
from skimage.io import imread
from skimage.color import rgb2gray
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pickle


root = "/mnt/c/Users/fedex/Documents/Notes/UniPi_CSMaster_AI/IntelligentSystemsforPatternRecognition/assignments/midterm1/imgdataset/"
directories = [root + "img_1/", root + "img_2/", root + "img_3/", root + "img_4/"]
directories_GT = [root + "img_1_GT/", root + "img_2_GT/", root + "img_3_GT/", root + "img_4_GT/"]

sift = None
if (os.path.exists("siftdata.pkl")):
    print("SIFT already computed")
    with open("siftdata.pkl", "rb") as file:
        sift = pickle.load(file)
else:
    sift = SIFT()
    for dir in directories:
        for file in os.listdir(os.fsencode(dir)):
            print("\r" + str(file), end="")
            img = rgb2gray(imread(dir + os.fsdecode(file)))
            sift.detect_and_extract(img)
    print("")
    with open("siftdata.pkl", "wb") as file:
        pickle.dump(sift, file)

kmeans_descriptors = KMeans(n_clusters=4, init="random", n_init=10, max_iter=300, tol=1e-04, random_state=42)
kmeans_descriptors.fit(sift.descriptors)

#plt.plot(kmeans_descriptors.cluster_centers_)
#plt.savefig("test.png", bbox_inches='tight')

sift_GT = None
if (os.path.exists("siftdata_GT.pkl")):
    print("SIFT GT already computed")
    with open("siftdata_GT.pkl", "rb") as file:
        sift_GT = pickle.load(file)
else:
    sift_GT = SIFT()
    for dir in directories_GT:
        for file in os.listdir(os.fsencode(dir)):
            print("\r" + str(file), end="")
            img = rgb2gray(imread(dir + os.fsdecode(file)))
            try:
                sift_GT.detect_and_extract(img)
            except RuntimeError: continue
    print("")
    with open("siftdata_GT.pkl", "wb") as file:
        pickle.dump(sift_GT, file)

kmeans_descriptors_GT = KMeans(n_clusters=4, init="random", n_init=10, max_iter=300, tol=1e-04, random_state=42)
kmeans_descriptors_GT.fit(sift_GT.descriptors)

for center, center_GT in zip(kmeans_descriptors.cluster_centers_, kmeans_descriptors_GT.cluster_centers_):
    print(np.linalg.norm(center - center_GT))
