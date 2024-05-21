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
parser.add_argument('--model', type=str, default='gpt-3.5-turbo', help='The model to use for the orchestrator')
parser.add_argument('--api_key', type=str, default=OPENAI_API_KEY, help='The OpenAI API key')
parser.add_argument('--api_base', type=str, default='https://api.openai.com/v1', help='The OpenAI API base URL')
parser.add_argument('--agents_config', type=str, default=defaults["agents_config"], help='Path to the agents configuration file')
parser.add_argument("--verbose", action="store_true", help="Print out the responses from the agents and the evaluation of the responses.")
# The query to send to the orchestrator, take all the rest of the arguments as the query even when not enclosed in quotes
parser.add_argument('query', nargs=argparse.REMAINDER, help='The query to send to the orchestrator')
args = parser.parse_args()

tools_config = load_tools_config(args.tools_config)
all_tools = [Tool(config) for config in tools_config["tools"]]
llm = OpenAI(model=args.model,api_key=args.api_key, api_base=args.api_base) #"http://localhost:1234/v1")

agents_config = yaml.safe_load(open(args.agents_config, 'r'))

agents = load_agents(llm, agents_config, all_tools)

director = Orchestrator(llm, agents, agents_config=agents_config, verbose=args.verbose)

director.query(" ".join(args.query))
