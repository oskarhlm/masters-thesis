# from pydantic import BaseModel
# from typing import Type

# from langchain.tools import BaseTool
# from langchain.pydantic_v1 import BaseModel, Field


# class SetMapLayerPaintInput(BaseModel):
#     pass


# class SetMapLayerPaintTool(BaseTool):
#     name = "set_map_layer_paint"
#     description = "Useful for when you need change the paint property of a MapBox layer."
#     args_schema: Type[BaseModel] = SetMapLayerPaintInput

#     def _run(self) -> str:
#         return '_run'

#     async def _arun(self) -> str:
#         llm = ChatOpenAI()
#         prompt = ChatPromptTemplate.from_messages(
#             [
#                 (
#                     'system',
#                     (
#                         'Based on a list of messages between a human user and an AI agent, '
#                         'you will help decide a strategy for the AI agent by selecting its next "thought".\n'
#                         'You will select between different strategies that are provided to you.\n\n'
#                         'Here is the system message for the AI agent:\n\n"""{system_message}"""\n\n'
#                         'Here is the conversation up to this point:\n\n{chat_history}\n\n'
#                         'Here here are the suggested ai_suffixes for you to choose from:\n\n{available_ai_suffixes}\n\n'
#                         'Prefer the database query suffix in most cases, unless it makes no sense at all.\n'
#                         'If none of the suggested suffix seem fit, you may make one up yourself. Put emphasis on the last message.'
#                     )
#                 )
#             ]
#         )

#         chain = create_structured_output_chain(AISuffix, llm, prompt)
#         result = chain.invoke({
#             'system_message': system_message,
#             'chat_history': agent_executor.memory.chat_memory.messages + [user_query],
#             'available_ai_suffixes': suggested_ai_suffixes
#         })

#         return result['function'].ai_suffix
#         return {'ws': {'paint': '{...}'}}
