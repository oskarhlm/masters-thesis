import os
import uuid
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from datetime import datetime

MEMORY_KEY = 'chat_memory'


def get_session(session_id: str = None):
    if not session_id:
        current_date = datetime.now().strftime("%Y%m%d")  # Format: YYYYMMDD
        session_id = f'session-{uuid.uuid4()}-{current_date}'

    message_history = []

    if os.getenv('IS_DOCKER_CONTAINER'):
        if not os.getenv('REDIS_URL'):
            raise KeyError('No REDIS_URL set in Docker environment')
        message_history = RedisChatMessageHistory(
            url=os.getenv('REDIS_URL'), session_id=session_id)

    memory = ConversationBufferWindowMemory(
        k=6, memory_key=MEMORY_KEY, chat_memory=message_history, return_messages=True, input_key='input', output_key='output')

    if not memory:
        raise NameError('No memory')

    return session_id, memory
