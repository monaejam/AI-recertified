from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Analysis prompt
analysis_prompt = PromptTemplate.from_template("""
Analyze this customer survey response and extract the following information:

1. Sentiment: positive, negative, or neutral
2. Features mentioned (select from: portal, billing, API, authentication, service_delivery)
3. Issues reported (performance, outage, usability, integration, security, other)
4. Competitors mentioned (if any)
5. Revenue impact mentioned (true/false)

Survey Response: "{text}"

Return ONLY valid JSON in this exact format:
{{
    "sentiment": "positive|negative|neutral",
    "features_mentioned": ["feature1", "feature2"],
    "issues": ["issue1", "issue2"],
    "competitors_mentioned": ["competitor1"],
    "revenue_impact": true/false
}}
""")

def process_survey(text: str) -> dict:
    """Process survey text with LLM and extract structured data"""
    try:
        chain = analysis_prompt | llm
        result = chain.invoke({"text": text})
        
        # Parse JSON response
        parsed = json.loads(result.content)
        
        # Ensure all required fields exist
        return {
            "sentiment": parsed.get("sentiment", "neutral"),
            "features_mentioned": parsed.get("features_mentioned", []),
            "issues": parsed.get("issues", []),
            "competitors_mentioned": parsed.get("competitors_mentioned", []),
            "revenue_impact": parsed.get("revenue_impact", False)
        }
    
    except Exception as e:
        print(f"LLM processing error: {e}")
        return {
            "sentiment": "neutral",
            "features_mentioned": [],
            "issues": [],
            "competitors_mentioned": [],
            "revenue_impact": False
        }

def generate_summary(responses: list) -> str:
    """Generate executive summary of multiple responses"""
    summary_prompt = PromptTemplate.from_template("""
    Create a brief executive summary of these survey responses:
    
    {responses}
    
    Focus on:
    - Key themes and patterns
    - Critical issues requiring attention
    - Overall sentiment trends
    
    Keep it under 200 words.
    """)
    
    chain = summary_prompt | llm
    result = chain.invoke({"responses": str(responses)})
    return result.content

