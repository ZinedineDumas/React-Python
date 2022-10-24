"""Chain that interprets a prompt and executes python code to do math."""
from typing import Dict, List

from pydantic import BaseModel, Extra

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.chains.llm_math.prompt import PROMPT
from langchain.chains.python import PythonChain
from langchain.llms.base import LLM


class LLMMathChain(Chain, BaseModel):
    """Chain that interprets a prompt and executes python code to do math."""

    llm: LLM
    verbose: bool = False
    input_key: str = "question"
    output_key: str = "answer"

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key."""
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key."""
        return [self.output_key]

    def _run(self, inputs: Dict[str, str]) -> Dict[str, str]:
        llm_executor = LLMChain(prompt=PROMPT, llm=self.llm)
        python_executor = PythonChain()
        question = inputs[self.input_key]
        t = llm_executor.predict(question=question, stop=["```output"]).strip()
        if t.startswith("```python"):
            code = t[9:-4]
            if self.verbose:
                print("[DEBUG] evaluating code")
                print(code)
            output = python_executor.run(code)
            answer = "Answer: " + output
        elif t.startswith("Answer:"):
            answer = t
        else:
            raise ValueError(f"unknown format from LLM: {t}")
        return {self.output_key: answer}

    def run(self, question: str) -> str:
        """More user-friendly interface for interfacing with LLM math."""
        return self({self.input_key: question})[self.output_key]
