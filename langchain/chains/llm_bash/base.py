"""Chain that interprets a prompt and executes bash code to perform bash operations."""
from typing import Dict, List

from pydantic import BaseModel, Extra

from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.chains.llm_bash.prompt import PROMPT
from langchain.input import print_text
from langchain.llms.base import LLM
from langchain.utilities.bash import BashProcess


class LLMBashChain(Chain, BaseModel):
    """Chain that interprets a prompt and executes bash code to perform bash operations.

    Example:
        .. code-block:: python

            from langchain import LLMBashChain, OpenAI
            llm_bash = LLMBashChain(llm=OpenAI())
    """

    llm: LLM
    """LLM wrapper to use."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        llm_executor = LLMChain(prompt=PROMPT, llm=self.llm)
        bash_executor = BashProcess()
        if self.verbose:
            print_text(inputs[self.input_key])

        t = llm_executor.predict(question=inputs[self.input_key])
        if self.verbose:
            print_text(t, color="green")

        t = t.strip()
        if t.startswith("```bash"):
            # Split the string into a list of substrings
            command_list = t.split("\n")
            print(command_list)

            # Remove the first and last substrings
            command_list = [s for s in command_list[1:-1]]
            output = bash_executor.run(command_list)

            if self.verbose:
                print_text("\nAnswer: ")
                print_text(output, color="yellow")

        else:
            raise ValueError(f"unknown format from LLM: {t}")
        return {self.output_key: output}
