import os
from typing import List, Dict, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from langchain.schema import Document
from langchain_openai import ChatOpenAI
import numpy as np
from vector_store import AdvancedVectorStore
from web_search_api import WebSearchAPI
import json

class AdvancedRetrieval:
    """Advanced retrieval with cross-encoder re-ranking, query expansion, and contextual compression"""
    
    def __init__(self):
        print("🚀 Initializing Advanced Retrieval System...")
        
        # Initialize base components
        self.vector_store = AdvancedVectorStore()
        self.web_search = WebSearchAPI()
        
        # Initialize cross-encoder for re-ranking
        self.cross_encoder_model = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.cross_encoder_model)
            self.cross_encoder = AutoModelForSequenceClassification.from_pretrained(self.cross_encoder_model)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.cross_encoder.to(self.device)
            print(f"✅ Cross-encoder loaded on {self.device}")
        except Exception as e:
            print(f"⚠️ Cross-encoder failed to load: {e}")
            self.cross_encoder = None
        
        # Initialize LLM for query expansion and compression
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        print("✅ Advanced Retrieval System ready")
    
    def retrieve_with_cross_encoder(self, query: str, k: int = 5, initial_k: int = 20) -> List[Document]:
        """
        Retrieve documents using cross-encoder re-ranking
        1. Get initial_k candidates from vector store
        2. Re-rank with cross-encoder
        3. Return top k
        """
        print(f"\n🔍 Advanced retrieval for: '{query}'")
        
        # Step 1: Get initial candidates from vector store
        initial_results = self.vector_store.search_similar(query, k=initial_k)
        
        if not initial_results['documents']:
            print("⚠️ No initial results found")
            return []
        
        # Step 2: Re-rank with cross-encoder
        if self.cross_encoder:
            reranked_docs = self._cross_encoder_rerank(query, initial_results)
        else:
            # Fallback to original order if cross-encoder not available
            reranked_docs = self._convert_to_documents(initial_results)
        
        # Return top k after re-ranking
        return reranked_docs[:k]
    
    def _cross_encoder_rerank(self, query: str, search_results: Dict) -> List[Document]:
        """Re-rank documents using cross-encoder"""
        documents = search_results['documents']
        metadatas = search_results['metadatas']
        
        # Prepare pairs for cross-encoder
        pairs = [[query, doc] for doc in documents]
        
        # Tokenize and score
        with torch.no_grad():
            inputs = self.tokenizer(pairs, padding=True, truncation=True, 
                                   max_length=512, return_tensors='pt').to(self.device)
            scores = self.cross_encoder(**inputs).logits.squeeze(-1).cpu().numpy()
        
        # Sort by scores
        sorted_indices = np.argsort(scores)[::-1]
        
        # Create reranked documents
        reranked_docs = []
        for idx in sorted_indices:
            doc = Document(
                page_content=documents[idx],
                metadata={
                    **metadatas[idx],
                    'cross_encoder_score': float(scores[idx]),
                    'original_rank': idx + 1
                }
            )
            reranked_docs.append(doc)
        
        print(f"✅ Re-ranked {len(reranked_docs)} documents with cross-encoder")
        return reranked_docs
    
    def query_expansion(self, original_query: str, num_expansions: int = 3) -> List[str]:
        """Use LLM to generate query expansions"""
        prompt = f"""Given the customer success query: "{original_query}"
        
        Generate {num_expansions} alternative search queries that would help find relevant survey responses.
        Consider synonyms, related concepts, and different phrasings.
        
        Return ONLY a JSON list of queries, nothing else:
        """
        
        try:
            response = self.llm.invoke(prompt)
            expanded_queries = json.loads(response.content)
            expanded_queries.insert(0, original_query)  # Include original
            
            print(f"✅ Expanded query to {len(expanded_queries)} variations")
            return expanded_queries[:num_expansions + 1]
        
        except Exception as e:
            print(f"⚠️ Query expansion failed: {e}")
            return [original_query]
    
    def contextual_compression(self, query: str, documents: List[Document], max_length: int = 200) -> List[Document]:
        """Compress document content to only relevant parts"""
        compressed_docs = []
        
        for doc in documents:
            prompt = f"""Given this query: "{query}"
            
            Extract ONLY the most relevant 1-2 sentences from this text that directly answer or relate to the query:
            
            Text: {doc.page_content}
            
            Return only the extracted sentences, nothing else:
            """
            
            try:
                response = self.llm.invoke(prompt)
                compressed_content = response.content.strip()
                
                compressed_doc = Document(
                    page_content=compressed_content,
                    metadata={
                        **doc.metadata,
                        'original_length': len(doc.page_content),
                        'compressed_length': len(compressed_content),
                        'compression_ratio': len(compressed_content) / len(doc.page_content)
                    }
                )
                compressed_docs.append(compressed_doc)
                
            except Exception as e:
                print(f"⚠️ Compression failed for document: {e}")
                compressed_docs.append(doc)  # Keep original if compression fails
        
        print(f"✅ Compressed {len(compressed_docs)} documents")
        return compressed_docs
    
    def hybrid_retrieval(self, query: str, k: int = 5) -> Dict:
        """
        Complete advanced retrieval pipeline:
        1. Query expansion
        2. Retrieve from multiple sources (vector store + web)
        3. Cross-encoder re-ranking
        4. Contextual compression
        """
        print(f"\n🔬 Running hybrid advanced retrieval for: '{query}'")
        
        # Step 1: Query expansion
        expanded_queries = self.query_expansion(query, num_expansions=2)
        
        # Step 2: Retrieve from vector store with expanded queries
        all_internal_docs = []
        for exp_query in expanded_queries:
            docs = self.retrieve_with_cross_encoder(exp_query, k=k, initial_k=15)
            all_internal_docs.extend(docs)
        
        # Remove duplicates based on content
        seen_content = set()
        unique_internal_docs = []
        for doc in all_internal_docs:
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                unique_internal_docs.append(doc)
        
        # Step 3: Get external web context
        web_results = self.web_search.search(query, num_results=3)
        web_docs = [
            Document(
                page_content=result['snippet'],
                metadata={
                    'source': 'web',
                    'title': result['title'],
                    'link': result['link'],
                    'search_source': result['source']
                }
            )
            for result in web_results
        ]
        
        # Step 4: Combine and re-rank all sources
        all_docs = unique_internal_docs[:k] + web_docs
        if self.cross_encoder and len(all_docs) > k:
            # Re-rank combined results
            combined_results = {
                'documents': [doc.page_content for doc in all_docs],
                'metadatas': [doc.metadata for doc in all_docs]
            }
            all_docs = self._cross_encoder_rerank(query, combined_results)[:k]
        
        # Step 5: Contextual compression
        compressed_docs = self.contextual_compression(query, all_docs[:k])
        
        return {
            'query': query,
            'expanded_queries': expanded_queries,
            'documents': compressed_docs,
            'retrieval_stats': {
                'total_candidates': len(all_internal_docs) + len(web_docs),
                'internal_sources': len(unique_internal_docs),
                'external_sources': len(web_docs),
                'final_results': len(compressed_docs),
                'used_cross_encoder': self.cross_encoder is not None
            }
        }
    
    def _convert_to_documents(self, search_results: Dict) -> List[Document]:
        """Convert search results to Document objects"""
        docs = []
        for i, content in enumerate(search_results['documents']):
            metadata = search_results['metadatas'][i] if i < len(search_results['metadatas']) else {}
            docs.append(Document(page_content=content, metadata=metadata))
        return docs
    
    def compare_retrieval_methods(self, query: str, k: int = 5) -> Dict:
        """Compare basic vs advanced retrieval for evaluation"""
        print(f"\n📊 Comparing retrieval methods for: '{query}'")
        
        # Basic retrieval (current system)
        basic_results = self.vector_store.search_similar(query, k=k)
        basic_docs = self._convert_to_documents(basic_results)
        
        # Advanced retrieval
        advanced_results = self.hybrid_retrieval(query, k=k)
        
        comparison = {
            'query': query,
            'basic_retrieval': {
                'documents': basic_docs,
                'count': len(basic_docs),
                'method': 'vector_similarity'
            },
            'advanced_retrieval': {
                'documents': advanced_results['documents'],
                'count': len(advanced_results['documents']),
                'method': 'hybrid_with_reranking',
                'stats': advanced_results['retrieval_stats']
            }
        }
        
        return comparison