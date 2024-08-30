from ctransformers import AutoModelForCausalLM
from transformers import AutoTokenizer
import torch
import os
from huggingface_hub import hf_hub_download
from config import config


class TextGenerator:
    def __init__(self,model_config:dict):
        print("Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_config['tokenizer'])
        
        if not model_config['custom_path']:

            d_path = self.download_llm_model(
                model_path=model_config['model_path'],
                model_file=model_config['model_file']
            )

            model_loading_path = f"{config['save_llm_models']}/{model_config['model_file']}"
        else:
            d_path = True
            model_loading_path = model_config['model_path']
        
        if d_path is None:
            print("Could not load the model.")
        else:
            print(f"Loading ('{model_loading_path}') model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                model_loading_path,
                context_length=model_config['context_length'],
                max_new_tokens=model_config['max_new_tokens'],
                gpu_layers=config['gpu_layers']
            )
            print("Model Loaded!")
       
    def model_input_tokens(self, system_prompt, user_prompt, tokenize=True):
        messages = []
    
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": user_prompt})
        # for prompt in messages:
        #     print(f"Role: {prompt['role']}\nContent: {prompt['content']}")
        input_ids = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=tokenize,
        )
        
        return input_ids

    def generate_text(self, system_prompt=config['system_prompt'], user_prompt=str)->str:
        tokens = self.model_input_tokens(system_prompt=system_prompt,user_prompt=user_prompt)
      
        generated_text = ""
        for tok in self.model.generate(torch.tensor(tokens),temperature=config['temperature']):
            
            char = str(self.model.detokenize(tok))
            # print(char, end="", flush=True)
            generated_text += char
        
        return generated_text

    def download_llm_model(self,model_path,model_file):
        try:
            # Download the model from Hugging Face Hub
            llm_model_path = hf_hub_download(
                model_path,
                filename=model_file,
                local_dir=f"{config['save_llm_models']}/",  # Download the model to the "models" folder
                token=config['HF_TOKEN'] #Replace this token from huggingface with your own token (Setting -> Access Toekns -> New token -> Generate Token)
            )
            return llm_model_path
        except Exception as e:
            print(f"Error Downloading Model {model_path}\nError: {e}")
            return None

