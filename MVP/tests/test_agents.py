import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from flagging_agent_advanced import SmartFlaggingAgent, FlaggingTools
from llm_processor import process_survey

@pytest.fixture
def sample_survey_data():
    return {
        'survey_id': 'TEST_001',
        'customer_id': 'CUST_001',
        'customer_name': 'Test Corp',
        'response_text': 'Portal is extremely slow and costing us revenue',
        'score': 2,
        'question_code': 'Portal_Experience'
    }

@pytest.fixture
def sample_ai_analysis():
    return {
        'sentiment': 'negative',
        'features_mentioned': ['portal'],
        'issues': ['performance'],
        'competitors_mentioned': [],
        'revenue_impact': True
    }

def test_flagging_tools_initialization():
    """Test that flagging tools initialize properly"""
    tools = FlaggingTools('./test_survey_sentinel.db')
    assert tools is not None
    assert hasattr(tools, 'check_customer_history')
    assert hasattr(tools, 'analyze_similar_patterns')

def test_customer_history_check(sample_survey_data):
    """Test customer history analysis"""
    tools = FlaggingTools('./test_survey_sentinel.db')
    result = tools.check_customer_history(sample_survey_data['customer_id'])
    assert isinstance(result, str)
    assert len(result) > 0

def test_business_impact_evaluation(sample_survey_data, sample_ai_analysis):
    """Test business impact assessment"""
    tools = FlaggingTools('./test_survey_sentinel.db')
    result = tools.evaluate_business_impact(
        sample_survey_data['customer_id'], 
        sample_ai_analysis
    )
    assert isinstance(result, str)
    assert 'Business Impact' in result

@pytest.mark.slow
def test_smart_flagging_agent_decision(sample_survey_data, sample_ai_analysis):
    """Test full agent decision making"""
    agent = SmartFlaggingAgent('./test_survey_sentinel.db')
    
    decision = agent.analyze_and_flag(sample_survey_data, sample_ai_analysis)
    
    # Check decision structure
    assert 'should_flag' in decision
    assert 'confidence' in decision
    assert 'priority' in decision
    assert 'reasoning' in decision
    assert isinstance(decision['should_flag'], bool)
    assert 0 <= decision['confidence'] <= 1

def test_escalation_triggers(sample_ai_analysis):
    """Test escalation rule checking"""
    tools = FlaggingTools('./test_survey_sentinel.db')
    result = tools.check_escalation_triggers(sample_ai_analysis, 'Enterprise')
    assert isinstance(result, str)

@pytest.mark.integration
def test_agent_with_real_survey():
    """Integration test with real survey processing"""
    # Test with a real survey response
    survey_text = "The billing system crashed during our month-end process. We lost 4 hours of work and couldn't generate invoices. This cost us approximately $15,000 in delayed payments."
    
    # Process with LLM first
    ai_analysis = process_survey(survey_text)
    
    # Then with agent
    survey_data = {
        'survey_id': 'INT_001',
        'customer_id': 'CUST_001', 
        'customer_name': 'Integration Test Corp',
        'response_text': survey_text,
        'score': 2,
        'question_code': 'BILL_Feedback_general'
    }
    
    agent = SmartFlaggingAgent('./test_survey_sentinel.db')
    decision = agent.analyze_and_flag(survey_data, ai_analysis)
    
    # Should flag due to revenue impact
    assert decision['should_flag'] == True
    assert decision['priority'] in ['high', 'critical']