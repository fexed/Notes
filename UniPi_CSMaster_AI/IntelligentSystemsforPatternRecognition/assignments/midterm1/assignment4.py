import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import color
from skimage.future import graph
from skimage.metrics import structural_similarity


def get_superpixels(image, iter = 10, prior = 5, n_superpixels = 350, n_levels = 20, n_bins = 20, print_intermediate=True, intermediate_name='result.jpg'):
    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    height, width, channels = converted_image.shape
    mask_img = np.zeros((height, width, 3), np.uint8)
    mask_img[:] = (255, 255, 255)
    seeds = cv2.ximgproc.createSuperpixelSEEDS(width, height, channels, n_superpixels, n_levels, prior, n_bins)
    seeds.iterate(converted_image, iter)
    labels = seeds.getLabels()
    mask = seeds.getLabelContourMask(False)

    if (print_intermediate):
        mask_inv = cv2.bitwise_not(mask)
        result_bg = cv2.bitwise_and(image, image, mask = mask_inv)
        result_fg = cv2.bitwise_and(mask_img, mask_img, mask = mask)
        result = cv2.add(result_bg, result_fg)
        cv2.imwrite(intermediate_name, result)

    return labels


def ncut(image, labels):
    rag = graph.rag_mean_color(image, labels, mode='similarity', sigma=512.0)
    new_labels = graph.ncut(labels, rag)
    return new_labels


def save_segmentation(image, labels, name='ncut.jpg'):
    color_list = [(128,0,0), (0,128,0), (128,128,0), (0,0,128), (128,0,128), (0,128,128), (128,128,128), (64,0,0), (192,0,0), (64,128,0), (192,128,0), (64,0,128), (192,0,128)]
    out = color.label2rgb(labels, image, kind='overlay', bg_color=(0,0,0), colors=color_list, alpha=1)
    cv2.imwrite(name, out)


def compare(image1, image2):
    return structural_similarity(image1, image2, channel_axis=2, gradient=False, full=False, multichannel=True)


def save_SSIM_image(image1, image2, filename):
    img = structural_similarity(image1, image2, channel_axis=2, gradient=False, full=True, multichannel=True)[1]
    img = (img*255).astype("uint8")
    cv2.imwrite(filename, img)


for imagefile in os.listdir(path="imgdataset/"):
    if (imagefile[-6:] != "GT.bmp"):
        if not os.path.exists("computedset/img_" + imagefile[0] + "_segm"): os.mkdir("computedset/img_" + imagefile[0] + "_segm")
        if not os.path.exists("computedset/img_" + imagefile[0] + "_interm"): os.mkdir("computedset/img_" + imagefile[0] + "_interm")
        print("\rSegmenting " + imagefile[:-4], end=" ")
        image = cv2.imread("imgdataset/" + imagefile)
        labels = get_superpixels(image, intermediate_name="computedset/img_" + imagefile[0] + "_interm/" + imagefile)
        new_labels = ncut(image, labels)
        save_segmentation(image, new_labels, name = "computedset/img_" + imagefile[0] + "_segm/" + imagefile)
print("Segmentation ended")
print("Computing differences with ground truths")
result = {}
for dir in os.listdir(path="computedset/"):
    if (dir[-4:] == "segm"):
        for imagefile in os.listdir(path="computedset/" + dir):
            print("\rComparing " + imagefile[:-4], end=" ")
            image1 = cv2.imread("computedset/" + dir + "/" + imagefile)
            image2 = cv2.imread("imgdataset/" + imagefile[:-4] + "_GT.bmp")
            metric_value = compare(image1, image2)
            result[imagefile[:-4]] = metric_value
result = {k:v for k, v in sorted(result.items(), key = lambda item : item[1], reverse=True)}
per_class = [0, 0, 0, 0, 0, 0, 0, 0]
for k in result:
    per_class[int(k[0]) - 1] += result[k]
print("")
print("Mean metric per class")
for i in range(8):
    per_class[i] /= 30
    print("\tClass " + str(i+1) + "\t" + str(per_class[i]))

print("Top 5")
if not os.path.exists("computedset/top"): os.mkdir("computedset/top")
i = 0
for k in result:
    print("\t" + k + "\t" + str(result[k]))
    image1 = cv2.imread("computedset/img_" + k[0] + "_segm/" + k + ".bmp")
    image2 = cv2.imread("imgdataset/" + k + "_GT.bmp")
    img = save_SSIM_image(image1, image2, "computedset/top/" + k + "_ssim.bmp")
    i += 1
    if i == 5: break

result = {k:v for k, v in sorted(result.items(), key = lambda item : item[1], reverse=False)}
print("Flop 5")
if not os.path.exists("computedset/flop"): os.mkdir("computedset/flop")
i = 0
for k in result:
    print("\t" + k + "\t" + str(result[k]))
    image1 = cv2.imread("computedset/img_" + k[0] + "_segm/" + k + ".bmp")
    image2 = cv2.imread("imgdataset/" + k + "_GT.bmp")
    img = save_SSIM_image(image1, image2, "computedset/flop/" + k + "_ssim.bmp")
    i += 1
    if i == 5: break
