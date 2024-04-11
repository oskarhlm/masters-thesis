import os

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

from .supervisor import create_agent_supervisor_node
from .common import AgentState
from ..sessions import generate_session_id
from ..redis_checkpointer import RedisSaver
from .worker import workers, map_worker, oaf_worker, python_analysis_worker
from .utils import check_valid_workers


def create_oaf_multi_agent_runnable(session_id: str = None):
    SUPERVISOR = 'supervisor'

    workflow = StateGraph(AgentState)

    workers_to_use = ['oaf_worker', 'map_worker', 'python_analysis_worker']
    check_valid_workers(workers_to_use)
    worker_objs = [workers[w] for w in workers_to_use]
    for worker in worker_objs:
        workflow.add_node(worker.name, worker.create_node())

    supervisor_system_prompt = (
        "You are a supervisor tasked with managing a GIS-related conversation between the"
        " following workers:\n{workers}\n\n"
        " You and your workers live on a server that is responsible of taking a"
        " natural language, GIS-related request from a human user and responding to it by"
        f" fetching appropriate data using `{oaf_worker.readable_name}`"
        f" and performing analysis on said data using `{python_analysis_worker.readable_name}.`"
        " On the web client that the server is taking requests from"
        ", there is a MapBox map that should display the results of the analysis to the human user."
        f" Use `{map_worker.readable_name}` to add data from the server onto this map,"
        " or for interacting with the map in other ways (zooming, deleting layers, etc.)"
        "\n\nGiven the following user request,"
        " respond with the worker to act next. Each worker will perform"
        " actions in the background and return their response to the main conversation.\n"
        f" DO NOT REPEATEDLY CALL THE SAME WORKER if it has already responded.\n"
        f" Remember to add any geospatial data retrieved to the map using `{map_worker.readable_name}`."
        ' When the user\'s question has been answered, or if the analysis was unsuccessful, respond with `FINISH`.'
    )

    supervisor_chain = create_agent_supervisor_node(
        [e for e in worker_objs], system_prompt=supervisor_system_prompt)
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


def create_sql_multi_agent_runnable(session_id: str = None):
    SUPERVISOR = 'supervisor'

    workflow = StateGraph(AgentState)

    workers_to_use = ['sql_worker', 'map_worker']
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
