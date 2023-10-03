import skimage.transform

import logging
import os
from multiprocessing.pool import ThreadPool as Pool

import skimage.transform
import numpy as np
from skimage import morphology
import cv2

from utils.config import Config

config = Config()
logger = logging.getLogger(__name__)


def worker(args):
    image, idx, path, threshold, upscale, algorithm = args
    expanded_image = skimage.transform.pyramid_expand(image, upscale)
    binary_image = (expanded_image > threshold).astype(np.uint8)
    binary_image = np.ascontiguousarray(binary_image)

    # Skeletonize the image
    skeleton = morphology.skeletonize(binary_image, method=algorithm)
    cv2.imwrite(path, (skeleton * 255).astype(np.uint8))


def skeletonize_mnist_dataset(images, labels):
    logger.info(f"Skeletonizing...")

    processing_queue = []
    for idx, image in enumerate(images):
        label = str(labels[idx])
        skeleton_path = os.path.join(config.mnist_skeletons_dir, f'{label}_{idx}.png')
        if os.path.exists(skeleton_path):
            continue
        image = images[idx].reshape(28, 28)
        processing_queue.append((image, idx, skeleton_path, config.mnist_image_threshold, config.up_scale_factor,
                                 config.skeletonization_algorithm))

    with Pool(processes=config.processors_limit) as pool:
        pool.map(worker, processing_queue)
