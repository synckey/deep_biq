"""
With this script you can finetune AlexNet as provided in the alexnet.py
class on any given dataset. 
Specify the configuration settings at the beginning according to your 
problem.
This script was written for TensorFlow 1.0 and come with a blog post 
you can find here:

https://kratzert.github.io/2017/02/24/finetuning-alexnet-with-tensorflow.html

Author: Frederik Kratzert 
contact: f.kratzert(at)gmail.com
"""
import os
import cPickle as pickle
from PIL import Image
import cv2
import numpy as np
import tensorflow as tf
from scipy.stats import pearsonr

from extract_alexnet_features import extract_one_image, get_mos
from image_processing import crop_a_image
from liblinearutil import load_model, predict
from alexnet import AlexNet

FLAGS = tf.app.flags.FLAGS

validation_dir = 'data/rawdata/validation'
m = load_model("./liblinear.model")

labels = []
preds_min = []
preds_avg = []
preds_max = []


def evaluate():
    for f_name in [os.path.join(validation_dir, f) for f in os.listdir(validation_dir)]:
        features = extract_one_image(f_name)
        pred_score = predict([], features, m, options="")[0]
        preds_min.append(np.min(pred_score))
        preds_max.append(np.max(pred_score))
        preds_avg.append(np.average(pred_score))
        mos = get_mos(f_name)
        print (mos, np.average(pred_score), np.max(pred_score), np.min(pred_score))
        labels.append(mos)
        print("avg_lcc", pearsonr(labels, preds_avg)[0], "min_lcc", pearsonr(labels, preds_min)[0], "max_lcc",
              pearsonr(labels, preds_max)[0])


def main():
    evaluate()


if __name__ == '__main__':
    main()
