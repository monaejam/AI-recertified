from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from typing import List, Dict
import os

class RAGGenerator:
    """RAG-powered response generator for survey insights with LangGraph awareness"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Enhanced RAG prompt template for LangGraph context
        self.chat_prompt = ChatPromptTemplate.from_template("""
        You are an expert customer success analyst with access to comprehensive survey data processed by advanced AI agents. 
        Based on the enriched survey context provided, answer the user's question with actionable insights.
        
        Context from survey responses (processed with LangGraph workflow analysis):
        {context}
        
        Question: {query}
        
        Provide a comprehensive analysis focusing on:
        - Specific customer concerns and actionable issues
        - Patterns across different customer tiers and segments  
        - Priority recommendations for the customer success team
        - Business impact assessment and risk factors
        - Immediate actions needed vs. long-term strategic improvements
        
        Use the rich metadata (customer tier, MRR, tenure, sentiment analysis) to provide nuanced insights.
        If the context doesn't contain relevant information, clearly state what data would be needed for a complete analysis.
        
        Format your response to be immediately actionable for customer success managers.
        """)
        
        # Create the enhanced chain
        self.generator_chain = self.chat_prompt | self.llm | StrOutputParser()
    
    def generate_response(self, query: str, context_docs: List[Document]) -> str:
        """Generate response using RAG pattern with LangGraph-enhanced context"""
        try:
            # Format context with comprehensive customer intelligence
            context_parts = []
            
            for doc in context_docs:
                # Extract comprehensive customer information
                customer_name = (
                    doc.metadata.get('customer_name') or 
                    doc.metadata.get('company_name') or
                    doc.metadata.get('customer_id') or
                    'Unknown Customer'
                )
                
                # Collect rich metadata for enhanced analysis
                score = doc.metadata.get('score', 'N/A')
                sentiment = doc.metadata.get('sentiment', 'Unknown')
                tier = doc.metadata.get('tier', 'Unknown')
                mrr = doc.metadata.get('mrr', 'Unknown')
                tenure = doc.metadata.get('tenure_months', 'Unknown')
                industry = doc.metadata.get('industry', 'Unknown')
                
                # Extract AI analysis results
                issues = doc.metadata.get('issues', [])
                features_mentioned = doc.metadata.get('features_mentioned', [])
                revenue_impact = doc.metadata.get('revenue_impact', False)
                competitors_mentioned = doc.metadata.get('competitors_mentioned', [])
                
                # Build comprehensive context entry
                context_part = f"""
CUSTOMER: {customer_name}
Business Profile: {tier} tier, ${mrr}/month MRR, {tenure} months tenure, {industry} industry
Survey Score: {score}/10 (Sentiment: {sentiment})
Issues Identified: {', '.join(issues) if issues else 'None specific'}
Features Mentioned: {', '.join(features_mentioned) if features_mentioned else 'None'}
Revenue Impact: {'Yes' if revenue_impact else 'No'}
Competitors Mentioned: {', '.join(competitors_mentioned) if competitors_mentioned else 'None'}
Response: {doc.page_content}
"""
                context_parts.append(context_part.strip())
            
            # Combine all context
            context = "\n\n" + "="*50 + "\n\n".join(context_parts)
            
            # Generate enhanced response
            response = self.generator_chain.invoke({
                "query": query,
                "context": context
            })
            
            return response
            
        except Exception as e:
            return f"Error generating response: {e}. Please ensure the LangGraph agent pipeline has processed survey data properly."
    
    def generate_executive_summary(self, context_docs: List[Document]) -> str:
        """Generate executive summary with LangGraph insights"""
        try:
            # Create executive summary prompt
            executive_prompt = ChatPromptTemplate.from_template("""
            Based on the comprehensive survey analysis below, create an executive summary for customer success leadership.
            
            Survey Data Analysis:
            {context}
            
            Provide a structured executive summary with:
            
            **KEY FINDINGS:**
            - Most critical customer issues requiring immediate attention
            - Customer satisfaction trends by tier/segment
            - Revenue at risk and expansion opportunities
            
            **IMMEDIATE ACTIONS REQUIRED:**
            - Top 3 priority actions for the next 30 days
            - Specific customers needing urgent outreach
            - Process/product improvements needed
            
            **STRATEGIC RECOMMENDATIONS:**
            - Long-term improvements to prevent recurring issues
            - Investment priorities for customer success initiatives
            - Data-driven insights for product development
            
            Keep the summary concise but actionable, focusing on business impact and ROI.
            """)
            
            # Format context for executive view
            context_parts = []
            high_risk_customers = []
            expansion_opportunities = []
            
            for doc in context_docs:
                customer_name = doc.metadata.get('customer_name', 'Unknown')
                tier = doc.metadata.get('tier', 'Unknown')
                mrr = doc.metadata.get('mrr', 0)
                sentiment = doc.metadata.get('sentiment', 'neutral')
                score = doc.metadata.get('score', 5)
                
                # Categorize customers
                if sentiment == 'negative' or score <= 3:
                    high_risk_customers.append(f"{customer_name} ({tier}, ${mrr}/mo)")
                elif sentiment == 'positive' and score >= 8 and tier in ['Professional', 'Enterprise']:
                    expansion_opportunities.append(f"{customer_name} ({tier}, ${mrr}/mo)")
                
                context_parts.append(f"{customer_name}: {sentiment} sentiment, {score}/10 score, {tier} tier")
            
            context_summary = "\n".join(context_parts)
            context_summary += f"\n\nHigh Risk Customers: {'; '.join(high_risk_customers[:5])}"
            context_summary += f"\nExpansion Opportunities: {'; '.join(expansion_opportunities[:5])}"
            
            # Generate executive summary
            exec_chain = executive_prompt | self.llm | StrOutputParser()
            summary = exec_chain.invoke({"context": context_summary})
            
            return summary
            
        except Exception as e:
            return f"Error generating executive summary: {e}"
    
    def analyze_customer_health_trends(self, context_docs: List[Document]) -> Dict:
        """Analyze customer health trends from LangGraph-processed data"""
        try:
            # Initialize metrics
            tier_metrics = {}
            sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}
            total_mrr_risk = 0
            total_customers = len(context_docs)
            
            for doc in context_docs:
                tier = doc.metadata.get('tier', 'Unknown')
                sentiment = doc.metadata.get('sentiment', 'neutral')
                mrr = doc.metadata.get('mrr', 0)
                score = doc.metadata.get('score', 5)
                
                # Track tier metrics
                if tier not in tier_metrics:
                    tier_metrics[tier] = {"count": 0, "avg_score": 0, "total_mrr": 0, "at_risk": 0}
                
                tier_metrics[tier]["count"] += 1
                tier_metrics[tier]["avg_score"] += score
                tier_metrics[tier]["total_mrr"] += mrr
                
                # Count sentiment
                if sentiment in sentiment_distribution:
                    sentiment_distribution[sentiment] += 1
                
                # Calculate risk
                if sentiment == 'negative' or score <= 3:
                    tier_metrics[tier]["at_risk"] += 1
                    total_mrr_risk += mrr
            
            # Calculate averages
            for tier in tier_metrics:
                if tier_metrics[tier]["count"] > 0:
                    tier_metrics[tier]["avg_score"] /= tier_metrics[tier]["count"]
                    tier_metrics[tier]["risk_percentage"] = (tier_metrics[tier]["at_risk"] / tier_metrics[tier]["count"]) * 100
            
            # Overall health score (0-100)
            positive_ratio = sentiment_distribution["positive"] / total_customers if total_customers > 0 else 0
            negative_ratio = sentiment_distribution["negative"] / total_customers if total_customers > 0 else 0
            overall_health_score = (positive_ratio * 100) - (negative_ratio * 50)
            
            return {
                "overall_health_score": round(max(0, min(100, overall_health_score)), 1),
                "total_customers_analyzed": total_customers,
                "sentiment_distribution": sentiment_distribution,
                "tier_breakdown": tier_metrics,
                "total_mrr_at_risk": total_mrr_risk,
                "risk_percentage": round((sentiment_distribution["negative"] / total_customers) * 100, 1) if total_customers > 0 else 0,
                "analysis_powered_by": "langgraph_enhanced_rag"
            }
            
        except Exception as e:
            return {"error": f"Health trend analysis failed: {e}"}