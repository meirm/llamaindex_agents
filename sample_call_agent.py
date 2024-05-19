#!/usr/bin/env python
# coding: utf-8

import argparse
from llama_crew.helper import get_openai_api_key
OPENAI_API_KEY = get_openai_api_key()

import nest_asyncio
nest_asyncio.apply()

import yaml
from llama_crew.tools import Tool, load_tools_config
from llama_index.llms.openai import OpenAI
from llama_crew.agents.agent import Orchestrator
from llama_crew.agents.loader import load_agents

# get current path of the file
import os
current_path = os.path.dirname(os.path.abspath(__file__))
defaults = {"tools_config": os.path.join(current_path,'tools.yaml'), "agents_config": os.path.join(current_path,'agents.yaml')}

parser = argparse.ArgumentParser(description='Run the orchestrator')
parser.add_argument('--tools_config', type=str, default=defaults["tools_config"], help='Path to the tools configuration file')
parser.add_argument('--agents_config', type=str, default=defaults["agents_config"], help='Path to the agents configuration file')
parser.add_argument("--verbose", action="store_true", help="Print out the responses from the agents and the evaluation of the responses.")
parser.add_argument("agent", type=str, help="The agent to call")
parser.add_argument('query', nargs=argparse.REMAINDER, help='The query to send to the orchestrator')
args = parser.parse_args()

tools_config = load_tools_config(args.tools_config)
all_tools = [Tool(config) for config in tools_config["tools"]]
llm = OpenAI(model="gpt-3.5-turbo")

agents_config = yaml.safe_load(open(args.agents_config, 'r'))


agents = load_agents(llm, agents_config, all_tools)
    

agents[args.agent].query("".join(args.query))
