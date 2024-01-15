from langchain.schema import SystemMessage, HumanMessage
from langchain_experimental.tools import PythonREPLTool
from langchain_community.tools.shell import ShellTool
from ..tools.utils import get_custom_tools
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content='You are a helpful GIS agent/consultant.'),
            HumanMessage(content='{human_input}'),
            MessagesPlaceholder(variable_name='agent_scratchpad')
        ]
    )

    tools = [PythonREPLTool, ShellTool] + [tool
                                           for tool in get_custom_tools()]
    print(tools)
