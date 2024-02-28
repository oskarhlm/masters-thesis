from typing import Callable, Dict

from .sql_worker import create_sql_node
from .map_controller_worker import create_map_controller_node


class Worker:
    def __init__(self, name: str, description: str, node_creator: Callable):
        self.name = name
        self.description = description
        self.node_creator = node_creator

    def create_node(self):
        return self.node_creator()


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
        " Suitable for doing spatial analysis and generating GeoJSON files that are stored on the server,"
        " and in turn can be added to the map by map_worker."
    ),
    node_creator=create_sql_node
)

workers: Dict[str, Worker] = {
    "map_worker": map_worker,
    "sql_worker": sql_worker,
}
