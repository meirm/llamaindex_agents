#!/usr/bin/env python
# coding: utf-8
"""
This is a sample task that demonstrates how to use the Llama Index to build a system that can call multiple agents to answer a question.

agents.yaml:
```yaml
agents:
  - name: mathematician
    role: "Answers mathematics questions"
    prompt: "You are an expert in mathematics, you will answer questions related to maths."
    tools: [add, subtract, multiply, divide]
    verbose: true
  - name: online_research
    role: "Expert in online search"
    prompt: "You are an expert in online search"
    tools: [search]
    verbose: true
  - name: oracle
    role: "Answers questions about people's life and death"
    prompt: "You are the Oracle and you make up stories about people's life and death."
    verbose: true
```

tools.yaml:
```yaml
tools:
  - name: add
    module: tools.sample_tools
    function: add
  - name: subtract
    module: tools.sample_tools
    function: subtract
  - name: multiply
    module: tools.sample_tools
    function: multiply
  - name: divide
    module: tools.sample_tools
    function: divide
  - name: search
    module: tools.search_tools
    function: search_ddg
```


"""

# Sample config files
# tools.yaml
# agents.yaml

from llama_crew.helper import get_openai_api_key
OPENAI_API_KEY = get_openai_api_key()

import nest_asyncio
nest_asyncio.apply()

import yaml
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.tools import FunctionTool
from llama_crew.tools import Tool, load_tools_config
from llama_index.llms.openai import OpenAI
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent import AgentRunner
from llama_index.core.bridge.pydantic import PrivateAttr
from llama_index.core.agent import (
    CustomSimpleAgentWorker,
    Task,
    AgentChatResponse,
)
from typing import Dict, Any, Tuple, Optional
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core import ChatPromptTemplate
from llama_index.core.selectors import PydanticSingleSelector
from llama_index.core.bridge.pydantic import Field, BaseModel
from llama_index.core.llms import ChatMessage, MessageRole
from llama_crew.chat.utils import DEFAULT_PROMPT_STR, ResponseEval, get_chat_prompt_template

# get current path of the file
import os
current_path = os.path.dirname(os.path.abspath(__file__))
tools_config = load_tools_config(os.path.join(current_path,'tools.yaml'))

all_tools = [Tool(config) for config in tools_config["tools"]]

llm = OpenAI(model="gpt-3.5-turbo")

initial_tools = [ FunctionTool.from_defaults(fn=fn.instance) for fn in all_tools]

agents_config = yaml.safe_load(open(os.path.join(current_path,'agents.yaml'), 'r'))

agents = dict()


class SimpleAgentWorker(CustomSimpleAgentWorker):
    """Agent worker that adds a retry layer on top of a router.

    Continues iterating until there's no errors / task is done.

    """

    prompt_str: str = Field(default=DEFAULT_PROMPT_STR)
    role_prompt: str = Field(default="You are a AI assistant.")
    max_iterations: int = Field(default=3)
    __fields_set__: set =  {"prompt_str", "max_iterations","role_prompt"}
    _router_query_engine: RouterQueryEngine = PrivateAttr()
    

    def __init__(self, **kwargs: Any) -> None:
        """Initialize agent worker."""
        self.tools = []
        self.role_prompt = kwargs.get("role_prompt", "") + DEFAULT_PROMPT_STR
        self._router_query_engine = RouterQueryEngine(
            selector=PydanticSingleSelector.from_defaults(),
            query_engine_tools=self.tools,
            verbose=kwargs.get("verbose", False),
        )
        super().__init__(
            tools=[],
            **kwargs,
        )

    def _initialize_state(self, task: Task, **kwargs: Any) -> Dict[str, Any]:
        """Initialize state."""
        return {"count": 0, "current_reasoning": []}

    def _run_step(
        self, state: Dict[str, Any], task: Task, input: Optional[str] = None
    ) -> Tuple[AgentChatResponse, bool]:
        """Run step.

        Returns:
            Tuple of (agent_response, is_done)

        """
        if "new_input" not in state:
            new_input = task.input
        else:
            new_input = state["new_input"]

        if self.verbose:
            print(f"> Querying engine: {new_input}")
        
        if self.verbose:
            print(f"> Prompt: {self.role_prompt}")
        response = self.llm.complete(self.role_prompt + new_input)

            
        # append to current reasoning
        state["current_reasoning"].extend(
            [("user", new_input), ("assistant", str(response))]
        )
        is_done = True
        

        if self.verbose:
            print(f"> Question: {new_input}")
            print(f"> Response: {response}")
            # print(f"> Response eval: {response_eval.dict()}")

        # return response
        return AgentChatResponse(response=str(response)), is_done

    def _finalize_task(self, state: Dict[str, Any], **kwargs) -> None:
        """Finalize task."""
        # nothing to finalize here
        # this is usually if you want to modify any sort of
        # internal state beyond what is set in `_initialize_state`
        pass


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
    

# agents.keys()

# agents["oracle"].query(" When will I get married?")


# agents["oracle"].state

# agents["mathematician"].query("How much is 10 / 3 * 3")

# agents["mathematician"].state

# agents['ceo_expert'].query("What is the best way to increase revenue?")

class Orchestrator:
    system_prompt = "You are the orchestrator. You can ask any of the agents: [{agents_list}] and forward the response to the user Given the follow question from the user:\n"
    def __init__(self, llm, agents, **kwargs):
        self.llm = llm
        self.agents = agents
        self.agents_config = kwargs.get("agents_config", {})
        self.verbose = kwargs.get("verbose", False)
        
    def query(self, query):
        prompt = self.system_prompt.format(agents_list=[(agent["name"],agent["role"]) for agent in self.agents_config["agents"]])
        step = self.llm.complete( prompt + query +  "\n\nRespond with the name of the agent to call and the query to forward to the agent in the following format: 'agent_name: query'")
        agent_name, agent_query = str(step).split(":")
        if self.verbose:
            print(f"Forwarding the query to the agent {agent_name} with the query: {agent_query}")
        response = self.query_agent(agent_name.strip(), agent_query.strip())
        if self.verbose:
            print(f"Agent {agent_name} responded with: {response}")
        eval_response = self.eval_response(query, agent_name.strip(), agent_query.strip(), response)
        if self.verbose:
            print(f"Response evaluation: {eval_response}")
        return response, eval_response
        
    
    def eval_response(self, task, agent_name, query, response):
        system_prompt = f"Given the follow question from the user:\n{task}\n\nThe response from the agent {agent_name} to the query {query} is:\n{response}\n\nPlease evaluate the response in the following format: 'has_error: new_question: explanation'"
        return self.llm.complete(system_prompt)

    def query_agent(self, agent_name, query):
        return self.agents[agent_name].query(query)

director = Orchestrator(llm, agents, agents_config=agents_config, verbose=True)

# director.query("Ask the oracle When will I get married?")

# director.query("How much is 10 / 3 * 3")

# director.query("Today is May 20th, What was the dollar price on ethereum back in May 1st 2024?")

# director.query("Use python requests to get the current price of bitcoin and print it out.")


director.query("list all the files in the current directory")
