from skimage.future.graph import ncut
import cv2
import numpy as np


orig_img = cv2.imread('imgdataset/1_9_s.bmp')
img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2HSV)
h, w, c = img.shape

iter = 10
prior = 2
double_step = False
n_superpixels = 200
n_levels = 10
n_bins = 10

seeds = cv2.ximgproc.createSuperpixelSEEDS(w, h, c, n_superpixels, n_levels, prior, n_bins)
color_img = np.zeros((h, w, 3), np.uint8)
color_img[:] = (0, 0, 255)
seeds.iterate(img, iter)

labels = seeds.getLabels()
labels &= (1 << 2) - 1
labels *= 1 << (16 - 2)
mask = seeds.getLabelContourMask(False)

mask_inv = cv2.bitwise_not(mask)
result_bg = cv2.bitwise_and(orig_img, orig_img, mask = mask_inv)
result_fg = cv2.bitwise_and(img, orig_img, mask = mask)
result = cv2.add(result_bg, result_fg)

cv2.imwrite('mask.jpg', mask)
cv2.imwrite('result.jpg', result)

out = color.label2rgb(labels, orig_img, kind='avg', bg_label=0)
