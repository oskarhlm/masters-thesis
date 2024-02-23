from langgraph.graph import StateGraph, END

from .supervisor_agent import create_agent_supervisor_node
from .common import Worker, AgentState
from .analysis_agent import create_analysis_node
from .map_controller_agent import create_map_controller_node

from ..sessions import get_session


def create_multi_agent_runnable(session_id: str = None):
    supervisor_chain = create_agent_supervisor_node([e for e in Worker])

    analysis_node = create_analysis_node()
    map_controller_node = create_map_controller_node()

    SUPERVISOR = 'supervisor'

    workflow = StateGraph(AgentState)
    workflow.add_node(Worker.ANALYSIS.value, analysis_node)
    workflow.add_node(Worker.MAP.value, map_controller_node)
    workflow.add_node(SUPERVISOR, supervisor_chain)

    for worker in Worker:
        workflow.add_edge(worker.value, SUPERVISOR)

    conditional_map = {k.value: k.value for k in Worker}
    conditional_map["FINISH"] = END
    workflow.add_conditional_edges(
        SUPERVISOR, lambda x: x["next"], conditional_map)

    workflow.set_entry_point(SUPERVISOR)

    session_id, _ = get_session(session_id)

    return session_id, workflow.compile()
