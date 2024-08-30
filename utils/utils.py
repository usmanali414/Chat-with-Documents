ALLOWED_EXTENSIONS = {'pdf'}  # Set of allowed extensions

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


import chromadb
from llama_index.core import Settings
from config import config
def all_saved_index_dbs_paths():
    embedding_name = Settings.embed_model.model_name
    chroma_db_path = config['chromadb_path']
    chroma_db_index_path = f'{chroma_db_path}/{embedding_name}/'
    print(chroma_db_index_path)
    # saved_embedding_model = "/".join(chroma_db_index_path.split("/")[-3:-1])
    db = chromadb.PersistentClient(path=chroma_db_index_path)
    collections = db.list_collections()
    # print("collections",collections)
    return [coll.name for coll in collections]
def singlton_class(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance