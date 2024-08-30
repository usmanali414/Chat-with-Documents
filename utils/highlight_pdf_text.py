
import os
import pymupdf
from config import config
os.makedirs(config['highlight_downloads_dir'],exist_ok=True)
class HighlightText():
    def __init__(self):
        self.uploads_path = config['uploads_dir']
        self.download_path = config['highlight_downloads_dir']

    def highlight_text(self, page, query):
        
        # Search for the query in the page
        rects = page.search_for(query)
        if rects == []:  # If no matches found, return
            return 
        words = len(query.split(' '))  # Count the number of words in the query
        if words == 1:  # If single word, highlight all occurrences
            highlighted = page.add_highlight_annot(rects)
        else:  # If multiple words, highlight the entire text span
            p1 = rects[0].tl  # Top-left point of first rectangle
            p2 = rects[-1].br  # Bottom-right point of last rectangle
            page.add_highlight_annot(start=p1, stop=p2)

    def process_highlight(self,content_retrieved):
        opened_docs = {}
        for data in content_retrieved:
            file_name = data['file_name']
            page_no = data['page_no']
            content = data['content']
            pdf_path = f'{self.uploads_path}/{file_name}'
            # Check if document is already opened
            if pdf_path not in opened_docs:
                opened_docs[pdf_path] = pymupdf.open(pdf_path)
            
            doc = opened_docs[pdf_path]
            page = doc[int(page_no)-1]
            self.highlight_text(page=page,query=content)
        self.save_highlighted(opened_docs)

    def save_highlighted(self, opened_docs):
        
        for path in opened_docs.keys():
            save_file_name = path.split('/')[-1]
            print(f"Saving File: {path.split('/')[-1]}")

            save_path = f'{self.download_path}/{save_file_name}'
            doc = opened_docs[path]
            doc.save(save_path)
