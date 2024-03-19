from langchain_openai import OpenAIEmbeddings
from xml.dom.minidom import parseString
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredXMLLoader
import os
import fnmatch
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.openai_tools import JsonOutputToolsParser
from langchain_core.runnables import RunnableLambda, RunnableBranch
import xml.etree.ElementTree as ET
from langchain_community.vectorstores import FAISS


def find_files(root_folder, extensions):
    matches = []
    for root, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if any(fnmatch.fnmatch(filename, f'*.{ext}') for ext in extensions):
                matches.append(os.path.join(root, filename))
    return matches


def get_docs_paths():
    root_folder = '/home/dev/master-thesis/data'
    docs_extensions = ['xsd', 'pdf']
    files = find_files(root_folder, docs_extensions)
    formatted_list = "\n".join([f"- {file}" for file in files])
    return formatted_list


@tool('get_full_docs', return_direct=True)
def get_full_docs_tool(path: str):
    """Tool to read the documentation located at the path."""
    try:
        with open(path, 'r') as file:
            return file.read()
    except:
        return f'Failed to read file at {path}'


@tool('get_most_relevant_doc_chunks', return_direct=True)
def get_most_relevant_doc_chunks_tool(path: str, query: str):
    """Tool to get most relevant parts of dataset documentation using similarity search."""
    tree = ET.parse(path)
    root = tree.getroot()
    docs = [Document(page_content=parseString(ET.tostring(child)
                                              ).toprettyxml(newl="")) for child in root]
    faiss_index = FAISS.from_documents(docs, OpenAIEmbeddings())
    for doc in faiss_index.similarity_search(query, k=5):
        print(doc.page_content + f'\n\n{"-" * 100}\n')


async def get_documentation(dataset_name: str, query: str = None, return_chunks=True):
    llm = ChatOpenAI(model=os.getenv('GPT3_MODEL_NAME'))

    prompt = ChatPromptTemplate.from_messages([
        ('system', (
            "The following docs are available:\n"
            f"{get_docs_paths()}"
            "\n\nCall `get_most_relevant_doc_chunks` using the appropriate path"
            " and with a suitable query for similarity search based on this query: `{query}`"
        )),
        ('human', 'Give me the docs for {dataset_name}.')
    ])

    # branch = RunnableBranch(
    #     (lambda _: not return_chunks, llm.bind_tools(
    #         tools=[get_full_docs_tool],
    #         tool_choice={'type': 'function',
    #                      'function': {'name': 'get_full_docs'}})),
    #     (lambda _: return_chunks, )
    # )

    chain = (
        prompt
        # | llm.bind_tools(
        #     tools=[get_full_docs_tool],
        #     tool_choice={'type': 'function',
        #                  'function': {'name': 'get_full_docs'}}
        # )
        | llm.bind_tools(
            tools=[get_most_relevant_doc_chunks_tool],
            tool_choice={'type': 'function',
                         'function': {'name': 'get_most_relevant_doc_chunks'}}
        )
        | JsonOutputToolsParser()
        | RunnableLambda(lambda x: get_most_relevant_doc_chunks_tool(x[0]['args']))
    )

    return await chain.ainvoke({'dataset_name': dataset_name, 'query': query})
