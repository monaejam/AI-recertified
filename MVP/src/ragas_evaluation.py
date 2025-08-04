#!/usr/bin/env python3
"""
Enhanced RAGAS evaluation that compares basic vs advanced retrieval
"""

import requests
import pandas as pd
import json
import os
from typing import List, Dict
from datetime import datetime

class WorkingRAGASEvaluation:
    """Working RAGAS evaluation using your Survey Sentinel API"""
    
    def __init__(self, api_base="http://localhost:8000"):
        self.api_base = api_base
        
    def create_evaluation_dataset(self) -> List[Dict]:
        """Create evaluation questions with expected answers"""
        return [
            {
                "question": "What are the main customer complaints?",
                "context_type": "negative_feedback",
                "expected_elements": ["portal", "billing", "performance", "slow", "crashes"],
                "min_context_expected": 3
            },
            {
                "question": "Which customers seem most unhappy based on their scores?",
                "context_type": "low_scores", 
                "expected_elements": ["customer", "score", "unhappy", "dissatisfied"],
                "min_context_expected": 2
            },
            {
                "question": "Are there any urgent technical issues that need immediate attention?",
                "context_type": "urgent_issues",
                "expected_elements": ["portal", "down", "crash", "error", "broken"],
                "min_context_expected": 1
            },
            {
                "question": "What positive feedback patterns do you see?",
                "context_type": "positive_feedback",
                "expected_elements": ["happy", "great", "excellent", "good", "satisfied"],
                "min_context_expected": 2
            },
            {
                "question": "What billing-related issues are customers reporting?",
                "context_type": "billing_issues",
                "expected_elements": ["billing", "invoice", "payment", "charge", "cost"],
                "min_context_expected": 1
            },
            {
                "question": "Which Enterprise customers have raised concerns?",
                "context_type": "enterprise_issues",
                "expected_elements": ["enterprise", "ENT", "customer", "concern"],
                "min_context_expected": 1
            },
            {
                "question": "What portal-related problems are mentioned?",
                "context_type": "portal_issues", 
                "expected_elements": ["portal", "slow", "search", "broken", "error"],
                "min_context_expected": 2
            },
            {
                "question": "Are there any mentions of competitors or switching?",
                "context_type": "churn_risk",
                "expected_elements": ["competitor", "switch", "alternative", "considering"],
                "min_context_expected": 1
            }
        ]
    
    def evaluate_single_response(self, question: str, response_data: Dict, expected: Dict) -> Dict:
        """Evaluate a single question-response pair using RAGAS-style metrics"""
        
        response_text = response_data.get("analysis", "")
        context_count = response_data.get("context_count", 0)
        sources = response_data.get("sources", [])
        retrieval_method = response_data.get("retrieval_method", "unknown")
        
        # FAITHFULNESS: Is the response grounded in retrieved context?
        if context_count == 0:
            faithfulness = 0.0
        elif "no specific information" in response_text.lower() or "no data" in response_text.lower():
            faithfulness = 0.2
        elif any(word in response_text.lower() for word in ["based on", "survey", "feedback", "customer"]):
            faithfulness = 0.9
        else:
            faithfulness = 0.6
            
        # ANSWER RELEVANCY: Does the response directly answer the question?
        question_words = set(question.lower().split())
        response_words = set(response_text.lower().split())
        overlap = len(question_words.intersection(response_words))
        
        if len(response_text) < 50:
            answer_relevancy = 0.3
        elif overlap >= 2 and len(response_text) > 100:
            answer_relevancy = 0.9
        elif overlap >= 1:
            answer_relevancy = 0.7
        else:
            answer_relevancy = 0.4
            
        # CONTEXT PRECISION: How relevant is the retrieved context?
        expected_context = expected["min_context_expected"]
        if context_count >= expected_context:
            context_precision = min(1.0, context_count / (expected_context + 2))
        else:
            context_precision = context_count / expected_context if expected_context > 0 else 0
            
        # CONTEXT RECALL: Did we retrieve enough relevant context?
        max_expected_context = 5  # Reasonable maximum
        context_recall = min(1.0, context_count / max_expected_context) if context_count > 0 else 0.0
        
        # Check if expected elements are present in response
        expected_elements = expected.get("expected_elements", [])
        elements_found = sum(1 for elem in expected_elements if elem.lower() in response_text.lower())
        element_coverage = elements_found / len(expected_elements) if expected_elements else 1.0
        
        # Adjust scores based on element coverage
        if element_coverage > 0.5:
            answer_relevancy *= 1.2
            faithfulness *= 1.1
        
        # Bonus for external sources in advanced retrieval
        if retrieval_method == "advanced" and response_data.get("retrieval_stats", {}).get("external_sources", 0) > 0:
            context_precision *= 1.1
        
        # Cap at 1.0
        answer_relevancy = min(1.0, answer_relevancy)
        faithfulness = min(1.0, faithfulness)
        context_precision = min(1.0, context_precision)
        context_recall = min(1.0, context_recall)
        
        return {
            "question": question,
            "response_length": len(response_text),
            "context_count": context_count,
            "sources_count": len(sources),
            "faithfulness": round(faithfulness, 3),
            "answer_relevancy": round(answer_relevancy, 3),
            "context_precision": round(context_precision, 3), 
            "context_recall": round(context_recall, 3),
            "element_coverage": round(element_coverage, 3),
            "retrieval_method": retrieval_method,
            "response_preview": response_text[:150] + "..." if len(response_text) > 150 else response_text
        }
    
    def run_evaluation(self, test_advanced=True) -> Dict:
        """Run comprehensive RAGAS evaluation, optionally comparing basic vs advanced"""
        
        print("🚀 Running RAGAS-style evaluation on Survey Sentinel...")
        
        # Check API availability
        try:
            health_response = requests.get(f"{self.api_base}/system-health", timeout=10)
            if health_response.status_code != 200:
                return {"error": "API not available", "status_code": health_response.status_code}
            
            health_data = health_response.json()
            advanced_available = health_data.get("components", {}).get("advanced_retrieval", {}).get("status") == "operational"
            
            if test_advanced and not advanced_available:
                print("⚠️ Advanced retrieval not available, falling back to basic only")
                test_advanced = False
                
        except Exception as e:
            return {"error": f"Cannot connect to API: {e}"}
        
        test_cases = self.create_evaluation_dataset()
        basic_results = []
        advanced_results = []
        
        print(f"📝 Testing {len(test_cases)} evaluation questions...")
        
        # Test basic retrieval
        print("\n🔵 Testing BASIC retrieval...")
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing: '{test_case['question']}'")
            
            try:
                # Call the basic analyze endpoint
                response = requests.get(
                    f"{self.api_base}/analyze-basic",
                    params={"query": test_case["question"]},
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Evaluate this response
                    evaluation = self.evaluate_single_response(
                        test_case["question"],
                        response_data,
                        test_case
                    )
                    
                    basic_results.append(evaluation)
                    
                    print(f"   ✅ Basic - Context: {evaluation['context_count']}, "
                          f"Faithfulness: {evaluation['faithfulness']:.2f}, "
                          f"Relevancy: {evaluation['answer_relevancy']:.2f}")
                    
                else:
                    print(f"   ❌ API error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Test advanced retrieval if available
        if test_advanced:
            print("\n🟢 Testing ADVANCED retrieval...")
            for i, test_case in enumerate(test_cases, 1):
                print(f"\n{i}. Testing: '{test_case['question']}'")
                
                try:
                    # Call the advanced analyze endpoint
                    response = requests.get(
                        f"{self.api_base}/analyze-advanced",
                        params={"query": test_case["question"]},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        
                        # Evaluate this response
                        evaluation = self.evaluate_single_response(
                            test_case["question"],
                            response_data,
                            test_case
                        )
                        
                        advanced_results.append(evaluation)
                        
                        print(f"   ✅ Advanced - Context: {evaluation['context_count']}, "
                              f"Faithfulness: {evaluation['faithfulness']:.2f}, "
                              f"Relevancy: {evaluation['answer_relevancy']:.2f}")
                        
                        # Show extra stats if available
                        if "retrieval_stats" in response_data:
                            stats = response_data["retrieval_stats"]
                            print(f"      📊 Internal: {stats.get('internal_sources', 0)}, "
                                  f"External: {stats.get('external_sources', 0)}, "
                                  f"Total candidates: {stats.get('total_candidates', 0)}")
                        
                    else:
                        print(f"   ❌ API error: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Error: {e}")
        
        # Calculate aggregate metrics
        def calculate_aggregates(results):
            if not results:
                return {"error": "No successful evaluations"}
                
            metrics = {
                "faithfulness": sum(r["faithfulness"] for r in results) / len(results),
                "answer_relevancy": sum(r["answer_relevancy"] for r in results) / len(results),
                "context_precision": sum(r["context_precision"] for r in results) / len(results),
                "context_recall": sum(r["context_recall"] for r in results) / len(results),
                "average_context_count": sum(r["context_count"] for r in results) / len(results),
                "element_coverage": sum(r["element_coverage"] for r in results) / len(results)
            }
            
            # Overall RAG score
            metrics["overall_rag_score"] = (
                metrics["faithfulness"] + 
                metrics["answer_relevancy"] + 
                metrics["context_precision"] + 
                metrics["context_recall"]
            ) / 4
            
            return metrics
        
        basic_metrics = calculate_aggregates(basic_results)
        advanced_metrics = calculate_aggregates(advanced_results) if advanced_results else None
        
        evaluation_results = {
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(test_cases),
            "basic_evaluation": {
                "successful_evaluations": len(basic_results),
                "individual_results": basic_results,
                "aggregate_metrics": {k: round(v, 3) if isinstance(v, float) else v 
                                    for k, v in basic_metrics.items()}
            }
        }
        
        if advanced_results:
            evaluation_results["advanced_evaluation"] = {
                "successful_evaluations": len(advanced_results),
                "individual_results": advanced_results,
                "aggregate_metrics": {k: round(v, 3) if isinstance(v, float) else v 
                                    for k, v in advanced_metrics.items()}
            }
            
            # Calculate improvements
            if "error" not in basic_metrics and "error" not in advanced_metrics:
                improvements = {}
                for metric in basic_metrics:
                    if isinstance(basic_metrics[metric], (int, float)) and basic_metrics[metric] > 0:
                        improvement = ((advanced_metrics[metric] - basic_metrics[metric]) / basic_metrics[metric]) * 100
                        improvements[metric] = round(improvement, 1)
                
                evaluation_results["improvements"] = improvements
        
        evaluation_results["evaluation_method"] = "Custom RAGAS-style evaluation with comparison"
        
        return evaluation_results
    
    def print_results(self, results: Dict):
        """Print formatted evaluation results with comparison"""
        
        print("\n" + "="*70)
        print("📊 SURVEY SENTINEL - RAGAS EVALUATION RESULTS")
        print("="*70)
        
        # Basic results
        if "basic_evaluation" in results:
            basic_metrics = results["basic_evaluation"]["aggregate_metrics"]
            
            if "error" not in basic_metrics:
                print(f"\n🔵 BASIC RETRIEVAL METRICS:")
                print(f"{'Metric':<20} {'Score':<8} {'Interpretation'}")
                print("-" * 50)
                for metric, value in basic_metrics.items():
                    if metric != "overall_rag_score" and isinstance(value, (int, float)):
                        interpretation = 'High' if value > 0.7 else 'Medium' if value > 0.5 else 'Low'
                        print(f"{metric:<20} {value:<8.3f} {interpretation}")
                
                print(f"\n{'Overall RAG Score':<20} {basic_metrics.get('overall_rag_score', 0):<8.3f}")
        
        # Advanced results
        if "advanced_evaluation" in results:
            advanced_metrics = results["advanced_evaluation"]["aggregate_metrics"]
            
            if "error" not in advanced_metrics:
                print(f"\n🟢 ADVANCED RETRIEVAL METRICS:")
                print(f"{'Metric':<20} {'Score':<8} {'Interpretation'}")
                print("-" * 50)
                for metric, value in advanced_metrics.items():
                    if metric != "overall_rag_score" and isinstance(value, (int, float)):
                        interpretation = 'High' if value > 0.7 else 'Medium' if value > 0.5 else 'Low'
                        print(f"{metric:<20} {value:<8.3f} {interpretation}")
                
                print(f"\n{'Overall RAG Score':<20} {advanced_metrics.get('overall_rag_score', 0):<8.3f}")
        
        # Comparison
        if "improvements" in results:
            print(f"\n📈 IMPROVEMENTS (Advanced vs Basic):")
            print(f"{'Metric':<25} {'Improvement':<15} {'Impact'}")
            print("-" * 60)
            
            for metric, improvement in results["improvements"].items():
                impact = "🟢 Significant" if improvement > 10 else "🟡 Moderate" if improvement > 5 else "🔴 Minimal"
                print(f"{metric:<25} {improvement:>6.1f}% {impact}")
        
        # Summary
        print(f"\n📈 PERFORMANCE SUMMARY:")
        print(f"Total Questions Tested: {results['total_questions']}")
        
        if "basic_evaluation" in results:
            print(f"Basic Retrieval - Successful: {results['basic_evaluation']['successful_evaluations']}")
            
        if "advanced_evaluation" in results:
            print(f"Advanced Retrieval - Successful: {results['advanced_evaluation']['successful_evaluations']}")
            
            # Overall interpretation
            if "improvements" in results:
                avg_improvement = sum(results["improvements"].values()) / len(results["improvements"])
                
                if avg_improvement > 15:
                    print(f"\n🎉 EXCELLENT: Advanced retrieval shows significant improvements ({avg_improvement:.1f}% average)!")
                elif avg_improvement > 5:
                    print(f"\n✅ GOOD: Advanced retrieval provides meaningful improvements ({avg_improvement:.1f}% average).")
                else:
                    print(f"\n🟡 MARGINAL: Advanced retrieval shows modest improvements ({avg_improvement:.1f}% average).")
        
        print("\n" + "="*70)

def main():
    """Run RAGAS evaluation and save results"""
    
    evaluator = WorkingRAGASEvaluation()
    
    print("🔍 Starting RAGAS evaluation of Survey Sentinel...")
    print("   This will compare basic retrieval vs advanced retrieval (if available)")
    
    results = evaluator.run_evaluation(test_advanced=True)
    
    # Print results
    evaluator.print_results(results)
    
    # Save results to file
    output_file = "ragas_comparison_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    # Return results for programmatic use
    return results

if __name__ == "__main__":
    main()