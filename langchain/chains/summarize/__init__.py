"""Load summarizing chains."""
from typing import Any, Mapping, Protocol

from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.refine import RefineDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import map_reduce_prompt, refine_prompts, stuff_prompt
from langchain.llms.base import LLM
from langchain.prompts.base import BasePromptTemplate


class LoadingCallable(Protocol):
    """Interface for loading the combine documents chain."""

    def __call__(self, llm: LLM, **kwargs: Any) -> BaseCombineDocumentsChain:
        """Callable to load the combine documents chain."""


def _load_stuff_chain(
    llm: LLM,
    prompt: BasePromptTemplate = stuff_prompt.PROMPT,
    document_variable_name: str = "text",
    **kwargs: Any,
) -> StuffDocumentsChain:
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    # TODO: document prompt
    return StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name=document_variable_name, **kwargs
    )


def _load_map_reduce_chain(
    llm: LLM,
    map_prompt: BasePromptTemplate = map_reduce_prompt.PROMPT,
    combine_prompt: BasePromptTemplate = map_reduce_prompt.PROMPT,
    combine_document_variable_name: str = "text",
    map_reduce_document_variable_name: str = "text",
    **kwargs: Any,
) -> MapReduceDocumentsChain:
    map_chain = LLMChain(llm=llm, prompt=map_prompt)
    reduce_chain = LLMChain(llm=llm, prompt=combine_prompt)
    # TODO: document prompt
    combine_document_chain = StuffDocumentsChain(
        llm_chain=reduce_chain, document_variable_name=combine_document_variable_name
    )
    return MapReduceDocumentsChain(
        llm_chain=map_chain,
        combine_document_chain=combine_document_chain,
        document_variable_name=map_reduce_document_variable_name,
        **kwargs,
    )


def _load_refine_chain(
    llm: LLM,
    question_prompt: BasePromptTemplate = refine_prompts.PROMPT,
    refine_prompt: BasePromptTemplate = refine_prompts.REFINE_PROMPT,
    document_variable_name: str = "text",
    initial_response_name: str = "existing_answer",
    **kwargs: Any,
) -> RefineDocumentsChain:
    initial_chain = LLMChain(llm=llm, prompt=question_prompt)
    refine_chain = LLMChain(llm=llm, prompt=refine_prompt)
    return RefineDocumentsChain(
        initial_llm_chain=initial_chain,
        refine_llm_chain=refine_chain,
        document_variable_name=document_variable_name,
        initial_response_name=initial_response_name,
        **kwargs,
    )


def load_summarize_chain(
    llm: LLM, chain_type: str = "stuff", **kwargs: Any
) -> BaseCombineDocumentsChain:
    """Load summarizing chain.

    Args:
        llm: Language Model to use in the chain.
        chain_type: Type of document combining chain to use. Should be one of "stuff",
            "map_reduce", and "refine".

    Returns:
        A chain to use for summarizing.
    """
    loader_mapping: Mapping[str, LoadingCallable] = {
        "stuff": _load_stuff_chain,
        "map_reduce": _load_map_reduce_chain,
        "refine": _load_refine_chain,
    }
    if chain_type not in loader_mapping:
        raise ValueError(
            f"Got unsupported chain type: {chain_type}. "
            f"Should be one of {loader_mapping.keys()}"
        )
    return loader_mapping[chain_type](llm, **kwargs)
