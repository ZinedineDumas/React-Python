"""Main entrypoint into package."""

from typing import Optional

from langchain.agents import MRKLChain, ReActChain, SelfAskWithSearchChain
from langchain.cache import BaseCache
from langchain.chains import (
    ConversationChain,
    LLMBashChain,
    LLMChain,
    LLMCheckerChain,
    LLMMathChain,
    PALChain,
    QAWithSourcesChain,
    SQLDatabaseChain,
    VectorDBQA,
    VectorDBQAWithSourcesChain,
)
from langchain.docstore import InMemoryDocstore, Wikipedia
from langchain.llms import Cohere, HuggingFaceHub, OpenAI
from langchain.llms.huggingface_pipeline import HuggingFacePipeline
from langchain.logger import BaseLogger, StdOutLogger
from langchain.prompts import (
    BasePromptTemplate,
    FewShotPromptTemplate,
    Prompt,
    PromptTemplate,
)
from langchain.serpapi import SerpAPIChain, SerpAPIWrapper
from langchain.sql_database import SQLDatabase
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.vectorstores import FAISS, ElasticVectorSearch

logger: BaseLogger = StdOutLogger()
verbose: bool = False
llm_cache: Optional[BaseCache] = None

__all__ = [
    "LLMChain",
    "LLMBashChain",
    "LLMCheckerChain",
    "LLMMathChain",
    "SelfAskWithSearchChain",
    "SerpAPIWrapper",
    "SerpAPIChain",
    "GoogleSearchAPIWrapper",
    "Cohere",
    "OpenAI",
    "BasePromptTemplate",
    "Prompt",
    "FewShotPromptTemplate",
    "PromptTemplate",
    "ReActChain",
    "Wikipedia",
    "HuggingFaceHub",
    "HuggingFacePipeline",
    "SQLDatabase",
    "SQLDatabaseChain",
    "FAISS",
    "MRKLChain",
    "VectorDBQA",
    "ElasticVectorSearch",
    "InMemoryDocstore",
    "ConversationChain",
    "VectorDBQAWithSourcesChain",
    "QAWithSourcesChain",
    "PALChain",
]
