import logging
import os
import random
import shutil
import traceback
from datetime import datetime
import concurrent.futures

import numpy as np
from sklearn.datasets import fetch_openml

from recognition.base_graphs import get_nominates
from recognition.digit_detector import calculate_cost_concurrently
from recognition.input_graph import InputGraph
from reduction.graph_simplifier import reduce_graphs_edges
from skeletonization.mnist_skeleton import skeletonize_mnist_dataset
from utils.config import Config
from utils.confusion_matrix_builder import build_confusion_matrix
from utils.result_drawer import GraphDrawer

config = Config()
os.makedirs(os.path.join(config.output_dir), exist_ok=True)
logging.basicConfig(format=config.log_format,
                    filename=os.path.join(config.output_dir, "app.log"),
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=config.log_level)
logger = logging.getLogger(__name__)
logger.info(f"Loaded configurations:{config}")


def find_best_cost(subject_graph, base_graphs):
    best_score = float("inf")
    best_result = {
        "base_graph_name": "N/A",
        "g_to_h_cost": float("inf"),
        "h_to_g_cost": float("inf"),
        "detected": False,
        "cost": float("inf")
    }

    with concurrent.futures.ProcessPoolExecutor(max_workers=config.processors_limit) as executor:
        args = [(subject_graph, base_graph) for base_graph in base_graphs]
        for result in executor.map(calculate_cost_concurrently, args):
            if result["cost"] != -1 and result["cost"] < best_score:
                best_score = result["cost"]
                best_result = result

    return [best_result["base_graph_name"], best_result["g_to_h_cost"], best_result["h_to_g_cost"],
            best_result["detected"], best_result["cost"]]


def get_digit_samples(labels):
    digit_samples = {}
    for idx in range(len(labels)):
        label = labels[idx]
        digit_samples.setdefault(label, []).append(idx)

    return digit_samples


def get_base_graphs(base_labels):
    logger.info(f"Moving base graphs...")
    base_graphs_path = os.path.join(config.output_dir, "base_graphs")
    os.makedirs(base_graphs_path, exist_ok=True)
    base_graphs = []
    for idx, digit in enumerate(base_labels):
        graph = InputGraph(
            os.path.join(config.graphs_dir, f'{digit}_{idx}.adjlist'), True,
            name=f"{digit}_{idx}", digit=digit
        )
        shutil.copy(
            graph.adjacency_list_path,
            os.path.join(base_graphs_path, f"{graph.name}.adjlist")
        )
        base_graphs.append(graph)

    return base_graphs


def main():
    try:
        logger.info(f"Loading dataset...")
        base_images = np.load("./input/base_images.npy")
        base_labels = np.load("./input/base_labels.npy")
        correct_images = np.load("./input/correct_images.npy")
        correct_labels = np.load("./input/correct_labels.npy")
        mistake_images = np.load("./input/mistake_images.npy")
        mistake_labels = np.load("./input/mistake_labels.npy")

        images = np.concatenate((base_images, correct_images, mistake_images))
        labels = np.concatenate((base_labels, correct_labels, mistake_labels))
        skeletonize_mnist_dataset(images, labels)
        reduce_graphs_edges(labels)
        base_graphs = get_base_graphs(base_labels)
        logger.info(f"Base graphs are created and saved to {os.path.join(config.output_dir, 'base_graphs')}")

        digit_samples = get_digit_samples(labels)

        csv_path = os.path.join(config.output_dir, f"result.csv")
        with open(csv_path, "w") as f:
            f.write(f"G Name, H Name, G->H Cost, H->G Cost, Detected, Total Cost\n")
        logger.info("Calculating recognition on the rest of the dataset...")

        shuffled_digit_samples = []
        max_len = max(len(arr) for arr in digit_samples.values())
        for j in range(4, max_len):
            for i in range(10):
                if j < len(digit_samples[i]):
                    shuffled_digit_samples.append((i, digit_samples[i][j]))

        with open(csv_path, "a") as f:
            for counter, (i, idx) in enumerate(shuffled_digit_samples):
                if counter > config.number_of_subjects:
                    break
                try:
                    subject_graph = InputGraph(
                        os.path.join(config.graphs_dir, f'{i}_{idx}.adjlist'), True,
                        name=f"{i}_{idx}", digit=i
                    )
                    best_cost = find_best_cost(subject_graph, base_graphs)
                    f.write(f"{subject_graph.name},{','.join(map(str, best_cost))}\n")
                    if counter % 10 == 0:
                        f.flush()
                    if counter % 100 == 0:
                        logger.info(f"{counter}/{len(shuffled_digit_samples)} is done!")
                except BaseException as e:
                    logging.error(traceback.format_exc())
                    f.write(f"{subject_graph.name},None,-1,-1,False,-1\n")
                    continue
            f.flush()
        logger.info(f"Results saved to {csv_path}!")
        build_confusion_matrix(csv_path, os.path.join(config.output_dir))
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
