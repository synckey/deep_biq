import threading
from Queue import Queue

import numpy as np
import cv2, os
import tensorflow as tf
import time

"""
This code is highly influenced by the implementation of:
https://github.com/joelthchao/tensorflow-finetune-flickr-style/dataset.py
But changed abit to allow dataaugmentation (yet only horizontal flip) and 
shuffling of the data. 
The other source of inspiration is the ImageDataGenerator by @fchollet in the 
Keras library. But as I needed BGR color format for fine-tuneing AlexNet I 
wrote my own little generator.
"""

FLAGS = tf.app.flags.FLAGS


class ImageDataGenerator:
    def __init__(self, class_list, horizontal_flip=False, shuffle=False,
                 mean=np.array([104., 117., 124.]), scale_size=(227, 227),
                 nb_classes=2, useQueue=True):

        # Init params
        self.horizontal_flip = horizontal_flip
        self.n_classes = nb_classes
        self.shuffle = shuffle
        self.mean = mean
        self.scale_size = scale_size
        self.pointer = 0
        self.read_class_list(class_list)

        if self.shuffle:
            self.shuffle_data()

    def read_class_list(self, class_list):
        """
        Scan the image file and get the image paths and labels
        """
        with open(class_list) as f:
            lines = f.readlines()
            self.images = []
            self.labels = []
            self.scores = []
            for l in lines:
                items = l.split()
                self.images.append(items[0])
                self.labels.append(int(items[1]))

            # store total number of data
            self.data_size = len(self.labels)

    def shuffle_data(self):
        """
        Random shuffle the images and labels
        """
        images = self.images[:]
        labels = self.labels[:]
        self.images = []
        self.labels = []

        # create list of permutated index and shuffle data accoding to list
        idx = np.random.permutation(len(labels))
        for i in idx:
            self.images.append(images[i])
            self.labels.append(labels[i])

    def reset_pointer(self):
        """
        reset pointer to begin of the list
        """
        self.pointer = 0
        print("pointer rested")
        if self.shuffle:
            self.shuffle_data()

    def read_one_img(self, path):
        img = cv2.imread(path)
        # flip image at random if flag is selected
        if self.horizontal_flip and np.random.random() < 0.5:
            img = cv2.flip(img, 1)
            # rescale image
        # img = cv2.resize(img, (self.scale_size[0], self.scale_size[0]))
        img = img.astype(np.float32)

        # subtract mean
        img -= self.mean
        return img

    def next_batch(self, batch_size):
        """
        This function gets the next n ( = batch_size) images from the path list
        and labels and loads the images into them into memory 
        """
        # Get next batch of image (path) and labels
        paths = self.images[self.pointer:self.pointer + batch_size]
        labels = self.labels[self.pointer:self.pointer + batch_size]

        # update pointer
        self.pointer += batch_size

        # Read images
        images = np.ndarray([batch_size, self.scale_size[0], self.scale_size[1], 3])
        for i in range(len(paths)):
            img = self.read_one_img(paths[i])

            images[i] = img

        # return array of images and labels
        return images, labels

    @staticmethod
    def get_mos_from_path(f_name):
        f_name = os.path.basename(f_name)
        mos = float(f_name.split('_')[1])
        return mos

    def next_batch_with_filename(self, batch_size):
        """
        This function gets the next n ( = batch_size) images from the path list
        and labels and loads the images into them into memory 
        """
        # Get next batch of image (path) and labels
        paths = self.images[self.pointer:self.pointer + batch_size]
        labels = self.labels[self.pointer:self.pointer + batch_size]

        # update pointer
        self.pointer += batch_size

        # Read images
        images = np.ndarray([batch_size, self.scale_size[0], self.scale_size[1], 3])
        for i in range(len(paths)):
            img = self.read_one_img(paths[i])
            images[i] = img

        # return array of images and labels
        return images, [ImageDataGenerator.get_mos_from_path(f) for f in paths], paths