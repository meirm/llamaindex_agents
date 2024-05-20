from llama_index.core import SummaryIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

# load documents
documents = SimpleDirectoryReader(input_files=["data/metagpt.pdf"]).load_data()

splitter = SentenceSplitter(chunk_size=1024)
nodes = splitter.get_nodes_from_documents(documents)

summary_index = SummaryIndex(nodes)
summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)

summary_tool = QueryEngineTool.from_defaults(
    name="summary_tool",
    query_engine=summary_query_engine,
    description=(
        "Useful if you want to get a summary of MetaGPT"
    ),
)