import os
import logging
from functools import wraps

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
formatter = logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s : %(message)s]")
consoleHandler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)


class CheckCluster:

    def __init__(self, filename):
        self.cluster_conf_filename = filename

    def __call__(self, wrap_function):
        @wraps(wrap_function)
        def wrapped(obj, cluster_name, obie_config):

            clusters_path = obie_config.obie_clusters_dir
            cluster_config_path = os.path.join(clusters_path, cluster_name, self.cluster_conf_filename)

            if not os.path.isfile(cluster_config_path):
                raise FileNotFoundError(cluster_config_path)

            wrap_function(obj, cluster_name, obie_config)

        return wrapped


class DependenciesGraph:

    def __init__(self):
        self.sorted_nodes = []
        self.graph = {}
        self.visited_nodes = {}

    def add_node(self, node):
        self.graph[node] = []

    def add_dependency(self, d_from, d_to):
        if self.graph.get(d_to) is not None:
            self.graph.get(d_to).append(d_from)
        else:
            self.graph[d_to] = [d_from]

    def _initialize(self):
        self.visited_nodes = {}
        self.sorted_nodes = []
        for node, neighbours in self.graph.items():
            self.visited_nodes[node] = 'w'
            for next_node in neighbours:
                self.visited_nodes[next_node] = 'w'

    def _dfs(self, node):
        self.visited_nodes[node] = 'g'

        for next_node in self.graph.get(node, []):
            if self.visited_nodes[next_node] == 'w':
                self._dfs(next_node)
            if self.visited_nodes[next_node] == 'g':
                logger.error('There are circular dependencies')
                return

        self.visited_nodes[node] = 'b'
        self.sorted_nodes.insert(0, node)

    def topological_sort(self):

        self._initialize()

        for node, _ in self.graph.items():
            if self.visited_nodes[node] == 'w':
                self._dfs(node)


def log_process_output(pipe):
    for line in iter(pipe.readline, b''):
        logger.info('%s', line.rstrip().decode())
