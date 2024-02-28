import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .supervisor import create_agent_supervisor_node
from .common import Worker, AgentState, prelude
from .analysis_worker import create_analysis_node
from .map_controller_worker import create_map_controller_node
from .sql_worker import create_sql_node
from ..sessions import generate_session_id
from ..redis_checkpointer import RedisSaver


def create_multi_agent_runnable(session_id: str = None):
    # analysis_node = create_analysis_node()
    map_controller_node = create_map_controller_node()
    sql_node = create_sql_node()

    SUPERVISOR = 'supervisor'

    workflow = StateGraph(AgentState)
    # workflow.add_node(Worker.ANALYSIS.value, analysis_node)
    workflow.add_node(Worker.MAP.value, map_controller_node)
    workflow.add_node(Worker.SQL.value, sql_node)

    # workers = list(filter(lambda n: n != SUPERVISOR, workflow.nodes))
    workers = list(
        filter(lambda w: w.value in workflow.nodes and w.value != SUPERVISOR, Worker))
    print(workers)

    supervisor_chain = create_agent_supervisor_node([e for e in workers])
    workflow.add_node(SUPERVISOR, supervisor_chain)

    for worker in workers:
        workflow.add_edge(worker.value, SUPERVISOR)

    conditional_map = {k.value: k.value for k in workers}
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
