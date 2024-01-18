import json
from langchain.tools import MoveFileTool, format_tool_to_openai_function
from langchain.agents import create_openai_tools_agent, AgentExecutor
import aiohttp
import requests
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import List
from typing import Optional, Type
from operator import itemgetter

from langchain.schema import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from dotenv import load_dotenv
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field


class AvailableFormatsAndProjectsionsInput(BaseModel):
    metadata_uuid: str = Field(
        description='Unique identifier for the item to download')
    area: str = Field(
        description="The 'kommune' or 'fylke' to be queried for available data formats and projections.")


class AvailableFormatsAndProjectionsTool(BaseTool):
    name = "available_formats_and_projections"
    description = "Useful for when you need to find available data formats and projections for a given geographical area."
    args_schema: Type[BaseModel] = AvailableFormatsAndProjectsionsInput

    def _run(self, metadata_uuid: str, area: str) -> str:
        """Use the tool."""
        res = requests.get(
            f'https://nedlasting.geonorge.no/api/codelists/area/{metadata_uuid}')
        data = res.json()

        for item in data:
            if item.get("name") == area:
                return item

        return 'Could not find formats and projections for provided area.'

    async def _arun(self, metadata_uuid: str, area: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("custom_search does not support async")


prompt1 = ChatPromptTemplate.from_template("""Dataset UUID: {uuid}
                                           
These are the available areas to choose from: 
                                           
{available_areas}
                                           
Here is the area(s) requested by the user: 
                                           
{requested_areas}
                                           
Select corresponding area(s) from the available ones. 
""")

prompt2 = ChatPromptTemplate.from_template("""Available formats and projections for {place}: 
                                           
{data}
""")


llm = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
    streaming=True,
    model_kwargs={
        'tools': [{'type': 'function', 'function': format_tool_to_openai_function(
            AvailableFormatsAndProjectionsTool())}],
        'tool_choice': AvailableFormatsAndProjectionsTool.name
    }
)
data = res.json()
names = extract_names(data)


def call_function(message):
    kwargs = message.additional_kwargs['tool_calls'][0]['function']['arguments']
    return AvailableFormatsAndProjectionsTool()._run(**json.loads(kwargs))


chain1 = (
    prompt1
    | llm
    | RunnableLambda(lambda msg: call_function(msg))
)

chain1.invoke({'uuid': uuid, 'available_areas': names,
              'requested_areas': ['ozlo']})


class MetaData(BaseModel):
    Uuid: str = Field(description='Unique identifier for the search result')
    Title: str = Field(description='Title of the search result')
    Abstract: str = Field(description='Abstract describing the result')


class GeonorgeDownloadResponse(BaseModel):
    NumFound: int = Field(
        description='Number of search results for the given query')
    Results: List[MetaData] = Field(
        description='List of metadata for the results')


class GeonorgeDownloadInput(BaseModel):
    """Input for GeonorgeSearchTool."""
    metadata_uuid: str = Field(
        description='Unique identifier for the item to download')
    area: Optional[str] = Field(description='The area')


class GeonorgeDownloadTool(BaseTool):
    """Custom tool to search for geospatial data through the Geonorge API."""

    name: str = "geonorge-search"
    args_schema: Type[BaseModel] = GeonorgeDownloadInput
    description: str = "Use this tool for search for geospatial dataset and APIs through the Geonorge API."

    base_url = "https://kartkatalog.geonorge.no"
    endpoint = "/api/search"

    def _run(self, text: str) -> str:
        params = {
            'text': text,
            'limit': 10
        }

        response = requests.get(
            url=f"{self.base_url}{self.endpoint}", params=params)
        data = response.json()

        return GeonorgeSearchResponse(**data).model_dump_json(indent=4)

    async def _arun(self, text: str):
        params = {'text': text}

        async with aiohttp.ClientSession() as session:
            async with session.get(url=f"{self.base_url}{self.endpoint}", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return GeonorgeSearchResponse(**data).model_dump_json(indent=4)
                else:
                    return f"Error: HTTP {response.status}"
