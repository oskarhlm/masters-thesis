from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools.shell import ShellTool
from langchain_openai import ChatOpenAI
from ..tools.utils import get_custom_tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain.agents import create_openai_tools_agent, AgentExecutor
from tempfile import TemporaryDirectory

from langchain_community.agent_toolkits import FileManagementToolkit

from .sessions import MEMORY_KEY, get_session


def get_file_management_tools():
    working_directory = TemporaryDirectory()
    toolkit = FileManagementToolkit(
        root_dir=str(working_directory.name),
        selected_tools=["read_file", "write_file", "list_directory"],

    )
    return toolkit.get_tools()


def create_tool_agent(session_id: str = None):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=(
                'You are a helpful GIS agent/consultant.\n'
            )),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            HumanMessagePromptTemplate.from_template('{input}'),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
    )
    tools = [PythonREPLTool(), ShellTool()] + [tool()
                                               for tool in get_custom_tools()]

    session_id, memory = get_session(session_id)
    # llm = ChatOpenAI(model="gpt-4-1106-preview", temperature=0,
    #                  streaming=True)
    llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0,
                     streaming=True)
    agent = create_openai_tools_agent(
        llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True, memory=memory
    )

    return session_id, agent_executor
