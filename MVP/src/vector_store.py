import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from typing import List, Dict
import os
import json

# Simple in-memory vector store that actually works
class AdvancedVectorStore:
    """Advanced vector store with in-memory storage and embeddings"""
    
    def __init__(self):
        print("🔧 Initializing AdvancedVectorStore...")
        
        # Better embedding model
        try:
            self.embedding_model = OpenAIEmbeddings(
                model="text-embedding-3-small",
                api_key=os.getenv("OPENAI_API_KEY")
            )
            print("✅ OpenAI embeddings initialized")
        except Exception as e:
            print(f"⚠️ OpenAI embeddings failed: {e}")
            self.embedding_model = None
        
        # Smart text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=750,
            chunk_overlap=100,
            length_function=self.tiktoken_len,
        )
        
        # Simple in-memory storage
        self.documents = []
        self.embeddings_cache = {}
        
        print("✅ Vector store initialized with in-memory storage")
    
    def tiktoken_len(self, text: str) -> int:
        """Count actual tokens using tiktoken"""
        try:
            tokens = tiktoken.encoding_for_model("gpt-4").encode(text)
            return len(tokens)
        except:
            return len(text.split())
    
    def add_survey(self, text: str, metadata: dict):
        """Add survey response with smart chunking"""
        try:
            print(f"📝 Adding survey: {text[:50]}...")
            
            # For survey responses, usually don't need chunking as they're short
            # But we'll do minimal chunking for consistency
            chunks = self.text_splitter.split_text(text) if len(text) > 800 else [text]
            
            for i, chunk in enumerate(chunks):
                # Create document with metadata
                doc_metadata = {
                    **metadata,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "source_text": text[:100] + "..." if len(text) > 100 else text
                }
                
                document = Document(
                    page_content=chunk,
                    metadata=doc_metadata
                )
                
                self.documents.append(document)
            
            print(f"✅ Added {len(chunks)} document chunks. Total documents: {len(self.documents)}")
            
        except Exception as e:
            print(f"❌ Error adding survey: {e}")
            # Still add the document even if processing fails
            doc = Document(page_content=text, metadata=metadata)
            self.documents.append(doc)
    
    def search_similar(self, query: str, k: int = 5) -> Dict:
        """Enhanced similarity search using embeddings or keyword matching"""
        try:
            print(f"🔍 Searching for: '{query}' in {len(self.documents)} documents")
            
            if not self.documents:
                print("⚠️ No documents to search")
                return {"query": query, "documents": [], "metadatas": [], "scores": []}
            
            # Try embedding-based search first
            if self.embedding_model:
                try:
                    return self._embedding_search(query, k)
                except Exception as e:
                    print(f"⚠️ Embedding search failed: {e}, falling back to keyword search")
            
            # Fallback to keyword search
            return self._keyword_search(query, k)
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return {"query": query, "documents": [], "metadatas": [], "scores": []}
    
    def _embedding_search(self, query: str, k: int) -> Dict:
        """Embedding-based similarity search"""
        # Get query embedding
        query_embedding = self.embedding_model.embed_query(query)
        
        # Calculate similarities
        similarities = []
        for i, doc in enumerate(self.documents):
            # Get or calculate document embedding
            doc_text = doc.page_content
            if doc_text not in self.embeddings_cache:
                doc_embedding = self.embedding_model.embed_query(doc_text)
                self.embeddings_cache[doc_text] = doc_embedding
            else:
                doc_embedding = self.embeddings_cache[doc_text]
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((doc, similarity, i))
        
        # Sort by similarity and take top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:k]
        
        return {
            "query": query,
            "documents": [doc.page_content for doc, _, _ in top_results],
            "metadatas": [doc.metadata for doc, _, _ in top_results],
            "scores": [float(score) for _, score, _ in top_results]
        }
    
    def _keyword_search(self, query: str, k: int) -> Dict:
        """Simple keyword-based search"""
        query_words = set(query.lower().split())
        matches = []
        
        for doc in self.documents:
            doc_words = set(doc.page_content.lower().split())
            # Calculate overlap score
            overlap = len(query_words.intersection(doc_words))
            if overlap > 0:
                score = overlap / len(query_words)
                matches.append((doc, score))
        
        # Sort by score and take top k
        matches.sort(key=lambda x: x[1], reverse=True)
        top_matches = matches[:k]
        
        print(f"🔍 Keyword search found {len(matches)} matches, returning top {len(top_matches)}")
        
        return {
            "query": query,
            "documents": [doc.page_content for doc, _ in top_matches],
            "metadatas": [doc.metadata for doc, _ in top_matches],
            "scores": [score for _, score in top_matches]
        }
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_context_for_query(self, query: str) -> List[Document]:
        """Get relevant context documents for RAG"""
        try:
            search_results = self.search_similar(query, k=5)
            
            # Convert search results back to Documents
            documents = []
            for i, doc_content in enumerate(search_results["documents"]):
                metadata = search_results["metadatas"][i] if i < len(search_results["metadatas"]) else {}
                documents.append(Document(page_content=doc_content, metadata=metadata))
            
            print(f"📄 Retrieved {len(documents)} context documents for RAG")
            return documents
            
        except Exception as e:
            print(f"❌ Context retrieval error: {e}")
            # Return some documents as fallback
            return self.documents[:5] if self.documents else []
    
    def count(self) -> int:
        """Get total number of stored documents"""
        count = len(self.documents)
        print(f"📊 Document count: {count}")
        return count