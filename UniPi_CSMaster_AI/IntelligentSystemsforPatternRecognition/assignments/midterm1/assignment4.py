import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import color
from skimage.future import graph


def get_superpixels(image, iter = 10, prior = 2, n_superpixels = 250, n_levels = 10, n_bins = 10, print_intermediate=True, intermediate_name='result.jpg'):
    converted_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    height, width, channels = converted_image.shape
    mask_img = np.zeros((height, width, 3), np.uint8)
    mask_img[:] = (255, 255, 255)
    seeds = cv2.ximgproc.createSuperpixelSEEDS(width, height, channels, n_superpixels, n_levels, prior, n_bins)
    seeds.iterate(converted_image, iter)
    labels = seeds.getLabels()

    if (print_intermediate):
        mask = seeds.getLabelContourMask(False)
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


for dir in os.listdir(path="imgdataset/"):
    if (dir[-2:] != "GT"):
        if not os.path.exists("computedset/" + dir + "_segm"): os.mkdir("computedset/" + dir + "_segm")
        if not os.path.exists("computedset/" + dir + "_interm"): os.mkdir("computedset/" + dir + "_interm")
        for imagefile in os.listdir(path="imgdataset/" + dir):
            print("\rSegmenting " + imagefile, end="")
            image = cv2.imread("imgdataset/" + dir + "/" + imagefile)
            labels = get_superpixels(image, intermediate_name="computedset/" + dir + "_interm/" + imagefile)
            new_labels = ncut(image, labels)
            save_segmentation(image, new_labels, name = "computedset/" + dir + "_segm/" + imagefile)
        print("")
"""
orig_img = cv2.imread('imgdataset/img_1/1_9_s.bmp')
labels = get_superpixels(orig_img)
new_labels = ncut(orig_img, labels)
save_segmentation(orig_img, new_labels)
"""
