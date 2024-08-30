"""
Wrap the text generation with llama-index CustomLLM to set the default model in settings.
"""
from typing import Any
from llama_index.core.callbacks import CallbackManager
from llama_index.core.llms import (
    CustomLLM,
    CompletionResponse,
    CompletionResponseGen,
    LLMMetadata,
)
from llama_index.core.llms.callbacks import llm_completion_callback

from typing import Optional
from llama_index.core.bridge.pydantic import (
    PrivateAttr,
    Field
    )

from local_llm.text_generator import TextGenerator
class OurLLM(CustomLLM):
    """
    Custom LLM class to interface with the TextGenerator.
    """
    # system_prompt: Optional[str] = Field(
    #     default=None, description="System prompt for LLM calls."
    # )
    _text_generator: Any = PrivateAttr()
    _model_config: Any = PrivateAttr()
    def __init__(self,model_config):
        super().__init__()
        self._model_config = model_config
        self._text_generator = TextGenerator(model_config=self._model_config)

    @property
    def metadata(self) -> LLMMetadata:
        """
        Get LLM metadata.
        """
        return LLMMetadata(
            context_window=self._model_config['context_length'],
            num_output=self._model_config['max_new_tokens'],
            model_name=self._model_config['model_name'],
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """
        Complete the given prompt using the text generator.
        """
        gen_text = self._text_generator.generate_text(user_prompt=prompt)
        return CompletionResponse(text=gen_text)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """
        Stream the completion of the given prompt using the text generator.
        """
        gen_text = self._text_generator.generate_text(user_prompt=prompt)
        response = ""
        for token in gen_text:
            response += token
            yield CompletionResponse(text=response, delta=token)

# # Set the custom LLM in settings
# Settings.llm = OurLLM()

# # Set the embedding model
# Settings.embed_model = HuggingFaceEmbedding(
#     model_name="BAAI/bge-small-en-v1.5"
# )

# Usage:
# llm = OurLLM()
# r = llm.complete("How are you?")
# print(r.text)
