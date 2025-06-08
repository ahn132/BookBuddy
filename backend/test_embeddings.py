from embeddings import TextEmbedder

def test_embeddings():
    # Initialize the embedder
    embedder = TextEmbedder()
    
    # Example text (replace with your actual chapter text)
    chapter_text = """
    This is a sample chapter text. It will be split into chunks and converted into embeddings.
    Each chunk will be stored in Pinecone with its metadata.
    The text will be processed in a way that maintains semantic meaning.
    """
    
    # Process the chapter
    num_chunks = embedder.process_book_chapter(chapter_text, "Chapter 1")
    print(f"Processed {num_chunks} chunks from the chapter")

if __name__ == "__main__":
    test_embeddings() 