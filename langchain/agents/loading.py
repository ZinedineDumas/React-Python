"""Functionality for loading agents."""
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Union

import requests
import yaml

from langchain.agents.agent import Agent
from langchain.agents.conversational.base import ConversationalAgent
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.react.base import ReActDocstoreAgent
from langchain.agents.self_ask_with_search.base import SelfAskWithSearchAgent
from langchain.chains.loading import load_chain, load_chain_from_config

AGENT_TO_CLASS = {
    "zero-shot-react-description": ZeroShotAgent,
    "react-docstore": ReActDocstoreAgent,
    "self-ask-with-search": SelfAskWithSearchAgent,
    "conversational-react-description": ConversationalAgent,
}

URL_BASE = "https://raw.githubusercontent.com/hwchase17/langchain-hub/master/agents/"


def load_agent_from_config(config: dict, **kwargs: Any) -> Agent:
    """Load agent from Config Dict."""
    if "_type" not in config:
        raise ValueError("Must specify an agent Type in config")
    config_type = config.pop("_type")

    if config_type not in AGENT_TO_CLASS:
        raise ValueError(f"Loading {config_type} agent not supported")

    agent_cls = AGENT_TO_CLASS[config_type]
    if "llm_chain" in config:
        config["llm_chain"] = load_chain_from_config(config.pop("llm_chain"))
    elif "llm_chain_path" in config:
        config["llm_chain"] = load_chain(config.pop("llm_chain_path"))
    else:
        raise ValueError("One of `llm_chain` and `llm_chain_path` should be specified.")
    combined_config = {**config, **kwargs}
    return agent_cls(**combined_config)  # type: ignore


def load_agent(path: Union[str, Path], **kwargs: Any) -> Agent:
    """Unified method for loading a agent from LangChainHub or local fs."""
    if isinstance(path, str) and path.startswith("lc://agents"):
        path = os.path.relpath(path, "lc://agents/")
        return _load_from_hub(path, **kwargs)
    else:
        return _load_agent_from_file(path, **kwargs)


def _load_from_hub(path: str, **kwargs: Any) -> Agent:
    """Load agent from hub."""
    suffix = path.split(".")[-1]
    if suffix not in {"json", "yaml"}:
        raise ValueError("Unsupported file type.")
    full_url = URL_BASE + path
    r = requests.get(full_url)
    if r.status_code != 200:
        raise ValueError(f"Could not find file at {full_url}")
    with tempfile.TemporaryDirectory() as tmpdirname:
        file = tmpdirname + "/agent." + suffix
        with open(file, "wb") as f:
            f.write(r.content)
        return _load_agent_from_file(file)


def _load_agent_from_file(file: Union[str, Path], **kwargs: Any) -> Agent:
    """Load agent from file."""
    # Convert file to Path object.
    if isinstance(file, str):
        file_path = Path(file)
    else:
        file_path = file
    # Load from either json or yaml.
    if file_path.suffix == ".json":
        with open(file_path) as f:
            config = json.load(f)
    elif file_path.suffix == ".yaml":
        with open(file_path, "r") as f:
            config = yaml.safe_load(f)
    else:
        raise ValueError("File type must be json or yaml")
    # Load the agent from the config now.
    return load_agent_from_config(config, **kwargs)
