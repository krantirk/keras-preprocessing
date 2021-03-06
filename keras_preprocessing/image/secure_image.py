import hashlib
import math
import os

import numpy as np

try:
    from PIL import Image
except ImportError:
    Image = None
try:
    from skimage.io import imread
except ImportError:
    imread = None


def transform(src_dir, dest_dir, count, block_size, image_x, image_y):
    """This function checks the directory and encrypts the image and saves
        it in the destination folder.

    # Arguments
        :param src_dir: source directory.
        :param dest_dir: destination directory.
        :param count: keeping count of images processed.
        :param block_size: block size for rotation.
        :param image_x: width of image.
        :param image_y: height of image.

    # Returns
        None.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    for filename in os.listdir(os.path.join(src_dir)):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            for file in os.listdir(os.path.join(src_dir, filename)):
                if file.endswith('.jpg'):
                    full_path = os.path.join(src_dir, filename, file)
                    if not os.path.exists(os.path.join(dest_dir, filename)):
                        os.mkdir(os.path.join(dest_dir, filename))
                    im = Image.open(full_path, "r")
                    im_resized = im.resize((image_x, image_y), Image.ANTIALIAS)
                    arr = im_resized.load()  # pixel data stored in this 2D array
                    transform_img(block_size, arr, image_x, image_y)
            if count % 1000 == 0:
                print("No of images processed " + str(count))
            im_resized.save(os.path.join(dest_dir, filename, file))
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            count += 1
            full_path = os.path.join(src_dir, filename)
            im = Image.open(full_path, "r")
            im_resized = im.resize((image_x, image_y), Image.ANTIALIAS)
            arr = im_resized.load()  # pixel data stored in this 2D array
            transform_img(block_size, arr, image_x, image_y)
            if count % 1000 == 0:
                print("No of images processed " + str(count))
            im_resized.save(os.path.join(dest_dir, filename))
        else:
            print("Unknown file type")


def encrypt_directory(src_dir, dest_dir, image_x, image_y, password):
    """This function encrypts the src_directory into dest_dir using hash
        of password as the block_size.

    # Arguments
        :param src_dir: source directory.
        :param dest_dir: destination directory.
        :param image_x: width of image.
        :param image_y: height of image.
        :param password: password for encryption.

    # Returns
        Success message.
    """
    hash_val = int(hashlib.sha1(password.encode('utf-8')).hexdigest(), 16) % 53
    if hash_val < 10:
        hash_val = hash_val * 2
    block_size = hash_val
    count = 0
    transform(src_dir=src_dir, dest_dir=dest_dir, count=count,
              block_size=block_size, image_x=image_x, image_y=image_y)
    return "Success"


def rot(A, n, x1, y1):
    """This is the function which rotates a given block.

    # Arguments
        :param A: numpy array to be rotated.
        :param n: counter.
        :param x1: helper pixel x1 used in shuffling.
        :param y1: helper pixel y1 used in shuffling.

    # Returns
        Image array.
    """
    temple = []
    for i in range(n):
        temple.append([])
        for j in range(n):
            temple[i].append(A[x1 + i, y1 + j])
    for i in range(n):
        for j in range(n):
            A[x1 + i, y1 + j] = temple[n - 1 - i][n - 1 - j]
    return A


def transform_img(block_size, arr, image_x, image_y):
    """ Shuffling pixels.

    # Arguments
        :param block_size: generated from the password.
        :param arr: image array.
        :param image_x: width of image.
        :param image_y: height of image.

     # Returns
        np array of the image.
    """

    for i in range(2, block_size + 1):
        for j in range(int(math.floor(float(image_x) / float(i)))):
            for k in range(int(math.floor(float(image_y) / float(i)))):
                rot(arr, i, j * i, k * i)
    for i in range(3, block_size + 1):
        for j in range(int(math.floor(float(image_x) /
                                      float(block_size + 2 - i)))):
            for k in range(int(math.floor(float(image_y) /
                                          float(block_size + 2 - i)))):
                rot(arr, block_size + 2 - i, j *
                    (block_size + 2 - i), k * (block_size + 2 - i))
    return np.array(arr, dtype=np.float32)


def decrypt_img(path_to_img, password, image_x, image_y):
    """This function decrypts the image using the same logic.

    # Arguments
        :param path_to_img: the path to image.
        :param password: password same as encryption.
        :param image_x: width of image.
        :param image_y: height of image.

    # Returns
        np array which could be yielded to a fit_generator function.
    """
    hash_val = int(hashlib.sha1(password.encode('utf-8')).hexdigest(), 16) % 53
    if hash_val < 10:
        hash_val = hash_val * 2
    block_size = hash_val
    arr = imread(path_to_img)
    return transform_img(block_size=block_size, arr=arr,
                         image_x=image_x, image_y=image_y)
