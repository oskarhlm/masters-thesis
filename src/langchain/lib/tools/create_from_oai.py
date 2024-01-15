from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
import unittest

tool_template = """
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

class <PydanticModel>(BaseModel):
    <docstring> (Optional)

    arg_1: float = Field(..., description="description for argument of type float")
    arg_2: str = Field(..., description="description for argument of type string")


class YourCustomTool(BaseTool):
    name = <name>
    description = <detailed-description>
    args_schema = <PydanticModel>

    def _run(self, arg_1, arg_2):  # Any number of arguments is accepted
        # Functionality of the tool
        pass

    def _arun(self, query):
        # Async implementation of the tool (Optional)
        raise NotImplementedError
"""

unit_test_tempalte = """
import unittest
from your_custom_tool import YourCustomTool, MyPydanticModel

class TestYourCustomTool(unittest.TestCase):
    
    def setUp(self):
        # Setup before each test case, if necessary
        pass

    def test_functionality_1(self):
        # Test for functionality 1
        tool = YourCustomTool()
        input_args = <PydanticModel>(arg_1=1.0, arg_2='example')
        expected_output = # Define the expected output
        self.assertEqual(tool._run(input_args.arg_1, input_args.arg_2), expected_output)

    # Add more test cases as necessary
    # ...
"""


class CreateNewToolInput(BaseModel):
    """Input for GeopyDistanceTool."""

    code: str = Field(..., description="The complete contents of the file that defines the LangChain tool")
    tool_path: str = Field(
        ..., description="Path to the folder that will contain the tool code and unit tests")


# class CreateNewToolTool(BaseTool):
#     name = 'create_new_tool'
#     description = (
#         'Use this to create a new LangChain tool that can be used in the future.\n\n'
#         f'The tool should follow the format below:\n{tool_template}'
#     )
#     args_schema: Type[BaseModel] = CreateNewToolInput

#     def _run(self, tool_code: str, test_code: str, tool_folder: str, tool_name):
#         with open(f'{tool_folder}/{tool_name}.py', 'w') as file:
#             file.write(tool_code)

#         with open(f'{tool_folder}/{tool_name}_tests.py', 'w') as file:
#             file.write(tool_code)

#         # suite = unittest.TestSuite()

#         # new_tool: type[unittest.TestCase] = pass
#         # suite.addTest(unittest.makeSuite(CreateNewToolTool))

#         # # Run the tests and collect results
#         # runner = unittest.TextTestRunner()
#         # result = runner.run(suite)

#         # # Now 'result' is an object containing the test results
#         # print("Errors: ", len(result.errors))
#         # print("Failures: ", len(result.failures))
#         # print("Tests Run: ", result.testsRun)
#         # print("Was Successful: ", result.wasSuccessful())

#     def _arun(self, query):
#         # Async implementation of the tool (Optional)
#         raise NotImplementedError
