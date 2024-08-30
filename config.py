import os




""" llm_model_to_use: There are two types
    1: Local 
    2: Online
    ## Local: 
        For Local you have to provide all parameters 
        -   "type": "Local",            
                # provide to type to call local pipeline

        -   "service":"Mistral",        
                # This is service name

        -   'model_name': "Mistral OpenOrca", 
                # Any name you want to see in interface

        -   'tokenizer': "Open-Orca/Mistral-7B-OpenOrca", 
                # provide model tokenizer path fom huggingface
           
        -   'model_path': incase custom of hf path
                * custom_path    =   "D:/Bilal/mistral-7b-openorca.gguf2.Q4_0.gguf",
                * hf_path        =    "TheBloke/Mistral-7B-OpenOrca-GGUF",
        
        -   'model_file': 'mistral-7b-openorca.Q4_0.gguf',
                # model specific file to download

        -   'context_length': 4096,
                # provide context length

        -   'max_new_tokens': -1,
                # -1 uses the all max tokens

        -   'custom_path':True
                # in case you are providing the custom path make it True

    ## Online
        While for Online you can skip the 
            -   'tokenizer': None,
            -   'model_path': None,
            -   'context_length': None,
            -   'max_new_tokens': None,

            BUT you have to provede the  Exact 
            -   "type":"Online",
            -   "service": "OpenAI",
            -   'model_name': "gpt-4o", this can be changed
"""
llm_model_to_use = {

    "1":{
        "type": "Local",
        "service":"Mistral",
        'model_name': "Mistral OpenOrca",

        'tokenizer': "Open-Orca/Mistral-7B-OpenOrca",
        'model_path': "TheBloke/Mistral-7B-OpenOrca-GGUF",
        'model_file': 'mistral-7b-openorca.Q4_0.gguf',
        'context_length': 4096,
        'max_new_tokens': -1,
        'custom_path':True # use if you are providing custom path from disk
    },
    "2":{
        "type":"Online",
        "service": "OpenAI",
        'model_name': "gpt-3.5-turbo",
        
        'tokenizer': None,
        'model_path': None,

        'context_length': 16_385,
        'max_new_tokens': None,
    },
    "3":{
        "type":"Online",
        "service": "OpenAI",
        'model_name': "gpt-4o",
        
        'tokenizer': None,
        'model_path': None,

        'context_length': 128_000,
        'max_new_tokens': None,
    },
}

""" embedding_to_use: There are two types
    ## Online:
        For online provide the name for embedding and lenght of it while other should be same
        -   "type":"Online",
        -   "service": "OpenAI",
        -   "name":"text-embedding-ada-002",    # service name form openai
        -   "lenght": 1536
    ## Local:
        You have to provide its name = huggingface path and service name 
            -   "type":"Local",
            -   "service": "BAAI",
            -   "name":"BAAI/bge-small-en-v1.5",    # hf_path 
            -   "lenght": 384
"""
embedding_to_use = {
   
    "1":{
        "type":"Online",
        "service": "OpenAI",
        "name":"text-embedding-ada-002",
        "lenght": 1536
        },

    "2":{
        "type":"Local",
        "service": "BAAI",
        "name":"BAAI/bge-small-en-v1.5",
        "lenght": 384
    }

}

config = {
    # upload dir
    'uploads_dir': './uploads',
    # highlighted downloads
    'highlight_downloads_dir':'./highlight_downloads',
    # saved chromadb dir name
    'chromadb_path':'./chromadb_index_saved',
    # saved huggingface_models
    'save_hf_models':'./models/save_hf_models',
    # saved llm_models
    'save_llm_models':'./models/save_llm_models',
    #  Upload multiple files
    "multiple_file_selection": True, # True or False

    # default selcted models
    "default_llm_model":"2",
    "default_embedding_model":"1",
    #openai api key value
    'OPENAI_API_KEY' : os.getenv('OPENAI_API_KEY'),
    # Huggingface token
    'HF_TOKEN':os.getenv('HF_TOKEN'),

    #model temp
    'temperature':0.7,
    # doc retrieval
    'top_k':3,
    # use of GPU layes 0: CPU
    'gpu_layers': 0, #CPU = 0


    # System Prompt for Local LLM
    'system_prompt': """Always assist with care, respect, and truth. \
Respond with utmost utility yet securely. \
Avoid harmful, unethical, prejudiced, or negative content. \
Ensure replies promote fairness and positivity.\
    """,

    # Query Prompt 
    'user_qa_prompt': """Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 
    """,

}

os.makedirs(config['save_hf_models'], exist_ok=True)
os.makedirs(config['save_hf_models'], exist_ok=True)
os.environ['HF_HOME'] = config['save_hf_models']