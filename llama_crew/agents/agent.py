
# https://github.com/run-llama/llama_index/blob/767de070b231fb328b6c0640c2e002c9c7af0a83/docs/docs/examples/agent/custom_agent.ipynb#L12

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
    system_prompt = "You are the orchestrator, at your disposition you have the following list of agents: [{agents_list}]\n" + \
    "Your job is to decompose the user's task into simple steps where each step is to be executed by a specific agent.\n"  + \
    "STEPS FORMAT:\n<agent_name>:<subtask>;<agent_name>:<subtask>;\n" + \
    "EXAMPLES:\nmathematician: What is the square root of 16?;\n" + \
    "crypto_trader:Price of Bitcoin in USD;crypto_trader:FX rate USD to EUR;mathematician:Calculate price of BTC in EUR;\n" + \
    "FINALLY:\nOnce you have the responses from the agents, you need to combine them into a coherent final answer.\n" + \
    "TASK: {task}\n\n"
    
    def __init__(self, llm, agents, **kwargs):
        self.llm = llm
        self.agents = agents #{agent["name"]: agent for agent in agents}
        self.agents_config = kwargs.get("agents_config", {})
        self.verbose = kwargs.get("verbose", False)
        
    def query(self, task):
        agent_list = [(agent["name"], agent["role"]) for agent in self.agents_config["agents"]]
        prompt = self.system_prompt.format(agents_list=agent_list,task=task)
        steps = self.llm.complete(prompt)
        steps = str(steps).strip().split(";")
        if self.verbose:
            print(f"Received the following task: {task}")
            print(f"Steps: [{steps}]")
        responses = []
        for step in steps:
            if step.strip() == "":
                continue
            agent_name, agent_query = step.split(":", 1)
            agent_prompt = "Given the User's task: {task}\n" + \
                                 "And the following query from the orchestrator: {query}\n" + \
                                    "Please provide a response to the query."
            if self.verbose:    
                print(f"Calling agent {agent_name} with the query: {agent_query}")
            response = self.query_agent(agent_name.strip(), agent_prompt.format(task=task, query=agent_query.strip()))
            if self.verbose:
                print(f"Agent {agent_name} responded with: {response}")
            responses.append(response)
            if (self.can_stop(task, responses)):
                break
        combined_responses = " ".join(str(responses))
        combined_response = self.combine_responses(task, combined_responses)
        eval_response = self.eval_response(task, "orchestrator", task, combined_response)
        if self.verbose:
            print(f"Response evaluation: {eval_response}")
        return combined_response, eval_response
    
    def can_stop(self, task, responses):
        # Generic logic to determine if the orchestrator can stop querying agents based on the responses so far
        prompt = "Given the following task from the user: {task}\n" + \
                    "And the following responses from agents: {responses}\n" + \
                    "Please determine if the orchestrator can stop querying agents.\n ANSWER: Yes/No"
        response = self.llm.complete(prompt.format(task=task, responses=responses))
        if "Yes" in str(response):
            return True
        return False
    
    def combine_responses(self, original_query, responses):
        # Generic logic to combine responses from different agents based on the original query context
        system_prompt = f"Given the following original query from the user:\n{original_query}\n\n" \
                        f"And the following responses from agents:\n" \
                        f"{responses}\n\n" \
                        f"Please combine these responses into a coherent final answer."
        combined_response = self.llm.complete(system_prompt)
        return combined_response
        
    def eval_response(self, task, agent_name, query, response):
        system_prompt = f"Given the following question from the user:\n{task}\n\nThe response from {agent_name} to the query {query} is:\n{response}\n\nPlease evaluate the response in the following format: 'has_error: new_question: explanation'"
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
