"""Wrapper around Cohere embedding models."""
import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Extra, root_validator

from langchain.embeddings.base import Embeddings


class CohereEmbeddings(BaseModel, Embeddings):
    """Wrapper around Cohere embedding models.

    To use, you should have the ``cohere`` python package installed, and the
    environment variable ``COHERE_API_KEY`` set with your API key or pass it
    as a named parameter to the constructor.

    Example:
        .. code-block:: python

            from langchain.embeddings import CohereEmbeddings
            cohere = CohereEmbeddings(model_name="medium", cohere_api_key="my-api-key")
    """

    client: Any  #: :meta private:
    model: str = "medium"
    """Model name to use."""

    cohere_api_key: Optional[str] = os.environ.get("COHERE_API_KEY")

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        cohere_api_key = values.get("cohere_api_key")

        if cohere_api_key is None or cohere_api_key == "":
            raise ValueError(
                "Did not find Cohere API key, please add an environment variable"
                " `COHERE_API_KEY` which contains it, or pass `cohere_api_key` as a"
                " named parameter."
            )
        try:
            import cohere

            values["client"] = cohere.Client(cohere_api_key)
        except ImportError:
            raise ValueError(
                "Could not import cohere python package. "
                "Please it install it with `pip install cohere`."
            )
        return values

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Call out to Cohere's embedding endpoint.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        embeddings = self.client.embed(model=self.model, texts=texts).embeddings
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Call out to Cohere's embedding endpoint.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        embedding = self.client.embed(model=self.model, texts=[text]).embeddings[0]
        return embedding
