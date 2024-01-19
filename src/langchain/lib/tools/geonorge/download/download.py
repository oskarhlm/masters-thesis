from .download_helper import DownloadHelperTool
from ..formats_and_projections import AvailableFormatsAndProjectionsTool

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import format_tool_to_openai_function
import json
import requests
from typing import List, Dict, Any, Type, Optional
import httpx


class DownloadGeonorgeDatasetInput(BaseModel):
    uuid: str = Field(description='The UUID of the dataset to be downloaded')
    areas: List[str] = Field(
        description='The areas of the dataset to be downloaded')
    data_format: Optional[str] = Field(
        description='Preferable forat of the dataset to be downloaded.')


class DownloadGeonorgeDatasetTool(BaseTool):
    name = "download_geonorge_dataset"
    description = (
        "Useful when you need to download a dataset from Geonorge.\n"
        "Stores the dataset in the current working directory."
    )
    args_schema: Type[BaseModel] = DownloadGeonorgeDatasetInput

    def _run(self, uuid: str, areas: List[str], data_format: Optional[str] = 'GML') -> str:
        """Use the tool."""
        url = 'https://nedlasting.geonorge.no/api/codelists/area/'
        res = requests.get(f'{url}{uuid}')
        area_names = extract_names_from_area_response(res.json())

        geonorge_download_chain = (
            formats_and_projection_prompt
            | formats_and_projections_model
            | {
                'result': RunnableLambda(lambda msg: call_formats_and_projections_tool(msg)),
                'uuid': RunnableLambda(lambda _: uuid),
                'data_format': RunnableLambda(lambda _: data_format)
            }
            | downloading_prompt
            | downloading_model
            | RunnableLambda(lambda msg: call_download_tool(msg))
        )

        return geonorge_download_chain.invoke({'uuid': uuid, 'available_areas': area_names,
                                               'requested_areas': areas})

    async def _arun(self, uuid: str, areas: List[str], data_format: Optional[str] = 'GML') -> str:
        """Use the tool asynchronously."""
        url = 'https://nedlasting.geonorge.no/api/codelists/area/'

        async with httpx.AsyncClient() as client:
            res = await client.get(f'{url}{uuid}')
            area_names = extract_names_from_area_response(res.json())

        geonorge_download_chain = (
            formats_and_projection_prompt
            | formats_and_projections_model
            | {
                'result': RunnableLambda(lambda msg: call_formats_and_projections_tool(msg)),
                'uuid': RunnableLambda(lambda _: uuid),
                'data_format': RunnableLambda(lambda _: data_format)
            }
            | downloading_prompt
            | downloading_model
            | RunnableLambda(lambda msg: call_download_tool(msg))
        )

        return geonorge_download_chain.invoke({'uuid': uuid, 'available_areas': area_names,
                                               'requested_areas': areas})


def extract_names_from_area_response(results: List[Dict[str, Any]]) -> List[str]:
    names = list(map(lambda res: res['name'], results))
    return names


#
# Model and prompt for getting the available formats and projections for a given dataset and area(s)
#
formats_and_projections_model = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
    streaming=True,
    model_kwargs={
        'tools': [{'type': 'function', 'function': format_tool_to_openai_function(
            AvailableFormatsAndProjectionsTool())}],
        'tool_choice': AvailableFormatsAndProjectionsTool.name
    }
)

formats_and_projection_prompt = ChatPromptTemplate.from_template("""Dataset UUID: {uuid}
                                           
These are the available areas to choose from: 
                                           
{available_areas}
                                           
Here is the area(s) requested by the user: 
                                           
{requested_areas}
                                           
Select corresponding area(s) from the available ones. 
""")


def call_formats_and_projections_tool(message):
    kwargs = message.additional_kwargs['tool_calls'][0]['function']['arguments']
    return AvailableFormatsAndProjectionsTool()._run(**json.loads(kwargs))


#
# Model and prompt for downloading the correct dataset(s)
#
downloading_model = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
    streaming=True,
    model_kwargs={
        'tools': [{'type': 'function', 'function': format_tool_to_openai_function(
            DownloadHelperTool())}],
        'tool_choice': DownloadHelperTool.name
    }
)

downloading_prompt = ChatPromptTemplate.from_template("""Here are available formats and projections that can be used for download: 
                                           
{result}
                                           
You are only allowed to use ONE format; it can be picked at random. {data_format} format is most preferable. 
                                           
The UUID for the dataset is: {uuid}
""")


def call_download_tool(message):
    kwargs = message.additional_kwargs['tool_calls'][0]['function']['arguments']
    return DownloadHelperTool()._run(json.loads(kwargs))
