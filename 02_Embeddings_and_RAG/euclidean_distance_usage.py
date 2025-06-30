"""
Euclidean Distance Usage Examples for Pythonic RAG Assignment

This file contains code examples showing how to use the new Euclidean distance
functions that were added to vectordatabase.py in your RAG pipeline.
"""

# Import the new distance functions
from aimakerspace.vectordatabase import euclidean_distance, normalized_euclidean_distance
from aimakerspace.vectordatabase import cosine_similarity

def compare_distance_metrics(query: str, vector_db, k: int = 3):
    """
    Compare different distance metrics for the same query.
    
    Args:
        query: The search query
        vector_db: Your vector database instance
        k: Number of results to retrieve
    
    Returns:
        Dictionary with results for each metric
    """
    metrics = {
        "Cosine Similarity": cosine_similarity,
        "Euclidean Distance": euclidean_distance,
        "Normalized Euclidean": normalized_euclidean_distance
    }
    
    results = {}
    
    for metric_name, metric_func in metrics.items():
        try:
            results[metric_name] = vector_db.search_by_text(
                query, k=k, distance_measure=metric_func
            )
        except Exception as e:
            results[metric_name] = f"Error: {str(e)}"
    
    return results

def enhanced_rag_pipeline_with_metrics(vector_db, chat_openai, rag_system_prompt, rag_user_prompt):
    """
    Enhanced RAG pipeline that supports different distance metrics.
    """
    class EnhancedRAGPipeline:
        def __init__(self, llm, vector_db_retriever, 
                     response_style: str = "detailed", include_scores: bool = False,
                     distance_metric: str = "cosine") -> None:
            self.llm = llm
            self.vector_db_retriever = vector_db_retriever
            self.response_style = response_style
            self.include_scores = include_scores
            self.distance_metric = distance_metric
            
            # Map metric names to functions
            self.metric_functions = {
                "cosine": cosine_similarity,
                "euclidean": euclidean_distance,
                "normalized_euclidean": normalized_euclidean_distance
            }

        def run_pipeline(self, user_query: str, k: int = 4, **system_kwargs) -> dict:
            # Get the appropriate distance metric
            distance_func = self.metric_functions.get(self.distance_metric, cosine_similarity)
            
            # Retrieve relevant contexts using selected metric
            context_list = self.vector_db_retriever.search_by_text(
                user_query, 
                k=k, 
                distance_measure=distance_func
            )
            
            context_prompt = ""
            similarity_scores = []
            
            for i, (context, score) in enumerate(context_list, 1):
                context_prompt += f"[Source {i}]: {context}\n\n"
                similarity_scores.append(f"Source {i}: {score:.3f}")
            
            # Create system message with parameters
            system_params = {
                "response_style": self.response_style,
                "response_length": system_kwargs.get("response_length", "detailed")
            }
            
            formatted_system_prompt = rag_system_prompt.create_message(**system_params)
            
            user_params = {
                "user_query": user_query,
                "context": context_prompt.strip(),
                "context_count": len(context_list),
                "similarity_scores": f"Relevance scores ({self.distance_metric}): {', '.join(similarity_scores)}" if self.include_scores else ""
            }
            
            formatted_user_prompt = rag_user_prompt.create_message(**user_params)

            return {
                "response": self.llm.run([formatted_system_prompt, formatted_user_prompt]), 
                "context": context_list,
                "context_count": len(context_list),
                "similarity_scores": similarity_scores if self.include_scores else None,
                "distance_metric": self.distance_metric,
                "prompts_used": {
                    "system": formatted_system_prompt,
                    "user": formatted_user_prompt
                }
            }
    
    return EnhancedRAGPipeline

# Example usage code (copy this into your notebook):

"""
# Cell 50: Using Euclidean Distance in RAG

## Import the new distance functions
from aimakerspace.vectordatabase import euclidean_distance, normalized_euclidean_distance

## Test query
test_query = "What is the 'Michael Eisner Memorial Weak Executive Problem'?"

## Using Cosine Similarity (original)
cosine_results = vector_db.search_by_text(
    test_query, 
    k=3, 
    distance_measure=cosine_similarity
)

## Using Euclidean Distance (new)
euclidean_results = vector_db.search_by_text(
    test_query, 
    k=3, 
    distance_measure=euclidean_distance
)

## Using Normalized Euclidean Distance (recommended)
norm_euclidean_results = vector_db.search_by_text(
    test_query, 
    k=3, 
    distance_measure=normalized_euclidean_distance
)

print("=== COSINE SIMILARITY RESULTS ===")
for i, (text, score) in enumerate(cosine_results, 1):
    print(f"Source {i} (Score: {score:.3f}): {text[:100]}...")

print("\n=== EUCLIDEAN DISTANCE RESULTS ===")
for i, (text, score) in enumerate(euclidean_results, 1):
    print(f"Source {i} (Score: {score:.3f}): {text[:100]}...")

print("\n=== NORMALIZED EUCLIDEAN RESULTS ===")
for i, (text, score) in enumerate(norm_euclidean_results, 1):
    print(f"Source {i} (Score: {score:.3f}): {text[:100]}...")

## Enhanced RAG Pipeline with Distance Metric Selection
EnhancedRAGPipeline = enhanced_rag_pipeline_with_metrics(vector_db, chat_openai, rag_system_prompt, rag_user_prompt)

# Test with Cosine Similarity
cosine_pipeline = EnhancedRAGPipeline(
    vector_db_retriever=vector_db,
    llm=chat_openai,
    response_style="detailed",
    include_scores=True,
    distance_metric="cosine"
)

cosine_result = cosine_pipeline.run_pipeline(test_query, k=3)

# Test with Euclidean Distance
euclidean_pipeline = EnhancedRAGPipeline(
    vector_db_retriever=vector_db,
    llm=chat_openai,
    response_style="detailed",
    include_scores=True,
    distance_metric="euclidean"
)

euclidean_result = euclidean_pipeline.run_pipeline(test_query, k=3)

print("=== COSINE SIMILARITY RAG RESULTS ===")
print(f"Response: {cosine_result['response']}")
print(f"Distance Metric: {cosine_result['distance_metric']}")
print(f"Similarity Scores: {cosine_result['similarity_scores']}")

print("\n=== EUCLIDEAN DISTANCE RAG RESULTS ===")
print(f"Response: {euclidean_result['response']}")
print(f"Distance Metric: {euclidean_result['distance_metric']}")
print(f"Similarity Scores: {euclidean_result['similarity_scores']}")

## Compare all metrics
comparison_results = compare_distance_metrics(test_query, vector_db, k=3)

print("=== DISTANCE METRIC COMPARISON ===")
for metric_name, results in comparison_results.items():
    print(f"\n{metric_name}:")
    if isinstance(results, list):
        for i, (text, score) in enumerate(results, 1):
            print(f"  Source {i} (Score: {score:.3f}): {text[:80]}...")
    else:
        print(f"  {results}")
"""

# Key differences between metrics:
METRIC_COMPARISON = """
### Key Differences Between Metrics:

| Metric | Range | Best For | Interpretation |
|--------|-------|----------|----------------|
| **Cosine Similarity** | [-1, 1] | Direction similarity | Higher = more similar |
| **Euclidean Distance** | [0, ∞) | Overall similarity | Lower = more similar |
| **Normalized Euclidean** | [0, 1] | Scaled comparison | Lower = more similar |

### When to Use Each Metric:

- **Cosine Similarity**: Best for semantic similarity, ignores magnitude
- **Euclidean Distance**: Best for precise matching, considers both direction and magnitude  
- **Normalized Euclidean**: Best for fair comparison across different vector dimensions
"""

print("Euclidean distance usage examples ready! Copy the code from the comments above into your notebook.") 