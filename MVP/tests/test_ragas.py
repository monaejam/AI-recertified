import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from evaluation_ragas import RAGASEvaluation

@pytest.fixture
def sample_survey_data():
    """Create sample survey data for testing"""
    return pd.DataFrame({
        'survey_id': ['S001', 'S002', 'S003'],
        'customer_id': ['C001', 'C002', 'C003'],
        'customer_name': ['Test Corp A', 'Test Corp B', 'Test Corp C'],
        'response_text': [
            'Portal is very slow and affecting productivity',
            'Great improvements to the API, much faster now',
            'Billing system crashed, lost revenue'
        ],
        'score': [3, 8, 2],
        'question_code': ['Portal_Experience', 'P_Feedback_general', 'BILL_Feedback_general']
    })

def test_ragas_evaluator_initialization():
    """Test RAGAS evaluator initializes properly"""
    evaluator = RAGASEvaluation()
    assert evaluator is not None
    assert hasattr(evaluator, 'generator_llm')
    assert hasattr(evaluator, 'embeddings')
    assert hasattr(evaluator, 'generator')

@pytest.mark.slow
def test_synthetic_data_generation(sample_survey_data):
    """Test synthetic data generation with RAGAS"""
    evaluator = RAGASEvaluation()
    
    # Generate small test set
    synthetic_cases = evaluator.generate_synthetic_dataset(sample_survey_data, size=5)
    
    assert len(synthetic_cases) > 0
    assert len(synthetic_cases) <= 5
    
    # Check structure of generated cases
    for case in synthetic_cases:
        assert 'id' in case
        assert 'response_text' in case
        assert 'customer_name' in case
        assert 'synthetic' in case
        assert case['synthetic'] == True

def test_fallback_synthetic_generation():
    """Test fallback data generation when RAGAS fails"""
    evaluator = RAGASEvaluation()
    
    synthetic_cases = evaluator._generate_fallback_dataset(10)
    
    assert len(synthetic_cases) == 10
    for case in synthetic_cases:
        assert 'id' in case
        assert 'response_text' in case
        assert 'should_flag' in case

@pytest.mark.integration  
def test_flagging_accuracy_evaluation(sample_survey_data):
    """Test flagging accuracy measurement"""
    evaluator = RAGASEvaluation()
    
    # Generate test cases
    synthetic_cases = evaluator._generate_fallback_dataset(5)
    
    # Evaluate flagging
    results = evaluator.evaluate_flagging_accuracy(synthetic_cases)
    
    assert 'total_cases' in results
    assert 'accuracy' in results
    assert 'average_confidence' in results
    assert 0 <= results['accuracy'] <= 1