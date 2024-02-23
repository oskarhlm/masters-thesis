import pickle
from typing import Optional

from redis.asyncio import Redis
from langchain_core.pydantic_v1 import Field
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.utils import ConfigurableFieldSpec

from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint


class RedisSaver(BaseCheckpointSaver):
    client: Redis  # Use redis.asyncio.Redis for asynchronous operations

    is_setup: bool = Field(False, init=False, repr=False)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_conn_string(cls, conn_string: str) -> "RedisSaver":
        client = Redis.from_url(conn_string)
        return cls(client=client)

    @property
    def config_specs(self) -> list[ConfigurableFieldSpec]:
        return [
            ConfigurableFieldSpec(
                id="thread_id",
                annotation=str,
                name="Thread ID",
                description=None,
                default="",
                is_shared=True,
            ),
        ]

    def get(self, config: RunnableConfig) -> Checkpoint | None:
        return NotImplementedError

    def put(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        return NotImplementedError

    async def aget(self, config: RunnableConfig) -> Optional[Checkpoint]:
        print(config["configurable"]["thread_id"])
        value = await self.client.get(config["configurable"]["thread_id"])
        return pickle.loads(value) if value else None

    async def aput(self, config: RunnableConfig, checkpoint: Checkpoint) -> None:
        await self.client.set(
            config["configurable"]["thread_id"],
            pickle.dumps(checkpoint)
        )
