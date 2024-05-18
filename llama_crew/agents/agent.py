from llama_index.core.agent import (
    CustomSimpleAgentWorker,
    Task,
    AgentChatResponse,
)
from llama_index.core.bridge.pydantic import Field, BaseModel
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.bridge.pydantic import PrivateAttr
from typing import Dict, Any, Tuple, Optional
from llama_index.core.selectors import PydanticSingleSelector
from llama_crew.chat.utils import DEFAULT_PROMPT_STR

class Orchestrator:
    system_prompt = "You are the orchestrator. You job is to forward the user's request to the agent to follow answer the request. You can ask any of the agents: [{agents_list}] and forward the response to the user Given the follow question from the user:\n"
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
