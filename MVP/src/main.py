from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import os
from dotenv import load_dotenv

from llm_processor import process_survey
from vector_store import AdvancedVectorStore
from rag_generator import RAGGenerator

# Import advanced retrieval components
try:
    from advanced_retrieval import AdvancedRetrieval
    print("✅ Advanced retrieval imported successfully")
    ADVANCED_RETRIEVAL_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Advanced retrieval import failed: {e}")
    print("   Make sure you have transformers and torch installed")
    ADVANCED_RETRIEVAL_AVAILABLE = False
    AdvancedRetrieval = None

# Fix the import - use the correct module name
try:
    from ragas_evaluation import WorkingRAGASEvaluation as RAGASEvaluation
except ImportError:
    print("⚠️ RAGAS evaluation not available")
    RAGASEvaluation = None

# Use improved import with better error handling
try:
    from flagging_agent import LangGraphFlaggingAgent
    print("✅ LangGraph flagging agent imported successfully")
except ImportError as e:
    print(f"⚠️ LangGraph import failed: {e}")
    print("   Try: pip install 'langgraph>=0.2.20,<0.3'")
    LangGraphFlaggingAgent = None

load_dotenv()

app = FastAPI(title="Survey Sentinel - Enhanced Agent System", version="0.7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components with error handling
vector_store = AdvancedVectorStore()
rag_generator = RAGGenerator()

# Initialize advanced retrieval if available
if ADVANCED_RETRIEVAL_AVAILABLE:
    try:
        advanced_retrieval = AdvancedRetrieval()
        # Share the same vector store
        advanced_retrieval.vector_store = vector_store
        print("✅ Advanced retrieval system initialized")
    except Exception as e:
        print(f"⚠️ Advanced retrieval failed to initialize: {e}")
        advanced_retrieval = None
        ADVANCED_RETRIEVAL_AVAILABLE = False
else:
    advanced_retrieval = None

# Initialize flagging agent with fallback
if LangGraphFlaggingAgent:
    try:
        langgraph_flagger = LangGraphFlaggingAgent()
        print("✅ LangGraph flagging agent initialized")
    except Exception as e:
        print(f"⚠️ LangGraph agent failed to initialize: {e}")
        langgraph_flagger = None
else:
    print("⚠️ LangGraph not available, flagging features disabled")
    langgraph_flagger = None

# Initialize RAGAS evaluator
if RAGASEvaluation:
    try:
        ragas_evaluator = RAGASEvaluation()
        print("✅ RAGAS evaluator initialized")
    except Exception as e:
        print(f"⚠️ RAGAS evaluator failed to initialize: {e}")
        ragas_evaluator = None
else:
    print("⚠️ RAGAS evaluation not available")
    ragas_evaluator = None

@app.get("/")
async def root():
    agent_status = "enabled" if langgraph_flagger else "disabled"
    agent_type = langgraph_flagger.agent_type if langgraph_flagger else "none"
    ragas_status = "enabled" if ragas_evaluator else "disabled"
    advanced_retrieval_status = "enabled" if ADVANCED_RETRIEVAL_AVAILABLE else "disabled"
    
    return {
        "message": "Survey Sentinel - Enhanced Agent System", 
        "status": "running",
        "features": ["Advanced Vector Search", "RAG Analysis", "Advanced Retrieval"],
        "agent_features": f"LangGraph agents: {agent_status}",
        "evaluation_features": f"RAGAS evaluation: {ragas_status}",
        "advanced_retrieval": advanced_retrieval_status,
        "version": "0.7.0",
        "agent_type": agent_type
    }

@app.post("/ingest")
async def ingest_surveys_with_intelligent_agents(file: UploadFile = File(...)):
    """Ingest surveys with intelligent agent flagging (if available)"""
    try:
        # Load survey responses
        df = pd.read_csv(file.file)
        
        # Load customer master data for enrichment
        customer_master_path = 'data/customer_master.csv'
        if os.path.exists(customer_master_path):
            customer_master = pd.read_csv(customer_master_path)
            print(f"📋 Loaded customer master data: {len(customer_master)} customers")
            
            # Join survey responses with customer master data
            df_enriched = df.merge(
                customer_master[['customer_id', 'company_name', 'tier', 'mrr', 'segment', 'industry']], 
                on='customer_id', 
                how='left'
            )
            
            # Fill missing company names with customer_id as fallback
            df_enriched['company_name'] = df_enriched['company_name'].fillna(df_enriched['customer_id'])
            
            print(f"✅ Enriched {len(df_enriched)} survey responses with customer data")
        else:
            print("⚠️ Customer master file not found, using customer_id as names")
            df_enriched = df.copy()
            df_enriched['company_name'] = df_enriched['customer_id']
            df_enriched['tier'] = 'Unknown'
            df_enriched['mrr'] = 0
            df_enriched['segment'] = 'Unknown'
            df_enriched['industry'] = 'Unknown'
        
        flagged_results = []
        processed_count = 0
        
        print(f"📥 Processing {len(df_enriched)} survey responses...")
        
        for _, row in df_enriched.iterrows():
            # AI analysis
            ai_analysis = process_survey(row['response_text'])
            
            # Create enriched metadata with actual customer names
            metadata = {
                **row.to_dict(),
                'customer_name': row['company_name'],  # Use the actual company name
                **ai_analysis
            }
            
            # Store in advanced vector database
            vector_store.add_survey(
                text=row['response_text'],
                metadata=metadata
            )
            
            # Intelligent flagging (if available)
            if langgraph_flagger:
                survey_data = {
                    **row.to_dict(),
                    'customer_name': row['company_name']  # Use actual company name
                }
                
                try:
                    # Execute intelligent workflow
                    agent_decision = langgraph_flagger.analyze_and_flag(survey_data, ai_analysis)
                    
                    if agent_decision['should_flag']:
                        flagged_results.append({
                            **agent_decision,
                            'customer_name': row['company_name'],  # Actual company name
                            'customer_tier': row.get('tier', 'Unknown'),
                            'customer_mrr': row.get('mrr', 0),
                            'response_preview': row['response_text'][:150] + "...",
                            'original_score': row.get('score', 'N/A'),
                            'agent_enhanced': True
                        })
                except Exception as e:
                    print(f"⚠️ Flagging error for {row['company_name']}: {e}")
            else:
                # Simple fallback flagging logic when LangGraph is not available
                score = row.get('score', 5)
                sentiment = ai_analysis.get('sentiment', 'neutral')
                
                # Basic flagging rules
                should_flag = (score <= 3) or (sentiment == 'negative' and score <= 5)
                
                if should_flag:
                    flagged_results.append({
                        'should_flag': True,
                        'confidence': 0.7,
                        'priority': 'medium',
                        'flag_score': 10 - score if score <= 10 else 5,
                        'reasoning': f"Simple rule-based flagging: score={score}, sentiment={sentiment}",
                        'customer_name': row['company_name'],
                        'customer_tier': row.get('tier', 'Unknown'),
                        'customer_mrr': row.get('mrr', 0),
                        'response_preview': row['response_text'][:150] + "...",
                        'original_score': score,
                        'agent_enhanced': False,
                        'agent_type': 'simple_fallback'
                    })
            
            processed_count += 1
        
        agent_status = "langgraph_enhanced" if langgraph_flagger else "simple_fallback"
        
        return {
            "processed": processed_count,
            "flagged": len(flagged_results),
            "flags": flagged_results,
            "agent_status": agent_status,
            "agent_type": langgraph_flagger.agent_type if langgraph_flagger else "simple_fallback",
            "vector_count": vector_store.count(),
            "customer_data_enriched": True,
            "langgraph_available": langgraph_flagger is not None
        }
        
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        return {"error": str(e)}, 500

@app.get("/flags-advanced")
async def get_intelligent_flags(
    tier: str = Query(None, description="Customer tier filter"),
    days: int = Query(7, ge=1, le=365, description="Days to look back"),
    priority: str = Query(None, description="Priority filter (low/medium/high/critical)")
):
    """Get flags with intelligent agent reasoning (if available)"""
    if not langgraph_flagger:
        return {
            "error": "LangGraph flagging agent not available",
            "message": "Try: pip install 'langgraph>=0.2.20,<0.3'",
            "flags": [],
            "total": 0
        }
    
    flags = langgraph_flagger.get_advanced_flags(tier=tier, days=days, priority=priority)
    
    return {
        "flags": flags,
        "total": len(flags),
        "filters_applied": {
            "tier": tier,
            "days": days, 
            "priority": priority
        },
        "agent_enhanced": True,
        "agent_type": langgraph_flagger.agent_type
    }

@app.get("/search")
async def search_similar(
    query: str = Query(..., min_length=1),
    k: int = Query(5, ge=1, le=20)
):
    """Advanced semantic search with enhanced vector store"""
    results = vector_store.search_similar(query, k)
    return results

@app.get("/analyze")
async def analyze_with_rag(
    query: str = Query(..., min_length=1, description="Analysis question about survey data"),
    use_advanced: bool = Query(False, description="Use advanced retrieval with cross-encoder and web search")
):
    """RAG-powered analysis of survey data with optional advanced retrieval"""
    try:
        if use_advanced and ADVANCED_RETRIEVAL_AVAILABLE:
            # Use advanced retrieval pipeline
            retrieval_results = advanced_retrieval.hybrid_retrieval(query, k=5)
            context_docs = retrieval_results['documents']
            
            # Generate analysis with enhanced RAG
            analysis = rag_generator.generate_response(query, context_docs)
            
            return {
                "query": query,
                "analysis": analysis,
                "context_count": len(context_docs),
                "sources": [
                    doc.metadata.get('customer_name', 
                    doc.metadata.get('source', 'Unknown')) 
                    for doc in context_docs
                ],
                "rag_enhanced": True,
                "retrieval_method": "advanced",
                "retrieval_stats": retrieval_results['retrieval_stats'],
                "expanded_queries": retrieval_results.get('expanded_queries', [])
            }
        else:
            # Use basic retrieval
            context_docs = vector_store.get_context_for_query(query)
            
            # Generate analysis with basic RAG
            analysis = rag_generator.generate_response(query, context_docs)
            
            return {
                "query": query,
                "analysis": analysis,
                "context_count": len(context_docs),
                "sources": [
                    doc.metadata.get('customer_name', 
                    doc.metadata.get('company_name', 'Unknown')) 
                    for doc in context_docs
                ],
                "rag_enhanced": True,
                "retrieval_method": "basic"
            }
        
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/analyze-basic")
async def analyze_with_basic_rag(
    query: str = Query(..., min_length=1, description="Analysis question about survey data")
):
    """Basic RAG analysis (for comparison with advanced)"""
    return await analyze_with_rag(query=query, use_advanced=False)

@app.get("/analyze-advanced")
async def analyze_with_advanced_rag(
    query: str = Query(..., min_length=1, description="Analysis question about survey data")
):
    """Advanced RAG analysis with cross-encoder and web search"""
    if not ADVANCED_RETRIEVAL_AVAILABLE:
        return {
            "error": "Advanced retrieval not available",
            "message": "Install required packages: pip install transformers torch"
        }, 503
    
    return await analyze_with_rag(query=query, use_advanced=True)

@app.get("/compare-retrieval")
async def compare_retrieval_methods(
    query: str = Query(..., min_length=1, description="Query to compare retrieval methods"),
    k: int = Query(5, ge=1, le=20, description="Number of results to retrieve")
):
    """Compare basic vs advanced retrieval methods for the same query"""
    if not ADVANCED_RETRIEVAL_AVAILABLE:
        return {
            "error": "Advanced retrieval not available",
            "message": "Install required packages: pip install transformers torch"
        }, 503
    
    try:
        comparison = advanced_retrieval.compare_retrieval_methods(query, k)
        return comparison
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/system-health")
async def get_system_health():
    """Comprehensive system health check"""
    try:
        # Check vector store
        vector_count = vector_store.count()
        
        # Check flagging system
        recent_flags = []
        flagging_status = "disabled"
        if langgraph_flagger:
            try:
                recent_flags = langgraph_flagger.get_advanced_flags(days=7)
                flagging_status = "operational"
            except Exception as e:
                flagging_status = f"error: {e}"
        
        # Check advanced retrieval
        advanced_retrieval_status = "disabled"
        if ADVANCED_RETRIEVAL_AVAILABLE and advanced_retrieval:
            try:
                # Quick test
                test_result = advanced_retrieval.query_expansion("test", num_expansions=1)
                if test_result:
                    advanced_retrieval_status = "operational"
            except Exception as e:
                advanced_retrieval_status = f"error: {e}"
        
        # Check if data files are available
        customer_data_available = os.path.exists('data/customer_master.csv')
        alert_rules_available = os.path.exists('data/alert_rules.json')
        
        # Check if RapidAPI key is configured
        rapidapi_configured = bool(os.getenv("RAPIDAPI_KEY"))
        
        return {
            "system_status": "healthy",
            "components": {
                "vector_store": {
                    "status": "operational",
                    "stored_vectors": vector_count,
                    "embedding_model": "text-embedding-3-small"
                },
                "intelligent_flagging": {
                    "status": flagging_status,
                    "recent_flags": len(recent_flags),
                    "agent_model": "gpt-4o-mini",
                    "langgraph_available": langgraph_flagger is not None,
                    "agent_type": langgraph_flagger.agent_type if langgraph_flagger else "none"
                },
                "advanced_retrieval": {
                    "status": advanced_retrieval_status,
                    "cross_encoder_available": ADVANCED_RETRIEVAL_AVAILABLE,
                    "web_search_configured": rapidapi_configured,
                    "components": {
                        "query_expansion": "available" if ADVANCED_RETRIEVAL_AVAILABLE else "disabled",
                        "cross_encoder_reranking": "available" if ADVANCED_RETRIEVAL_AVAILABLE else "disabled",
                        "contextual_compression": "available" if ADVANCED_RETRIEVAL_AVAILABLE else "disabled",
                        "web_search": "configured" if rapidapi_configured else "mock_mode"
                    }
                },
                "data_sources": {
                    "customer_master": customer_data_available,
                    "alert_rules": alert_rules_available,
                    "survey_responses": os.path.exists('data/survey_responses.csv')
                },
                "rag_analysis": {
                    "status": "available",
                    "llm_model": "gpt-3.5-turbo",
                    "basic_rag": "available",
                    "advanced_rag": "available" if ADVANCED_RETRIEVAL_AVAILABLE else "disabled"
                },
                "ragas_evaluation": {
                    "status": "available" if ragas_evaluator else "disabled",
                    "evaluator_available": ragas_evaluator is not None
                }
            },
            "version": "0.7.0",
            "features": ["Advanced Vector Search", "RAG Analysis", "Advanced Retrieval"],
            "agent_features": f"LangGraph agents: {'enabled' if langgraph_flagger else 'disabled'}",
            "evaluation_features": f"RAGAS: {'enabled' if ragas_evaluator else 'disabled'}",
            "retrieval_features": f"Advanced Retrieval: {'enabled' if ADVANCED_RETRIEVAL_AVAILABLE else 'disabled'}"
        }
        
    except Exception as e:
        return {"system_status": "degraded", "error": str(e)}, 500

@app.get("/stats")
async def get_enhanced_stats():
    """Enhanced system statistics"""
    recent_flags_count = 0
    if langgraph_flagger:
        try:
            recent_flags_count = len(langgraph_flagger.get_advanced_flags(days=30))
        except:
            pass
    
    return {
        "total_vectors": vector_store.count(),
        "total_flags": recent_flags_count,
        "embedding_model": "text-embedding-3-small",
        "vector_database": "In-Memory Enhanced",
        "flagging_system": "Intelligent Agent-based" if langgraph_flagger else "Simple Rule-based",
        "retrieval_system": "Advanced (Cross-encoder + Web)" if ADVANCED_RETRIEVAL_AVAILABLE else "Basic",
        "langgraph_available": langgraph_flagger is not None,
        "ragas_available": ragas_evaluator is not None,
        "advanced_retrieval_available": ADVANCED_RETRIEVAL_AVAILABLE,
        "agent_type": langgraph_flagger.agent_type if langgraph_flagger else "none",
        "system_status": "advanced" if ADVANCED_RETRIEVAL_AVAILABLE else "enhanced" if langgraph_flagger else "basic"
    }

# Optional RAGAS endpoints (only if RAGAS is available)
if RAGASEvaluation and ragas_evaluator:
    @app.post("/run-evaluation")
    async def run_ragas_evaluation():
        """Run RAGAS evaluation (if available)"""
        try:
            print("🚀 Starting RAGAS evaluation...")
            results = ragas_evaluator.run_evaluation()
            
            return {
                "evaluation_completed": True,
                "timestamp": results.get('timestamp'),
                "total_questions": results.get('total_questions', 0),
                "successful_evaluations": results.get('successful_evaluations', 0),
                "aggregate_metrics": results.get('aggregate_metrics', {}),
                "ragas_available": True
            }
            
        except Exception as e:
            return {"error": str(e), "evaluation_completed": False}, 500

def main():
    """Main entry point for the Enhanced Survey Sentinel application"""
    import uvicorn
    
    print("🚀 Starting Survey Sentinel - Enhanced Agent System...")
    if langgraph_flagger:
        print(f"✅ LangGraph agent system: {langgraph_flagger.agent_type}")
    else:
        print("⚠️ LangGraph not available - using fallback systems")
        print("   To enable advanced features, run: pip install 'langgraph>=0.2.20,<0.3'")
    
    if ADVANCED_RETRIEVAL_AVAILABLE:
        print("✅ Advanced retrieval system available (cross-encoder + web search)")
    else:
        print("⚠️ Advanced retrieval not available")
        print("   To enable: pip install transformers torch sentence-transformers")
    
    if ragas_evaluator:
        print("✅ RAGAS evaluation system available")
    else:
        print("⚠️ RAGAS evaluation not available")
    
    # Check for RapidAPI key
    if os.getenv("RAPIDAPI_KEY"):
        print("✅ RapidAPI key configured for web search")
    else:
        print("⚠️ No RapidAPI key found - web search will use mock data")
        print("   Get your free key at: https://rapidapi.com/contextualweb/api/web-search")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()