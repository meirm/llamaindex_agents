
# https://github.com/run-llama/llama_index/blob/767de070b231fb328b6c0640c2e002c9c7af0a83/docs/docs/examples/agent/custom_agent.ipynb#L12

from typing import List
from llama_index.core.bridge.pydantic import Field, BaseModel
from llama_index.core.output_parsers import PydanticOutputParser

from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import json

class Task(BaseModel):
    input: str
    context: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
class Step(BaseModel):
    agent: str
    subtask: str
    
class Plan(BaseModel):
    goal: str
    steps: List[Step]
class Orchestrator:
    system_prompt = (
        "DATE: {todays_date}\n\n"
        "You are the orchestrator. At your disposal, you have the following list of agents: {agents_list}\n"
        "Your job is to decompose the user's task into simple steps, each to be executed by a specific agent that you can choose from the agents list.\n"
        "Once you have the responses from the agents, you need to combine them into a coherent final answer to solve the task.\n\n"
        "TASK: {task}\n\n"
        )
    
    def __init__(self, llm, agents, **kwargs):
        self.llm = llm
        self.agents = agents #{agent["name"]: agent for agent in agents}
        self.agents_config = kwargs.get("agents_config", {})
        self.verbose = kwargs.get("verbose", False)
        
    def query(self, task):
        now = datetime.now()
        agent_list = [(agent["name"], agent["role"]) for agent in self.agents_config["agents"]]
        prompt = self.system_prompt.format(agents_list=agent_list,task=task, todays_date=now.strftime("%Y-%m-%d"))
        response_format = PydanticOutputParser(Plan)
        response = self.llm.complete(prompt + response_format.format_string)
        steps = json.loads(str(response))["steps"]
        steps = [f"{step['agent']}: {step['subtask']}" for step in steps]
        if self.verbose:
            print(f"Received the following task: {task}")
            print(f"Steps: [{steps}]")
        responses = []
        for step in steps:
            if step.strip() == "":
                continue
            agent_name, agent_query = step.split(":", 1)
            agent_prompt = (
                "Given the User's task: {task}\n"
                "And the following query from the orchestrator: {query}\n"
                "Please provide a response to the query."
            )
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
        prompt = (
            "Given the following task from the user: {task}\n"
            "And the following responses from agents: {responses}\n"
            "Please determine if the orchestrator can stop querying agents.\n"
            "ANSWER: Yes/No"
        )
        response = self.llm.complete(prompt.format(task=task, responses=responses))
        if "Yes" in str(response):
            return True
        return False
    
    def combine_responses(self, original_query, responses):
        # Generic logic to combine responses from different agents based on the original query context
        system_prompt = (
            f"Given the following original query from the user:\n{original_query}\n\n"
            f"And the following responses from agents:\n{responses}\n\n"
            "Please combine these responses into a coherent final answer."
        )
        combined_response = self.llm.complete(system_prompt)
        return combined_response
        
    def eval_response(self, task, agent_name, query, response):
        system_prompt = (
            f"Given the following question from the user:\n{task}\n\n"
            f"The response from {agent_name} to the query {query} is:\n{response}\n\n"
            "Please evaluate the response in the following format: 'has_error: new_question: explanation'"
        )
        return self.llm.complete(system_prompt)
    
    def query_agent(self, agent_name, query):
        return self.agents[agent_name].query(query)

