import requests
from pydantic import BaseModel, UUID4
from typing import List, Type, Optional
import os

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool


class Area(BaseModel):
    code: str
    name: str
    type: str


class Format(BaseModel):
    name: str


class Projection(BaseModel):
    code: str


class OrderLine(BaseModel):
    metadataUuid: UUID4
    areas: List[Area]
    formats: List[Format]
    projections: List[Projection]


class DownloadHelperInput(BaseModel):
    orderLines: List[OrderLine] = Field(
        description="Information necessary for download.")


class DownloadHelperTool(BaseTool):
    name = "download_geonorge_dataset"
    description = "Useful when you need to download a dataset from Geonorge."
    args_schema: Type[BaseModel] = DownloadHelperInput

    should_use = False

    def _run(self, orderLines: List[OrderLine]) -> str:
        """Use the tool."""
        res = requests.post(
            f'https://nedlasting.geonorge.no/api/order', json=orderLines)
        if res.status_code != 200:
            return "Failed to place order for datasets."

        data = res.json()
        if len(data['files']) == 0:
            return 'No files were found that matched the request.'

        download_results = []
        for file in data['files']:
            url = file['downloadUrl']
            filename = file['name']
            download_status = download_file(url, filename)
            download_results.append(f"{filename}: {download_status}")

        return "\n".join(download_results)

    async def _arun(self, orderLines: List[OrderLine]) -> str:
        """Use the tool asynchronously."""
        return NotImplementedError


def download_file(url, filename, save_dir: Optional[str] = None):
    print('Downloading...')
    if save_dir:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        full_path = os.path.join(save_dir, filename)
    else:
        full_path = filename

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(full_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=128):
                file.write(chunk)
        return f"Downloaded file: {full_path}"
    else:
        return f"Failed to download file: status code {response.status_code}"


async def download_file_async(session, url, filename, save_dir: Optional[str] = None):
    return NotImplementedError
