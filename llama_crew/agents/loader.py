from llama_index.core.tools import FunctionTool
from .agent import SimpleAgentWorker
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner


def load_agents(llm, agents_config, all_tools):
    agents = {}
    for agent_config in agents_config["agents"]:
        initial_tools = [ FunctionTool.from_defaults(fn=fn.instance) for fn in all_tools if fn.name in agent_config.get("tools",[])]
        if len(initial_tools) == 0:
            agent_worker = SimpleAgentWorker(llm=llm, role_prompt=agent_config["prompt"], can_delegate=agent_config.get("can_delegate",False), verbose=True)
        else:
            agent_worker = FunctionCallingAgentWorker.from_tools(
                initial_tools, 
                llm=llm, 
                verbose=True
            )
        agent = AgentRunner(agent_worker)
        agents[agent_config["name"]] = agent
    return agents