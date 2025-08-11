What is the purpose of the chunk_overlap parameter when using RecursiveCharacterTextSplitter to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?


Purpose: keep continuity when a fact spans a chunk boundary so retrieval doesn’t miss it.

Trade-offs:

↑ overlap → better chance long sentences/tables survive splits → higher recall, but more tokens, duplicate content in index, slower retrieval, and sometimes lower precision (more near-duplicates returned).

↓ overlap → faster/smaller index, less redundancy → higher precision on concise facts, but risk of missed context and boundary cuts → lower recall.



Your retriever is configured with search_kwargs={"k": 5}. How would adjusting k likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

Increase k → retriever returns more chunks.

Context Recall: tends to increase (relevant evidence more likely included).

Context Precision: tends to decrease (more irrelevant/noisy chunks dilute context).

Decrease k:

Context Precision: tends to increase (tighter, more on-point context).

Context Recall: tends to decrease (greater chance the gold evidence is missing).

Pick k jointly with re-ranking/compression: larger k + reranker often yields high recall without killing precision.


Question:
Compare the agent and agent_helpful assistants defined in langgraph.json. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

agent (simple_agent): __start__ → agent → action (tools) → agent → __end__.

agent_helpful (agent_with_helpfulness):
__start__ → agent → action (tools) → helpfulness → (agent | __end__).

Where the evaluator fits: right after the tool-use step (action).
Routing logic:

If evaluator judges the draft answer not sufficiently helpful (e.g., missing evidence, low confidence, incomplete), route back to agent to refine/re-query (up to loop limit).

If it’s helpful enough, terminate to __end__ and return the answer.