from typing import Callable, Dict

from .sql_worker import create_sql_node
from .map_controller_worker import create_map_controller_node
from .python_analysis_worker import create_python_analysis_node


class Worker:
    def __init__(self, name: str, description: str, node_creator: Callable):
        self.name = name
        self.description = description
        self.node_creator = node_creator

    def create_node(self):
        return self.node_creator()


python_analysis_worker = Worker(
    name="python_analysis_worker",
    description=(
        "A worker/agent that can generate and execute Python code."
        " Suitable for doing spatial analysis on files that are stored on the server,"
        " or uploaded to the server from the client."
    ),
    node_creator=create_python_analysis_node
)


map_worker = Worker(
    name="map_worker",
    description=(
        "A worker/agent that controls a client-side map that is visible to the user/human."
        " Has tools for adding GeoJSON to the map, changing layer color, etc."
    ),
    node_creator=create_map_controller_node
)

sql_worker = Worker(
    name="sql_worker",
    description=(
        "A worker/agent that has access to, and can query, a geospatial PostGIS database."
        " Suitable for doing spatial analysis on the tables found in the database."
        " The analysis results can be added to the map by map_worker."
    ),
    node_creator=create_sql_node
)

workers: Dict[str, Worker] = {
    worker.name: worker
    for worker in [
        python_analysis_worker,
        map_worker,
        sql_worker
    ]
}
