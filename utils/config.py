import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    _instance = None
    load_dotenv('.app.env')
    version = os.getenv('VERSION', '')
    # General
    log_level: str = int(os.getenv('LOG_LEVEL', '10'))
    processors_limit: int = int(os.getenv('NUMBER_OF_PROCESSES', '1'))
    log_format: str = os.getenv('LOG_FORMAT', '%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s')
    output_dir: str = os.path.abspath(os.getenv("OUTPUT_DIR", "./output"))
    temp_dir: str = os.path.abspath(os.getenv("TEMP_DIR", "/tmp"))
    image_width: int = int(os.getenv('IMAGE_WIDTH', '1024'))
    image_height: int = int(os.getenv('IMAGE_HEIGHT', '1024'))

    # LP
    solver_engine: str = os.getenv('SOLVER_ENGINE')
    solve_integrally: bool = True if os.getenv('SOLVE_INTEGRALLY') == 'True' else False
    alpha: int = int(os.getenv('ALPHA', '2'))
    beta: int = int(os.getenv('BETA', '3'))
    gamma: int = int(os.getenv('GAMMA', '9'))

    # MNIST to Skeleton
    up_scale_factor: int = int(os.getenv('UP_SCALE_FACTOR', '37'))
    skeletonization_algorithm: str = os.getenv('SKELETONIZATION_ALGORITHM', 'lee')
    mnist_image_threshold: int = int(os.getenv('MNIST_IMAGE_THRESHOLD', '100'))
    mnist_skeletons_dir: str = os.path.abspath(os.getenv("MNIST_SKELETONS_DIR", "./output/mnist_skeletons"))

    # Skeleton to Reduced Scaled Graph
    graphs_dir: str = os.path.abspath(os.getenv("GRAPHS_DIR", "./output/graphs"))
    reducer_lower_bound_node_size: int = int(os.getenv('REDUCER_LOWER_BOUND_NODE_SIZE', '30'))
    reducer_upper_bound_node_size: int = int(os.getenv('REDUCER_UPPER_BOUND_NODE_SIZE', '80'))
    small_edge_merger_threshold: int = int(os.getenv('SMALL_EDGE_MERGER_THRESHOLD', '80'))
    intermediary_node_remover_threshold: int = int(os.getenv('INTERMEDIARY_NODE_REMOVER_THRESHOLD', '5'))
    small_edge_remover_threshold_1: int = int(os.getenv('SMALL_EDGE_REMOVER_THRESHOLD_1', '30'))
    small_edge_remover_threshold_2: int = int(os.getenv('SMALL_EDGE_REMOVER_THRESHOLD_2', '90'))

    # Random samples to cluster representatives
    number_of_clusters: int = int(os.getenv('NUM_OF_CLUSTERS', '10'))
    top_n_clusters: int = int(os.getenv('TOP_N_CLUSTERS', '2'))
    number_of_samples: int = int(os.getenv('NUM_OF_SAMPLES', '5'))

    # Comparison
    number_of_subjects: float = float(os.getenv('NUM_OF_SUBJECTS', '1000'))

    # One to One
    g_graph_path: str = os.path.abspath(os.getenv("G_GRAPH", "./"))
    h_graph_path: str = os.path.join(os.getenv("H_GRAPH", "./"))

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(mnist_skeletons_dir, exist_ok=True)
    os.makedirs(graphs_dir, exist_ok=True)

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return f''' Config(
        log_level: {self.log_level},
        processor_limit: {self.processors_limit},
        log_format: {self.log_format},
        output_dir: {self.output_dir},
        temp_dir: {self.temp_dir},
        image_width: {self.image_width},
        image_height: {self.image_height},
        solver_engine: {self.solver_engine},
        solve_integrally: {self.solve_integrally},
        alpha: {self.alpha},
        beta: {self.beta},
        gamma: {self.gamma},
        up_scale_factor: {self.up_scale_factor},
        skeletonization_algorithm: {self.skeletonization_algorithm},
        mnist_image_threshold: {self.mnist_image_threshold},
        mnist_skeletons_dir: {self.mnist_skeletons_dir},
        graphs_dir: {self.graphs_dir},
        reducer_lower_bound_node_size: {self.reducer_lower_bound_node_size},
        reducer_upper_bound_node_size: {self.reducer_upper_bound_node_size},
        small_edge_merger_threshold: {self.small_edge_merger_threshold},
        intermediary_node_remover_threshold: {self.intermediary_node_remover_threshold},
        small_edge_remover_threshold_1: {self.small_edge_remover_threshold_1},
        small_edge_remover_threshold_2: {self.small_edge_remover_threshold_2},
        number_of_clusters: {self.number_of_clusters},
        top_clusters: {self.top_n_clusters},
        number_of_samples: {self.number_of_samples},
        number_of_subjects: {self.number_of_subjects},
        g_graph_path: {self.g_graph_path},
        h_graph_path: {self.h_graph_path}
        )'''
