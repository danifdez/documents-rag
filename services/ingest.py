from bs4 import BeautifulSoup
import uuid
import re
from qdrant_client.models import PointStruct
from database.database import get_database
from services.embedding_service import get_embedding_service

def ingest(source_id: str, project_id: str, content: str) -> bool:
    """
    Ingests the provided text for the given source and project.

    Args:
        source_id (str): The ID of the source.
        project_id (str): The ID of the project.
        content (str): The text to ingest.

    Returns:
        bool: True if ingestion was successful, False otherwise.
    """
    database = get_database()
    embedding_service = get_embedding_service()
    
    clean_content = _clean_html_text(content)

    if not clean_content:
        return True

    chunks = _chunk_text(clean_content)

    chunk_embeddings = embedding_service.encode(chunks, normalize_embeddings=True)

    points = []
    part_number = 0
    for chunk, embedding in zip(chunks, chunk_embeddings):
        part_number += 1
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={"text": chunk, "source_id": source_id, "project_id": project_id, "part_number": part_number}
            )
        )

    if points:
        database.upsert_points(points=points)
    
    return True


# Function to extract text from each HTML block element and return as array
def _clean_html_text(html_content):
    """
    Extract complete text from each HTML block element, ignoring inline formatting tags.
    """
    if not html_content:
        return []
    
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style"]):
        script.decompose()
    
    block_elements = [
        'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
        'li', 'td', 'th', 'blockquote', 'pre', 'section', 
        'article', 'header', 'footer', 'main', 'aside'
    ]
    
    text_elements = []
    
    for tag_name in block_elements:
        for element in soup.find_all(tag_name):
            text = element.get_text()
            text = re.sub(r'\s+', ' ', text.strip())
            
            if text:
                text_elements.append(text)
    
    soup_copy = BeautifulSoup(html_content, 'html.parser')
    for script in soup_copy(["script", "style"]):
        script.decompose()
    
    for tag_name in block_elements:
        for element in soup_copy.find_all(tag_name):
            element.decompose()
    
    remaining_text = soup_copy.get_text()
    remaining_text = re.sub(r'\s+', ' ', remaining_text.strip())
    if remaining_text:
        text_elements.append(remaining_text)
    
    return text_elements

# Function to chunk text array into approximately 200 word chunks without splitting elements
def _chunk_text(text_elements, words_per_chunk=200):
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for text_element in text_elements:
        element_word_count = len(text_element.split())
        
        if current_word_count + element_word_count > words_per_chunk and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [text_element]
            current_word_count = element_word_count
        else:
            current_chunk.append(text_element)
            current_word_count += element_word_count
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks