import functools
import os

from langchain_openai import ChatOpenAI

from ...tools.map_interaction.get_map_state import GetMapStateTool
from ...tools.map_interaction.publish_geojson import PublishGeoJSONTool
from .common import agent_node, create_agent


def create_map_controller_node():
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'), streaming=True)

    map_controller_agent = create_agent(
        llm=llm,
        tools=[GetMapStateTool(), PublishGeoJSONTool()],
        system_prompt=(
            "You are a map controller."
            " Client-side, the user has access to a MapBox/MapLibre map,"
            " and you are equipped with tools to interact with the visual aspects of this map.\n\n"
            "{current_files}"
        ),
        query_from_supervisor=True
    )

    map_controller_agent_node = functools.partial(
        agent_node, agent=map_controller_agent)

    return map_controller_agent_node
