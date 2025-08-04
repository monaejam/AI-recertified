from typing import TypedDict, List, Dict, Any
import json
import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain.tools import Tool

# Try different LangGraph import patterns
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    try:
        from langgraph import StateGraph, END  
        LANGGRAPH_AVAILABLE = True
    except ImportError:
        try:
            from langgraph.prebuilt import StateGraph, END
            LANGGRAPH_AVAILABLE = True
        except ImportError:
            print("⚠️ LangGraph not available, falling back to simple workflow")
            LANGGRAPH_AVAILABLE = False
            StateGraph = None
            END = None

# Define the agent state
class AgentState(TypedDict):
    survey_data: Dict
    ai_analysis: Dict
    customer_history: str
    pattern_analysis: str
    business_impact: str
    escalation_check: str
    final_decision: Dict
    reasoning_steps: List[str]

class FlaggingTools:
    """Advanced tools for intelligent flagging decisions"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Load business rules and customer data
        self.alert_rules = self._load_alert_rules()
        self.product_features = self._load_product_features()
        self.customer_data = self._load_customer_data()
    
    def _load_alert_rules(self) -> dict:
        """Load alert rules from JSON"""
        try:
            with open('data/alert_rules.json', 'r') as f:
                return json.load(f)
        except:
            return {"alert_rules": []}
    
    def _load_product_features(self) -> dict:
        """Load product feature ontology"""
        try:
            with open('data/product_features.md', 'r') as f:
                content = f.read()
                return {"content": content}
        except:
            return {"content": ""}
    
    def _load_customer_data(self) -> pd.DataFrame:
        """Load customer master data"""
        try:
            return pd.read_csv('data/customer_master.csv')
        except:
            return pd.DataFrame()
    
    def check_customer_history(self, customer_id: str) -> str:
        """Tool: Analyze customer's historical patterns"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get historical flags
            cursor.execute("""
                SELECT COUNT(*) as flag_count, AVG(flag_score) as avg_score,
                       MAX(created_at) as last_flag
                FROM flags_advanced 
                WHERE customer_name IN (
                    SELECT company_name FROM customer_master WHERE customer_id = ?
                ) AND created_at >= datetime('now', '-90 days')
            """, (customer_id,))
            
            result = cursor.fetchone()
            
            # Get customer details
            customer_info = self.customer_data[
                self.customer_data['customer_id'] == customer_id
            ]
            
            if customer_info.empty:
                customer_details = "Customer not found in master data"
            else:
                customer_details = f"Tier: {customer_info.iloc[0]['tier']}, MRR: ${customer_info.iloc[0]['mrr']:,}, Tenure: {customer_info.iloc[0]['tenure_months']} months"
            
            conn.close()
            
            if result and result[0] > 0:
                return f"Customer has {result[0]} flags in last 90 days (avg score: {result[1]:.1f}). {customer_details}. Pattern suggests recurring issues."
            else:
                return f"Clean history - no recent flags. {customer_details}. This appears to be first-time issue."
                
        except Exception as e:
            return f"Error checking history: {e}"
    
    def analyze_similar_patterns(self, response_text: str, customer_tier: str) -> str:
        """Tool: Find similar issues across customer base"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Look for similar issues in same tier
            similar_count = 0
            for term in ['outage', 'slow', 'billing', 'portal', 'error']:
                if term in response_text.lower():
                    cursor.execute("""
                        SELECT COUNT(*) FROM flags_advanced f
                        JOIN survey_responses s ON f.survey_id = s.survey_id
                        WHERE lower(s.response_text) LIKE ? 
                        AND f.tier = ?
                        AND f.created_at >= datetime('now', '-14 days')
                    """, (f'%{term}%', customer_tier))
                    
                    count = cursor.fetchone()[0]
                    similar_count += count
            
            conn.close()
            
            if similar_count > 2:
                return f"PATTERN DETECTED: {similar_count} similar issues from {customer_tier} customers in last 14 days. This suggests systemic problem."
            elif similar_count > 0:
                return f"Some similar issues reported ({similar_count} cases) - monitoring for trends."
            else:
                return "No similar patterns detected - appears to be isolated incident."
                
        except Exception as e:
            return f"Error analyzing patterns: {e}"
    
    def evaluate_business_impact(self, customer_id: str, extracted_data: dict) -> str:
        """Tool: Assess business impact based on customer value and issue severity"""
        try:
            # Get customer business metrics
            customer_info = self.customer_data[
                self.customer_data['customer_id'] == customer_id
            ]
            
            if customer_info.empty:
                return "Unable to assess business impact - customer not found"
            
            customer = customer_info.iloc[0]
            mrr = customer['mrr']
            tier = customer['tier']
            tenure = customer['tenure_months']
            
            # Calculate business impact score
            impact_factors = []
            
            if extracted_data.get('revenue_impact'):
                impact_factors.append("Direct revenue impact mentioned")
            
            if tier == 'Enterprise' and mrr > 50000:
                impact_factors.append("High-value Enterprise customer")
            
            if tenure < 12:
                impact_factors.append("New customer - retention risk")
            
            if extracted_data.get('competitors_mentioned'):
                impact_factors.append("Competitor comparison - churn risk")
            
            impact_level = "HIGH" if len(impact_factors) >= 2 else "MEDIUM" if len(impact_factors) == 1 else "LOW"
            
            return f"Business Impact: {impact_level}. Customer MRR: ${mrr:,}, Tier: {tier}, Tenure: {tenure}mo. Factors: {'; '.join(impact_factors) if impact_factors else 'None identified'}"
            
        except Exception as e:
            return f"Error evaluating business impact: {e}"
    
    def check_escalation_triggers(self, extracted_data: dict, customer_tier: str) -> str:
        """Tool: Check against defined escalation rules"""
        triggered_rules = []
        
        for rule in self.alert_rules.get('alert_rules', []):
            rule_triggered = True
            
            # Check conditions
            conditions = rule.get('conditions', {})
            
            # Check customer tier
            if 'customer_tier' in conditions:
                if customer_tier not in conditions['customer_tier']:
                    rule_triggered = False
            
            # Check revenue impact
            if 'revenue_impact' in conditions and not extracted_data.get('revenue_impact'):
                rule_triggered = False
            
            # Check competitors mentioned
            if 'competitors_mentioned' in conditions:
                if conditions['competitors_mentioned'].get('exists') and not extracted_data.get('competitors_mentioned'):
                    rule_triggered = False
            
            if rule_triggered:
                triggered_rules.append({
                    'rule': rule['name'],
                    'priority': rule['priority'],
                    'actions': rule['actions']
                })
        
        if triggered_rules:
            return f"ESCALATION TRIGGERED: {len(triggered_rules)} rules matched. Highest priority: {min(r['priority'] for r in triggered_rules)}"
        else:
            return "No escalation rules triggered - standard handling applies"

class LangGraphFlaggingAgent:
    """LangGraph-based intelligent survey response flagging agent with fallback"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv('DB_PATH', './survey_sentinel.db')
        self.tools_helper = FlaggingTools(self.db_path)
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create the workflow (LangGraph or fallback)
        if LANGGRAPH_AVAILABLE:
            self.graph = self._create_langgraph_workflow()
            self.agent_type = "langgraph"
            print("✅ LangGraph agent initialized")
        else:
            self.graph = None
            self.agent_type = "sequential_fallback"
            print("⚠️ Using sequential fallback (LangGraph not available)")
    
    def _create_langgraph_workflow(self):
        """Create the LangGraph workflow for intelligent flagging"""
        if not LANGGRAPH_AVAILABLE:
            return None
            
        try:
            # Define the workflow graph
            workflow = StateGraph(AgentState)
            
            # Add nodes for each analysis step
            workflow.add_node("check_history", self._check_customer_history)
            workflow.add_node("analyze_patterns", self._analyze_patterns)
            workflow.add_node("assess_impact", self._assess_business_impact)
            workflow.add_node("check_escalation", self._check_escalation_rules)
            workflow.add_node("make_decision", self._make_final_decision)
            
            # Define the workflow flow
            workflow.set_entry_point("check_history")
            workflow.add_edge("check_history", "analyze_patterns")
            workflow.add_edge("analyze_patterns", "assess_impact")
            workflow.add_edge("assess_impact", "check_escalation")
            workflow.add_edge("check_escalation", "make_decision")
            workflow.add_edge("make_decision", END)
            
            return workflow.compile()
        except Exception as e:
            print(f"⚠️ LangGraph compilation failed: {e}, using fallback")
            return None
    
    def _check_customer_history(self, state: AgentState) -> AgentState:
        """Graph Node: Check customer historical patterns"""
        customer_id = state["survey_data"].get("customer_id", "")
        
        try:
            history_result = self.tools_helper.check_customer_history(customer_id)
            state["customer_history"] = history_result
            state["reasoning_steps"].append(f"🔍 Customer History: {history_result[:100]}...")
        except Exception as e:
            state["customer_history"] = f"Error: {e}"
            state["reasoning_steps"].append(f"⚠️ History check failed: {e}")
        
        return state
    
    def _analyze_patterns(self, state: AgentState) -> AgentState:
        """Graph Node: Analyze similar patterns across customer base"""
        response_text = state["survey_data"].get("response_text", "")
        customer_tier = state["survey_data"].get("tier", "Unknown")
        
        try:
            pattern_result = self.tools_helper.analyze_similar_patterns(response_text, customer_tier)
            state["pattern_analysis"] = pattern_result
            state["reasoning_steps"].append(f"📊 Pattern Analysis: {pattern_result[:100]}...")
        except Exception as e:
            state["pattern_analysis"] = f"Error: {e}"
            state["reasoning_steps"].append(f"⚠️ Pattern analysis failed: {e}")
        
        return state
    
    def _assess_business_impact(self, state: AgentState) -> AgentState:
        """Graph Node: Assess business impact"""
        customer_id = state["survey_data"].get("customer_id", "")
        ai_analysis = state["ai_analysis"]
        
        try:
            impact_result = self.tools_helper.evaluate_business_impact(customer_id, ai_analysis)
            state["business_impact"] = impact_result
            state["reasoning_steps"].append(f"💼 Business Impact: {impact_result[:100]}...")
        except Exception as e:
            state["business_impact"] = f"Error: {e}"
            state["reasoning_steps"].append(f"⚠️ Impact assessment failed: {e}")
        
        return state
    
    def _check_escalation_rules(self, state: AgentState) -> AgentState:
        """Graph Node: Check escalation triggers"""
        ai_analysis = state["ai_analysis"]
        customer_tier = state["survey_data"].get("tier", "Unknown")
        
        try:
            escalation_result = self.tools_helper.check_escalation_triggers(ai_analysis, customer_tier)
            state["escalation_check"] = escalation_result
            state["reasoning_steps"].append(f"🚨 Escalation Check: {escalation_result[:100]}...")
        except Exception as e:
            state["escalation_check"] = f"Error: {e}"
            state["reasoning_steps"].append(f"⚠️ Escalation check failed: {e}")
        
        return state
    
    def _make_final_decision(self, state: AgentState) -> AgentState:
        """Graph Node: Make comprehensive flagging decision using LLM"""
        
        # Create decision prompt with all gathered context  
        decision_prompt = f"""
        You are an expert Customer Success flagging agent. Based on the comprehensive analysis below, make an intelligent flagging decision.

        SURVEY RESPONSE:
        Customer: {state['survey_data'].get('customer_name', 'Unknown')}
        Score: {state['survey_data'].get('score', 'N/A')}/10
        Response: {state['survey_data'].get('response_text', '')}

        ANALYSIS RESULTS:
        Customer History: {state['customer_history']}
        Pattern Analysis: {state['pattern_analysis']}
        Business Impact: {state['business_impact']}
        Escalation Check: {state['escalation_check']}
        AI Sentiment: {state['ai_analysis'].get('sentiment', 'unknown')}
        AI Issues: {state['ai_analysis'].get('issues', [])}

        Return ONLY a JSON object with this exact structure:
        {{
            "should_flag": true/false,
            "confidence": 0.0-1.0,
            "priority": "low/medium/high/critical",
            "flag_score": 0-10,
            "reasoning": "detailed explanation of decision logic",
            "business_impact": "low/medium/high",
            "recommended_actions": ["specific actions"],
            "escalate_to": "none/csm/am/leadership/executive",
            "timeline": "immediate/24h/48h/week",
            "risk_factors": ["identified risks"],
            "pattern_analysis": "isolated/trending/systemic"
        }}
        """
        
        try:
            response = self.llm.invoke(decision_prompt)
            
            # Parse LLM response
            try:
                decision_text = response.content
                if '{' in decision_text and '}' in decision_text:
                    json_start = decision_text.find('{')
                    json_end = decision_text.rfind('}') + 1
                    json_str = decision_text[json_start:json_end]
                    decision = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in LLM response")
                    
            except json.JSONDecodeError:
                # Fallback decision if JSON parsing fails
                decision = self._create_fallback_decision(state)
            
            # Enhance decision with agent metadata
            decision["agent_type"] = self.agent_type
            decision["reasoning_steps"] = state["reasoning_steps"]
            decision["graph_execution"] = "successful"
            
            state["final_decision"] = decision
            state["reasoning_steps"].append(f"✅ Final Decision: {'FLAG' if decision['should_flag'] else 'NO FLAG'} ({decision['priority']} priority)")
            
        except Exception as e:
            print(f"❌ Decision making error: {e}")
            decision = self._create_fallback_decision(state)
            decision["agent_type"] = f"{self.agent_type}_error"
            decision["error"] = str(e)
            state["final_decision"] = decision
        
        return state
    
    def _run_sequential_workflow(self, initial_state: AgentState) -> AgentState:
        """Fallback sequential workflow when LangGraph is not available"""
        print("🔄 Running sequential workflow...")
        
        # Run each step sequentially
        state = self._check_customer_history(initial_state)
        state = self._analyze_patterns(state)
        state = self._assess_business_impact(state)
        state = self._check_escalation_rules(state)
        state = self._make_final_decision(state)
        
        return state
    
    def _create_fallback_decision(self, state: AgentState) -> Dict:
        """Create fallback decision when LLM fails"""
        survey_data = state["survey_data"]
        ai_analysis = state["ai_analysis"]
        
        score = survey_data.get('score', 5)
        sentiment = ai_analysis.get('sentiment', 'neutral')
        
        # Simple fallback logic
        flag_score = 0
        if score <= 3: flag_score += 4
        if sentiment == 'negative': flag_score += 3
        if ai_analysis.get('revenue_impact'): flag_score += 5
        
        return {
            "should_flag": flag_score >= 5,
            "confidence": 0.6,
            "priority": "medium",
            "flag_score": flag_score,
            "reasoning": f"{self.agent_type} fallback decision due to LLM parsing error",
            "business_impact": "medium",
            "recommended_actions": ["manual_review"],
            "escalate_to": "csm",
            "timeline": "24h",
            "risk_factors": ["llm_parsing_error"],
            "pattern_analysis": "unknown"
        }
    
    def analyze_and_flag(self, survey_data: Dict, ai_analysis: Dict) -> Dict:
        """Main entry point - execute workflow (LangGraph or sequential fallback)"""
        
        print(f"🚀 {self.agent_type.title()} Agent analyzing response from {survey_data.get('customer_name', 'Unknown')}...")
        
        # Initialize agent state
        initial_state = AgentState(
            survey_data=survey_data,
            ai_analysis=ai_analysis,
            customer_history="",
            pattern_analysis="",
            business_impact="",
            escalation_check="",
            final_decision={},
            reasoning_steps=[]
        )
        
        try:
            # Execute the workflow
            if self.graph is not None and LANGGRAPH_AVAILABLE:
                final_state = self.graph.invoke(initial_state)
            else:
                final_state = self._run_sequential_workflow(initial_state)
                
            decision = final_state["final_decision"]
            
            # Store flag if needed
            if decision.get('should_flag', False):
                self._store_advanced_flag(survey_data, decision)
                print(f"🚩 {self.agent_type.title()} Flagged: {decision['priority']} priority - {decision['reasoning'][:100]}...")
            
            return decision
            
        except Exception as e:
            print(f"❌ {self.agent_type.title()} execution failed: {e}")
            return self._create_fallback_decision({
                "survey_data": survey_data,
                "ai_analysis": ai_analysis,
                "reasoning_steps": [f"{self.agent_type} execution error: {e}"]
            })
    
    def _store_advanced_flag(self, survey_data: dict, decision: dict):
        """Store enhanced flag data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create enhanced table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS flags_advanced (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_id TEXT,
                    customer_id TEXT,
                    customer_name TEXT,
                    question_code TEXT,
                    original_score INTEGER,
                    flag_score REAL,
                    confidence REAL,
                    priority TEXT,
                    business_impact TEXT,
                    reasoning TEXT,
                    recommended_actions TEXT,
                    escalate_to TEXT,
                    timeline TEXT,
                    risk_factors TEXT,
                    pattern_analysis TEXT,
                    agent_reasoning TEXT,
                    agent_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert flag
            cursor.execute("""
                INSERT INTO flags_advanced 
                (survey_id, customer_id, customer_name, question_code, original_score,
                 flag_score, confidence, priority, business_impact, reasoning,
                 recommended_actions, escalate_to, timeline, risk_factors,
                 pattern_analysis, agent_reasoning, agent_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                survey_data.get('survey_id'),
                survey_data.get('customer_id'),
                survey_data.get('customer_name'),
                survey_data.get('question_code'),
                survey_data.get('score'),
                decision.get('flag_score', 0),
                decision.get('confidence', 0),
                decision.get('priority', 'medium'),
                decision.get('business_impact', 'medium'),
                decision.get('reasoning', ''),
                json.dumps(decision.get('recommended_actions', [])),
                decision.get('escalate_to', 'csm'),
                decision.get('timeline', '24h'),
                json.dumps(decision.get('risk_factors', [])),
                decision.get('pattern_analysis', 'unknown'),
                json.dumps(decision.get('reasoning_steps', [])),
                decision.get('agent_type', self.agent_type)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Flag storage error: {e}")
    
    def get_advanced_flags(self, tier: str = None, days: int = 7, priority: str = None) -> List[dict]:
        """Retrieve flags with full context"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT f.*, c.tier, c.mrr 
                FROM flags_advanced f
                LEFT JOIN customer_master c ON f.customer_id = c.customer_id
                WHERE f.created_at >= datetime('now', '-{} days')
            """.format(days)
            
            params = []
            if tier and tier != "All":
                query += " AND c.tier = ?"
                params.append(tier)
            
            if priority:
                query += " AND f.priority = ?"
                params.append(priority)
            
            query += " ORDER BY f.flag_score DESC, f.created_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in rows:
                flag_dict = dict(zip(columns, row))
                # Parse JSON fields
                try:
                    flag_dict['recommended_actions'] = json.loads(flag_dict['recommended_actions'] or '[]')
                    flag_dict['risk_factors'] = json.loads(flag_dict['risk_factors'] or '[]')
                    flag_dict['agent_reasoning'] = json.loads(flag_dict['agent_reasoning'] or '[]')
                except:
                    pass
                results.append(flag_dict)
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Flag retrieval error: {e}")
            return []

# Alias for backward compatibility
SmartFlaggingAgent = LangGraphFlaggingAgent