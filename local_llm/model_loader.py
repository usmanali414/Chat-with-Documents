"""
This module handles the loading of the model, embedding-model and tokenizer as singletons.
"""

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from config import embedding_to_use, llm_model_to_use, config
from llama_index.core import Settings
from local_llm.custom_llm import OurLLM

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding



class ModelLoader:
    """
    Class to load and provide access to model and tokenizer.
    """
    def __init__(
        self,
        default_llm_key=config['default_llm_model'],
        default_embedding_key=config['default_embedding_model']
        ):
        self.default_llm_key = default_llm_key
        self.default_embedding_key = default_embedding_key

    def load_embedding_model(self, select_embedding_model_key = None):
        if select_embedding_model_key is None:
            print("Selecting Default Embeddings...")
            select_embedding_model_key = self.default_embedding_key

        embedding_data = embedding_to_use[select_embedding_model_key]
        embedding_type = embedding_data['type']
        embedding_model_name = embedding_data['name']
        
        if embedding_type  == "Local":
            print(f"Loading the `Local` embedding model: name = {embedding_model_name}...")
            embed_model = HuggingFaceEmbedding(model_name=embedding_model_name)
            
            Settings.embed_model = embed_model
            # print(Settings.embed_model.get_text_embedding("Hello"))
        else:
            print(f"Loading the `Online` embedding model: name = {embedding_model_name}...")
            self.online_embedding_services(embedding_config=embedding_data)

    def load_llm_model(self, select_llm_model_key = None):
        if select_llm_model_key is None:
            print("Selecting Default LLM Model...")
            select_llm_model_key = self.default_llm_key

        llm_model_data = llm_model_to_use[select_llm_model_key]
        model_type = llm_model_data['type']
        model_in_use = llm_model_data['model_name']

        if model_type  == "Local":
            print(f"Loading the Local LLM Model: name = {model_in_use}")
            Settings.llm = OurLLM(model_config=llm_model_data)
        else:
            print(f"Loading the Online LLM Model: name = {model_in_use}...")
            self.online_model_services(llm_config=llm_model_data)
    
    def online_model_services(self, llm_config):
        model_service = llm_config['service']

        model = llm_config['model_name']
        max_tokens = llm_config['max_new_tokens']

        temp = config['temperature']

        kwargs = {
            'model': model,
            }

        if temp is not None:
            kwargs['temperature'] = temp
        if max_tokens is not None:
            kwargs['max_tokens'] = max_tokens
        
        # USE THE API SERVICES
        if model_service == "OpenAI":
            Settings.llm = OpenAI(api_key=config['OPENAI_API_KEY'],**kwargs)
    
    def online_embedding_services(self, embedding_config):
        model_service = embedding_config['service']

        model_name = embedding_config['name']
        # USE THE API SERVICES
        if model_service == "OpenAI":
            Settings.embed_model = OpenAIEmbedding(api_key=config['OPENAI_API_KEY'],model=model_name)



        
    