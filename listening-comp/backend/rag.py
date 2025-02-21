from langchain import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore

class TranscriptRAG:
    def __init__(self, supabase_client):
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=self.embeddings,
            table_name="transcripts"
        )
    
    def store_transcript(self, transcript, metadata):
        """Store transcript in vector database"""
        texts = [chunk['text'] for chunk in transcript]
        self.vector_store.add_texts(
            texts=texts,
            metadatas=[metadata] * len(texts)
        )
    
    def generate_questions(self, transcript):
        """Generate listening comprehension questions"""
        # Template for question generation
        template = """
        Generate 3 listening comprehension questions based on this transcript:
        {transcript}
        
        Format as JSON with questions, options, and correct answers.
        """
        # Implementation continues...
