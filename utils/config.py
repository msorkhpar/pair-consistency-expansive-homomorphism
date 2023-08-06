import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    _instance = None
    load_dotenv('.env')

    log_level: str = int(os.getenv('LOG_LEVEL', '10'))
    log_format: str = os.getenv('LOG_FORMAT', '%(asctime)s %(levelname)s:%(name)s:%(funcName)s:%(message)s')
    h_graph_path: str = os.getenv('H_GRAPH_PATH')
    g_graph_path: str = os.getenv('G_GRAPH_PATH')
    computerized_graphs_dir: str = os.getenv('COMPUTERIZED_GRAPHS_DIR')
    solver_engine: str = os.getenv('SOLVER_ENGINE')
    solve_integrally: bool = True if os.getenv('INTEGRAL') == 'True' else False
    generate_mapping_diagrams: bool = True if os.getenv('GENERATE_MAPPING_DIAGRAMS') == 'True' else False
    input_width: int = int(os.getenv('INPUT_WIDTH', '1024'))
    input_height: int = int(os.getenv('INPUT_HEIGHT', '1024'))

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return f''' Config(
        log_level: {self.log_level},
        log_format: {self.log_format},
        H_path:{self.h_graph_path},
        G_path: {self.g_graph_path},
        computerized_graphs_dir: {self.computerized_graphs_dir},
        solver_engine: {self.solver_engine},
        solve_integrally = {self.solve_integrally},
        generate_mapping_diagrams = {self.generate_mapping_diagrams},
        input_width: {self.input_width},
        input_height: {self.input_height},
        )'''
