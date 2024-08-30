from flask import Flask, render_template, url_for, request, flash, redirect, session, jsonify, send_file
import os
import json
import utils.utils as utils
from zipfile import ZipFile
from config import config,llm_model_to_use,embedding_to_use
from local_llm.model_loader import ModelLoader
import chromadb
from llama_index.core import StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore

from llama_index.core import Settings
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core import PromptTemplate
from utils.custom_doc_reader import CustomDirectoryReader
from utils.highlight_pdf_text import HighlightText
app = Flask(__name__)

app.secret_key = 'your_secret_key_here'

load_models = ModelLoader()
load_models.load_embedding_model()

load_models.load_llm_model()
custom_doc_reader_obj=CustomDirectoryReader()
text_highliter = HighlightText()

context_index = None
processed_documents = None
default_llm = None
default_embedd = None
loaded_index = None
retrieval_page = False
content_found = []
@app.context_processor
def context_processor():
    """ Using Values in Flask Html Templates
    """
    values = {
        "multiple_file_selection": config['multiple_file_selection'], 
        # "openai_gpt_models": config['openai_gpt_models'],
        "llm_model_to_use": llm_model_to_use,
        "embedding_to_use": embedding_to_use,
        "default_llm_model_key":default_llm if default_llm else config['default_llm_model'],
        "default_embedding_model_key":default_embedd if default_embedd else config['default_embedding_model'],
        "db_collections_list": utils.all_saved_index_dbs_paths(),
        "processed_documents":processed_documents,
        "loaded_index":loaded_index,
        "retrieval_page":retrieval_page,
    }
    return values

@app.route('/')
def index_page():
    """ Home Page
    """
    global retrieval_page
    retrieval_page = False
    
    prompts = {"user_qa_prompt":config['user_qa_prompt']}
    
    
    uploaded_docs = []

    if not os.path.exists(config['uploads_dir']) and not  os.path.isdir(config['uploads_dir']):
        os.makedirs(config['uploads_dir'], exist_ok=True)
        flash("Upload directory created.")
    
    else:
        # If the upload directory exists and is a directory
        uploaded_docs = [file for file in os.listdir(config['uploads_dir'])]
       
    return render_template('index.html', uploaded_docs=uploaded_docs,prompts=prompts)

@app.route('/data-retrieval')
def data_retrieval_index():
    global retrieval_page
    retrieval_page = True
    prompts = {"user_qa_prompt":config['user_qa_prompt']}
    
    
    uploaded_docs = []

    if not os.path.exists(config['uploads_dir']) and not  os.path.isdir(config['uploads_dir']):
        os.makedirs(config['uploads_dir'], exist_ok=True)
        flash("Upload directory created.")
    
    else:
        # If the upload directory exists and is a directory
        uploaded_docs = [file for file in os.listdir(config['uploads_dir'])]
       
    return render_template('data-retrieval.html', uploaded_docs=uploaded_docs,prompts=prompts)
    


@app.route('/upload', methods=['POST'])
def upload_doc():
    """ Upload Files
    """
    redirect_page = request.form.get('redirect_page')
    print(redirect_page)
    msj=""
    uploaded_files = request.files.getlist('files')
    for file in uploaded_files:
        if file and utils.allowed_file(file.filename):
            
            file_path = os.path.join(config['uploads_dir'], file.filename)
            file.save(file_path)

            msj= f"{file.filename} uploaded successfully"
            flash(msj)
            
        else:
            flash(f'{file.filename}. Only "{", ".join(utils.ALLOWED_EXTENSIONS)}" files are allowed.')
    
    if redirect_page == 'index_page':
        return redirect(url_for('index_page'))
    else:
        return redirect(url_for('data_retrieval_index'))
    

@app.route('/delete_uploads')
def delete_uploads():
    """ Delete documents from upload dir
    """

    try:

        for filename in os.listdir(config['uploads_dir']):
            file_path = os.path.join(config['uploads_dir'], filename)
            os.remove(file_path)
        
        flash("Upload Files are Delete.")
        return redirect('/')
    except Exception as e:
        flash(str(e))
        return redirect('/')

@app.route('/settings',methods=['POST'])
def setting_default_components():
    global default_llm
    global default_embedd
    global loaded_index
    loaded_index = None

    saved_settings = request.form
    selected_llm_model_key = saved_settings['selected_llm_model_key']
    selected_embedding_model_key = saved_settings['selected_embedding_model_key']
    
    if selected_llm_model_key != default_llm:
        load_models.load_llm_model(select_llm_model_key=selected_llm_model_key)
    if selected_embedding_model_key != default_embedd:
        load_models.load_embedding_model(select_embedding_model_key=selected_embedding_model_key)

    default_embedd = selected_embedding_model_key
    default_llm = selected_llm_model_key
    return jsonify({"status": "success", "message": "Settings updated successfully"})

@app.route('/docs-process', methods=['GET'])
def docs_process():
    """ Process the documents to get all text from it.
    and store it into Cache memory
    """
    global context_index
    global processed_documents 
    print("SimpleDirectoryReader Initailizing...")
    processed_documents = SimpleDirectoryReader(config['uploads_dir']).load_data()
    print("Documents Loaded Sucessfully!!\n-------------\n")
    return {"working": "well"}

@app.route('/save-index',methods=["POST"])
def saving_index():
    global context_index
    global loaded_index

    form_input = request.form
    chroma_db_name = form_input['chroma_collection_name']
    chunk_size = form_input['chunk_size']
    chunk_overlap = form_input['chunk_overlap']
    read_page_by_page = form_input['read_page_by_page']

    embedding_name = Settings.embed_model.model_name

    chroma_db_path = config['chromadb_path']
    chroma_db_index_path = f'{chroma_db_path}/{embedding_name}/'

    # if processed_documents is not None:
    # save to disk
    db = chromadb.PersistentClient(path=chroma_db_index_path)
    chroma_collection = db.get_or_create_collection(chroma_db_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    if read_page_by_page == "True":
        print("CustomDirectoryReader Initailizing...")
        processed_documents = custom_doc_reader_obj.documnet_nodes(config['uploads_dir'])
        print("Documents Loaded Sucessfully!!\n-------------\n")
        
        if processed_documents == []:
            return jsonify({"status": "error", "message": f"Sorry could not process page by page documents reading."})
        else:
            # Save Context with provide chunks sizes 
            context_index = VectorStoreIndex(
                processed_documents, storage_context=storage_context, show_progress=True
            )
    else:
        # Setting Default Chunk Size
        Settings.chunk_size = int(chunk_size)
        Settings.chunk_overlap = int(chunk_overlap)
        print("SimpleDirectoryReader Initailizing...")
        processed_documents = SimpleDirectoryReader(config['uploads_dir']).load_data()
        print("Documents Loaded Sucessfully!!\n-------------\n")

        # Save Context with provide chunks sizes 
        context_index = VectorStoreIndex.from_documents(
            processed_documents, storage_context=storage_context, show_progress=True
        )

    loaded_index = chroma_db_name
    return jsonify({"status": "success", "message": f"('{chroma_db_name}'): Index saved and loaded successfully!"})

@app.route('/load-index',methods=['POST'])  
def load_index():
    global context_index
    global loaded_index
    
    form_input = request.form
    selected_collection = form_input['selected_collection']
    
    embedding_name = Settings.embed_model.model_name
    
    chroma_db_path = config['chromadb_path']
    
    correct_embed_model = False
    for value in embedding_to_use.values():
        if value['name'] == embedding_name:
            correct_embed_model = True
            saved_embedding_model = os.path.join(chroma_db_path, embedding_name)
        

    if correct_embed_model:
        loaded_index = selected_collection
        # load from disk
        db = chromadb.PersistentClient(path=saved_embedding_model)
        chroma_collection = db.get_or_create_collection(selected_collection)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        context_index = VectorStoreIndex.from_vector_store(
            vector_store
        )
        return jsonify({"status": "success", "message": "Document Vector Index Loaded."})
    else:
        print(f"Please use {embedding_name} for this index")
        return jsonify({"status": "error", "message": f"Please Use embedding: `{embedding_name}` for vectore index."})

@app.route('/delete-index',methods=['DELETE'])  
def delete_index():
    global loaded_index
    
    form_input = request.form
    selected_collection = form_input['selected_collection']
    
    embedding_name = Settings.embed_model.model_name
    
    chroma_db_path = config['chromadb_path']
    
    correct_embed_model = False
    for value in embedding_to_use.values():
        if value['name'] == embedding_name:
            correct_embed_model = True
            saved_embedding_model = os.path.join(chroma_db_path, embedding_name)
        

    if correct_embed_model:
        loaded_index = None
        # load from disk
        db = chromadb.PersistentClient(path=saved_embedding_model)
        db.delete_collection(name=selected_collection)
        return jsonify({"status": "success", "message": "Document Vector Index Deleted."})
    else:
        print(f"Please use {embedding_name} for this index")
        return jsonify({"status": "error", "message": f"Please Use embedding: `{embedding_name}` for vectore index."})

@app.route('/chat', methods=['POST'])
def user_input():
    """ Chat Completion on user_query
    """
    global context_index
    if context_index is None:
        return "Documents index not found. Please upload documents and process documents or load saved documents index."
    
    response = ""
   
    # Getting values from the form
    user_input = request.form
    user_qa_prompt = user_input["user_qa_prompt"]
    user_query = user_input["user_query"]
    top_k = user_input["top_k"]

    if top_k is None or top_k=="":
        top_k = config['top_k']

    # Check if the keywords not provides
    if "{context_str}" not in user_qa_prompt and "{query_str}" not in user_qa_prompt:
        return "Please Insert {context_str} and {query_str} keywords inside Q&A Prompt."
    
    # Setting default prompt
    qa_template = PromptTemplate(user_qa_prompt)
    query_engine = context_index.as_query_engine(
                text_qa_template=qa_template
            )
   
    # if user enter the query processd else not
    if user_query:
        try:
            """Completion of user and system message from openai API
            
            returns: 
                dictionary contains keys gpt_response and tokens(prompt, completion, total)
            """
            # Query and print response
            query_engine = context_index.as_query_engine(
                text_qa_template=qa_template,
                similarity_top_k = int(top_k)
            )
            print('Generating response...')
            response = query_engine.query(user_query)
            print('Generated!!!')
            print(response.response)
            return response.response

        except Exception as e:
            
            response = f" Error Occurred while Generating response.{e}"
    else:
        response = "Sorry, I am unable to understand your query."


    return str(response)


@app.route('/retrieval-chat', methods=['POST'])
def retrieval_user_input():
    global context_index
    global context_index
    global content_found

    if context_index is None:
        return "Documents index not found. Please upload documents and process documents or load saved documents index."
    

    user_input = request.form
    query = user_input["msg"]
    top_k = user_input["top_k_retrieval"]
    
    if top_k is None or top_k=="":
        top_k = config['top_k']

    file_name_list = []
    file_content = ""
    content_found = []
    if query:
        retriever = context_index.as_retriever(similarity_top_k=int(top_k))
        doc_retrieved = retriever.retrieve(query)
        # doc_retrieved
        for doc in doc_retrieved:
            filename = doc.metadata['file_name']
            page_no = doc.metadata['page_label']
            file_name_list.append(filename)
            text = f"""Documents: {filename}\
                    Score: {round(doc.score,2)} \
                    Page No: {page_no} \
                    Documents content: {doc.text}"""
            file_content += text
            content_found.append(
                {
                    'file_name':filename,
                    'page_no':page_no,
                    'content':doc.text
                
                }
            )
        
        delimiter = '|split|'
        return   f"{file_content}{delimiter}{delimiter.join(set(file_name_list))}"

@app.route('/download-highlight-pdf',methods=['POST'])
def download_highlighted_pdf():
    global content_found
    if loaded_index:
        text_highliter.process_highlight(content_retrieved=content_found)

        zip_filename = 'highlighted_pdfs.zip'
        zip_path = os.path.join(config['highlight_downloads_dir'], zip_filename)
        
        # Create a zip file containing all PDFs in the config['highlight_downloads_dir'] directory
        with ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(config['highlight_downloads_dir']):
                for file in files:
                    if file.endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, config['highlight_downloads_dir']))

        # Return the zip file to the user
        return send_file(zip_path, as_attachment=True)
        # return jsonify({"status": "success", "message": f"Pdf Downloaded."})
    else:
        return jsonify({"status": "error", "message": f"Please Load Index."})



if __name__=="__main__":
    app.run(debug=True)