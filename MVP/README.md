📝 **Task 1:**
✅ Defining your Problem and Audience

Customer Success teams struggle to efficiently identify and prioritize critical customer feedback from thousands of survey responses, risking missed revenue-impacting issues and customer churn.

✅ Why This Is a Problem
Customer Success teams at B2B SaaS companies already use Qualtrics or similar platforms to collect and tally NPS and satisfaction scores, but those tools stop at basic dashboards and keyword tags. They don’t automatically triage free-text feedback based on customer tier, MRR, or historical health, nor do they draw cross-customer pattern insights in real time. As a result, even though CSMs aren’t reading every comment manually, they still miss emerging “whispers” of churn risk buried in thousands of open-ended responses—and urgent issues from high-value accounts can slip through until it’s too late.

📝 **Task 2:**
✅ Articulate your proposed solution
Survey Sentinel transforms the CSM workflow by providing an AI-powered intelligent triage system that automatically analyzes every survey response in real-time. When survey data is uploaded, AI agents immediately process each response, extracting sentiment, identifying mentioned features, detecting business impact indicators, and cross-referencing against customer history and business value. The system then intelligently flags responses that need attention, providing priority levels
The system feels like having a team of analysts working 24/7, surfacing critical issues before they escalate and providing CSMs with exactly what they need to know, when they need to know it.
The experience is conversational and intuitive - CSMs can ask natural language questions like "Which Enterprise customers have raised concerns?" or "What billing issues are customers reporting?" and receive comprehensive, actionable answers backed by specific customer data. 


✅ Deliverables
Tools in the stack:
1.	LLM: 
GPT-4-mini(For intelligent flagging decisions) and GPT-3.5-turbo(For analyzing survey responses,For RAG response generation) - Chosen for their balance of performance, cost-effectiveness, and strong instruction-following capabilities for both analysis and conversation.
2.	Embedding Model:
 OpenAI text-embedding-3-small - Selected for its superior performance in semantic similarity matching and compact vector size for efficient storage.
3.	Orchestration:
 LangChain + LangGraph - LangChain provides robust abstractions for LLM interactions while LangGraph enables sophisticated multi-step agent workflows with state management.
4.	Vector Database:
 In-memory store with persistence to SQLite - Chosen for simplicity and speed in proof-of-concept while maintaining upgrade path to Qdrant/Chroma.
5.	Monitoring:
 Custom logging with structured metrics tracking - Provides visibility into agent decisions, API performance, and system health without external dependencies.
6.	Evaluation:
 RAGAS framework - Industry-standard framework for evaluating RAG performance with metrics like faithfulness, relevancy, and context precision.
7.	User Interface:
 FastAPI backend with HTML/JavaScript frontend - FastAPI for high-performance async API operations and vanilla JS for zero-dependency, responsive UI.
8.	Serving & Inference: 
Uvicorn ASGI server - Production-grade async server that handles concurrent requests efficiently.
Agent usage:
The system uses LangGraph agents in the flagging_agent.py for intelligent survey response prioritization. The agent performs multi-step reasoning:
1.	Checks customer history for patterns
2.	Analyzes similar issues across the customer base
3.	Evaluates business impact based on MRR and tier
4.	Checks against escalation rules
5.	Makes final flagging decision with confidence scores
This agentic reasoning ensures that flagging decisions consider full business context, not just sentiment analysis.

📝 **Task 3: Dealing with the Data(Faker library)**

✅Deliverables
1.	Survey Responses CSV (survey_responses.csv) - Primary data containing customer feedback with scores and text responses, used for sentiment analysis and issue identification.
2.	Customer Master Data (customer_master.csv) - Enrichment data providing business context (MRR, tier, tenure) for prioritization decisions.
3.	Alert Rules JSON (alert_rules.json) - Business logic for escalation triggers based on customer tier, MRR thresholds, and issue types.
4.	Product Features Ontology (product_features.md) - Domain knowledge for accurate feature extraction and issue categorization from unstructured text.
5.	Question Codes Mapping (question_codes.json) - Maps survey question codes to full questions and categories for better context.
External APIs planned:
•	Web search API (for competitive intelligence when competitors are mentioned)
•	Slack/Email APIs (for escalation notifications)
•	CRM integration (future - for full customer context)

✅Chunking strategy:
The system uses RecursiveCharacterTextSplitter with:
•	Chunk size: 750 tokens
•	Overlap: 100 tokens
•	Length function: tiktoken for accurate GPT-4 token counting
This strategy is optimal for survey responses because:
•	Most responses are under 750 tokens (no unnecessary splitting)
•	100-token overlap preserves context across boundaries
•	Tiktoken ensures accurate token limits for LLM processing
Additional data needs:
•	Historical resolution data to train on what actions successfully retained customers
•	Competitor feature comparisons for competitive intelligence responses
•	Product roadmap data to address feature requests

📝 **Task 4: The app**

✅main.py - The Central API Server
This is the FastAPI application that serves as the main entry point. It orchestrates all the components and provides REST endpoints for:

Survey ingestion (/ingest) - Processes uploaded CSV files of survey responses, enriches them with customer data, runs AI analysis, and triggers intelligent flagging
Search capabilities (/search) - Semantic search through stored surveys
RAG analysis (/analyze) - Both basic and advanced retrieval-augmented generation for answering questions about survey data
Flag management (/flags-advanced) - Retrieves flagged surveys with intelligent agent reasoning
System health monitoring (/system-health, /stats) - Checks status of all components

✅vector_store.py - Document Storage & Retrieval
An in-memory vector database that:

Stores survey responses as embeddings using OpenAI's text-embedding-3-small model
Implements smart text chunking for longer documents
Provides similarity search using cosine similarity between embeddings
Falls back to keyword search if embeddings fail
Maintains a cache of embeddings for performance

✅llm_processor.py - AI Analysis Engine
Processes individual survey responses using GPT-3.5-turbo to extract:

Sentiment (positive/negative/neutral)
Features mentioned (portal, billing, API, etc.)
Issues reported (performance, outage, usability, etc.)
Competitor mentions
Revenue impact indicators
Returns structured JSON data for downstream processing

✅flagging_agent.py - Intelligent Alert System
Makes intelligent flagging decisions based on comprehensive context
Stores detailed flag data including priority, recommended actions, and escalation paths
Falls back to sequential processing if LangGraph isn't available
Considers factors like customer tier, MRR, tenure, and historical patterns

✅rag_generator.py - Response Generation
Generates comprehensive analyses using RAG (Retrieval-Augmented Generation):

Creates detailed responses to questions about survey data
Incorporates customer context (tier, MRR, sentiment) into responses
Generates executive summaries highlighting key findings and action items
Analyzes customer health trends across the customer base
Formats responses for customer success managers to take immediate action

✅advanced_retrieval.py - Enhanced Search System
Implements advanced retrieval techniques including:

Cross-encoder re-ranking - Uses a neural model to re-rank initial search results for better relevance
Query expansion - Generates alternative search queries using LLM
Hybrid retrieval - Combines internal vector store results with external web search
Contextual compression - Extracts only the most relevant portions of documents

✅web_search_api.py - External Context Integration
Integrates with RapidAPI's ContextualWeb to:

Search for relevant industry news and trends
Find competitor information from recent articles

✅ragas_evaluation.py - Quality Assessment
Implements RAGAS (Retrieval Augmented Generation Assessment) evaluation:

Tests the RAG system with predefined questions
Measures metrics like faithfulness, answer relevancy, context precision, and context recall
Compares basic vs advanced retrieval performance

✅models.py - Database Schema
Defines SQLAlchemy models for structured data storage:

SurveyResponse - Stores survey data with all extracted metadata
Flag - Stores flagging decisions and reasons
Provides database initialization functions

📝 **Task 5 SDG:**


📊 SURVEY SENTINEL - RAGAS EVALUATION RESULTS
======================================================================

🔵 BASIC RETRIEVAL METRICS:
Metric               Score    Interpretation
--------------------------------------------------
faithfulness         0.945    High
answer_relevancy     0.950    High
context_precision    1.000    High
context_recall       1.000    High
average_context_count 5.000    High
element_coverage     0.387    Low

Overall RAG Score    0.974   

🟢 ADVANCED RETRIEVAL METRICS:
Metric               Score    Interpretation
--------------------------------------------------
faithfulness         0.922    High
answer_relevancy     0.925    High
context_precision    1.000    High
context_recall       1.000    High
average_context_count 5.000    High
element_coverage     0.525    Medium

Overall RAG Score    0.962   

📈 IMPROVEMENTS (Advanced vs Basic):
Metric                    Improvement     Impact
------------------------------------------------------------
faithfulness                -2.4% 🔴 Minimal
answer_relevancy            -2.6% 🔴 Minimal
context_precision            0.0% 🔴 Minimal
context_recall               0.0% 🔴 Minimal
average_context_count        0.0% 🔴 Minimal
element_coverage            35.5% 🟢 Significant
overall_rag_score           -1.2% 🔴 Minimal

📈 PERFORMANCE SUMMARY:
Total Questions Tested: 8
Basic Retrieval - Successful: 4
Advanced Retrieval - Successful: 4

🟡 MARGINAL: Advanced retrieval shows modest improvements (4.2% average).

======================================================================

📝 **Task 6:  The Benefits of Advanced Retrieval**

✅
1.	Hybrid Search (Keyword + Semantic) - Already implemented! Combines embedding similarity with keyword matching for robust retrieval.
2.	Metadata Filtering - Already implemented! system can filter by customer tier, date ranges, and other attributes for targeted retrieval.
3.	Re-ranking with Cross-Encoders - Would improve relevance by re-scoring initial results with more sophisticated models.
4.	Query Expansion - Use LLM to generate alternative phrasings of queries for better recall.
5.	Contextual Compression - Reduce retrieved chunks to only relevant portions for more focused context.


📝 **Task 7: Assessing Performance**

Planned improvements for second half:
1.	Fine-tuned Embeddings - Train on  survey-specific vocabulary for better semantic matching
2.	Agentic Memory - Add conversation memory for context-aware follow-up questions
3.	Multi-modal Analysis - Incorporate CSAT scores, usage data, and support tickets



loom video :
https://www.loom.com/share/69c490ce51cb4ee2b01692031b085ce3?sid=4e66e702-3a0e-431f-abd9-2fb8bf1c07e4

