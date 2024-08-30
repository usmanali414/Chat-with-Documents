import os
from PyPDF2 import PdfReader
from typing import List,Dict
from llama_index.core.schema import Document

class CustomDirectoryReader():
    def __init__(self) -> None:
        pass
    def documnet_nodes(self, dir_path:str) -> List[Document]:
        processd_docs = self.read_documnets(dir_path=dir_path)
        if processd_docs == []:
            return []
        documents = []
        for data in processd_docs:
            documents.append(Document(
                text=data['text'],
                metadata=data['metadata']
            ))
        return documents
    
    def read_documnets(self, dir_path:str) -> List[Dict]:
        if not os.path.exists(dir_path):
            print("Directory path does not exist.")
            return []

        all_files = os.listdir(dir_path)
        if all_files == []:
            print(f"No document found in directory: {dir_path}")
            return []
            
        doc_list = []
        for file in all_files:
            reader = PdfReader(os.path.join(dir_path,file))
            all_pages = len(reader.pages)
            for page_no in range(all_pages):
                page = reader.pages[page_no]
                text = page.extract_text()
                doc_list.append(
                    {
                    'text':text,
                    'metadata':{
                        'file_name':file,
                        'page_label':page_no+1
                        }
                }
                )
        return doc_list
