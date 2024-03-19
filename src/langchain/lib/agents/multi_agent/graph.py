import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .supervisor import create_agent_supervisor_node
from .common import AgentState
from ..sessions import generate_session_id
from ..redis_checkpointer import RedisSaver
from .worker import workers
from .utils import check_valid_workers


def create_multi_agent_runnable(session_id: str = None):
    SUPERVISOR = 'supervisor'

    workflow = StateGraph(AgentState)

    workers_to_use = ['sql_worker', 'map_worker', 'python_analysis_worker']
    check_valid_workers(workers_to_use)

    worker_objs = [workers[w] for w in workers_to_use]

    for worker in worker_objs:
        workflow.add_node(worker.name, worker.create_node())

    supervisor_chain = create_agent_supervisor_node([e for e in worker_objs])
    workflow.add_node(SUPERVISOR, supervisor_chain)

    for worker in worker_objs:
        workflow.add_edge(worker.name, SUPERVISOR)

    conditional_map = {k.readable_name: k.name for k in worker_objs}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges(
        SUPERVISOR, lambda x: x["next"], conditional_map)

    workflow.set_entry_point(SUPERVISOR)

    session_id = generate_session_id()

    if os.getenv('REDIS_URL'):
        memory = RedisSaver.from_conn_string(os.getenv('REDIS_URL'))
    else:
        memory = SqliteSaver.from_conn_string(':memory:')

    return session_id, workflow.compile(checkpointer=memory)
