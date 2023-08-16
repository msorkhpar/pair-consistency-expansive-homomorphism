import logging
import os
import random
import shutil
from datetime import datetime
import concurrent.futures

from sklearn.datasets import fetch_openml

from recognition.base_graphs import get_nominates
from recognition.digit_detector import calculate_cost_concurrently
from recognition.input_graph import InputGraph
from reduction.graph_simplifier import reduce_graphs_edges
from skeletonization.mnist_skeleton import skeletonize_mnist_dataset
from utils.config import Config
from utils.result_drawer import GraphDrawer

config = Config()
version = datetime.now().strftime('%y-%m-%d %H:%M')
os.makedirs(os.path.join(config.output_dir, version))
logging.basicConfig(format=config.log_format,
                    filename=os.path.join(config.output_dir, version, "app.log"),
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

    with concurrent.futures.ProcessPoolExecutor() as executor:
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
    for key in digit_samples:
        random.shuffle(digit_samples[key])
    return digit_samples


def get_base_graphs(digit_samples, version):
    logger.info(f"Creating base graphs...")
    base_graphs_path = os.path.join(config.output_dir, version, "base_graphs")
    os.makedirs(base_graphs_path)
    base_graphs = get_nominates(digit_samples)

    for base_graph in base_graphs:
        shutil.copy(
            base_graph.adjacency_list_path,
            os.path.join(base_graphs_path, f"{base_graph.name}.adjlist")
        )
        GraphDrawer(
            base_graph.undirected_graph,
            os.path.join(base_graphs_path, f"{base_graph.name}.png")
        ).convert_graph_to_cv2_image(color=(0, 0, 255))

    return base_graphs


def main():
    try:
        logger.info(f"Loading MNIST dataset...")
        mnist = fetch_openml('mnist_784', data_home=config.temp_dir)
        images = mnist.data.to_numpy()
        labels = mnist.target.astype('int64')

        if config.build_skeletons:
            skeletonize_mnist_dataset(images, labels)

        if config.build_graphs:
            reduce_graphs_edges(labels)

        digit_samples = get_digit_samples(labels)

        base_graphs = get_base_graphs(digit_samples, version)
        logger.info(f"Base graphs are created and saved to {os.path.join(config.output_dir, version, 'base_graphs')}")
        csv_path = os.path.join(config.output_dir, version, f"result.csv")
        with open(csv_path, "w") as f:
            f.write(f"G Name, H Name, G->H Cost, H->G Cost, Detected, Total Cost\n")
        logger.info("Calculating recognition on the rest of the dataset...")
        with open(csv_path, "a") as f:
            for i in range(10):
                for counter, idx in enumerate(digit_samples[i][config.number_of_samples:], 1):
                    if counter > config.number_of_subjects:
                        break
                    subject_graph = InputGraph(
                        os.path.join(config.graphs_dir, str(idx // 1000), f'{i}_{idx}.adjlist'), True,
                        name=f"{i}_{idx}", digit=i
                    )
                    best_cost = find_best_cost(subject_graph, base_graphs)
                    f.write(f"{subject_graph.name},{','.join(map(str, best_cost))}\n")
                    if counter % 10 == 0:
                        f.flush()
                    if counter % 500 == 0:
                        logger.info(f"Digit [{i}], {counter}/{len(digit_samples[i])} is done!")

                f.flush()
        logger.info(f"Results saved to {csv_path}!")
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
