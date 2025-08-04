import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from llm_processor import process_survey
from flagging_agent_advanced import SmartFlaggingAgent
from vector_store import AdvancedVectorStore

def test_full_pipeline_integration():
    """Test complete pipeline: LLM → Agent → Vector Store"""
    survey_text = "Portal performance is terrible, customers are complaining"
    
    # Step 1: LLM Processing
    ai_analysis = process_survey(survey_text)
    assert 'sentiment' in ai_analysis
    
    # Step 2: Agent Flagging
    survey_data = {
        'survey_id': 'PIPE_001',
        'customer_id': 'CUST_PIPE',
        'customer_name': 'Pipeline Test Corp',
        'response_text': survey_text,
        'score': 3,
        'question_code': 'Portal_Experience'
    }
    
    agent = SmartFlaggingAgent('./test_pipeline.db')
    decision = agent.analyze_and_flag(survey_data, ai_analysis)
    assert 'should_flag' in decision
    
    # Step 3: Vector Storage
    vector_store = AdvancedVectorStore()
    vector_store.add_survey(survey_text, {**survey_data, **ai_analysis})
    
    # Step 4: Search
    search_results = vector_store.search_similar("portal issues", k=1)
    assert len(search_results['documents']) > 0