import streamlit as st
import requests
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Survey Sentinel - AI Enhanced",
    page_icon="🤖",
    layout="wide"
)

# API base URL
API_BASE = "http://localhost:8000"

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE}/system-health")
        return response.status_code == 200, response.json()
    except:
        return False, {}

# Main app
st.title("🤖 Survey Sentinel - AI Enhanced")
st.subtitle("Agent-Based Flagging • RAGAS Evaluation • Advanced Analytics")

# Check API status
api_healthy, health_data = check_api_health()
if not api_healthy:
    st.error("⚠️ API server not running! Please start with: `uvicorn src.main_advanced:app --reload`")
    st.stop()

# Display system health
with st.expander("🔍 System Health", expanded=False):
    if health_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Vector Store", health_data.get('components', {}).get('vector_store', {}).get('stored_vectors', 0))
        with col2:
            st.metric("Recent Flags", health_data.get('components', {}).get('agent_flagging', {}).get('recent_flags', 0))
        with col3:
            st.metric("System Status", health_data.get('system_status', 'unknown'))

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("Choose a page", [
    "📥 Ingest Surveys", 
    "🚩 AI Agent Flags", 
    "🔍 Semantic Search", 
    "📊 Advanced Analytics",
    "🧪 RAGAS Evaluation",
    "💬 RAG Analysis"
])

if page == "📥 Ingest Surveys":
    st.header("📥 Upload & Process Surveys with AI Agents")
    
    uploaded_file = st.file_uploader(
        "Upload Survey CSV", 
        type="csv",
        help="CSV should have columns: survey_id, customer_id, response_text, score, question_code"
    )
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.subheader("📋 Data Preview")
        st.dataframe(df.head())
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Responses", len(df))
        with col2:
            avg_score = df['score'].mean() if 'score' in df.columns else 0
            st.metric("Average Score", f"{avg_score:.1f}/10")
        
        if st.button("🤖 Process with AI Agents", type="primary"):
            with st.spinner("🔄 AI agents analyzing responses..."):
                uploaded_file.seek(0)
                files = {"file": uploaded_file}
                
                try:
                    response = requests.post(f"{API_BASE}/ingest", files=files)
                    result = response.json()
                    
                    if response.status_code == 200:
                        st.success("✅ Processing Complete!")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Processed", result['processed'])
                        with col2:
                            st.metric("Flagged", result['flagged'])
                        with col3:
                            st.metric("Vector Count", result.get('vector_count', 0))
                        with col4:
                            flag_rate = (result['flagged'] / result['processed']) * 100 if result['processed'] > 0 else 0
                            st.metric("Flag Rate", f"{flag_rate:.1f}%")
                        
                        if result['flagged'] > 0:
                            st.warning(f"🚩 {result['flagged']} issues flagged by AI agents!")
                            
                            for i, flag in enumerate(result['flags'][:5]):  # Show top 5
                                with st.expander(f"🚨 {flag['customer_name']} - {flag['priority'].upper()} Priority"):
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write("**Response Preview:**")
                                        st.write(flag['response_preview'])
                                        st.write(f"**Original Score:** {flag.get('original_score', 'N/A')}/10")
                                    with col2:
                                        st.write("**Agent Analysis:**")
                                        st.write(f"**Confidence:** {flag.get('confidence', 0):.1%}")
                                        st.write(f"**Business Impact:** {flag.get('business_impact', 'unknown').title()}")
                                        st.write(f"**Timeline:** {flag.get('timeline', 'unknown')}")
                                        if flag.get('recommended_actions'):
                                            st.write("**Actions:** " + ", ".join(flag['recommended_actions']))
                        else:
                            st.success("🎉 No critical issues detected by AI agents!")
                    else:
                        st.error(f"❌ Processing failed: {result}")
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {e}")

elif page == "🚩 AI Agent Flags":
    st.header("🚩 AI Agent Flagged Issues")
    
    # Enhanced filters
    col1, col2, col3 = st.columns(3)
    with col1:
        tier_filter = st.selectbox("Customer Tier", ["All", "Enterprise", "Mid-Market", "SMB"])
    with col2:
        priority_filter = st.selectbox("Priority Level", ["All", "critical", "high", "medium", "low"])
    with col3:
        days_filter = st.slider("Days Back", 1, 90, 7)
    
    try:
        params = {"days": days_filter}
        if tier_filter != "All":
            params["tier"] = tier_filter
        if priority_filter != "All":
            params["priority"] = priority_filter
            
        response = requests.get(f"{API_BASE}/flags-advanced", params=params)
        flags_data = response.json()
        flags = flags_data.get('flags', [])
        
        if flags:
            st.success(f"🔍 Found {len(flags)} flagged issues")
            
            # Priority distribution chart
            priority_counts = {}
            for flag in flags:
                priority = flag.get('priority', 'unknown')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            if priority_counts:
                fig = px.pie(
                    values=list(priority_counts.values()),
                    names=list(priority_counts.keys()),
                    title="Flag Priority Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Display flags
            for flag in flags:
                priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟠", "low": "🟢"}.get(flag.get('priority'), "⚪")
                
                with st.expander(f"{priority_emoji} {flag.get('customer_name', 'Unknown')} - {flag.get('priority', 'unknown').title()} Priority"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Agent Reasoning:**")
                        st.write(flag.get('reasoning', 'No reasoning provided'))
                        
                        if flag.get('risk_factors'):
                            st.write("**Risk Factors:**")
                            for risk in flag['risk_factors']:
                                st.write(f"• {risk}")
                    
                    with col2:
                        st.metric("Confidence", f"{flag.get('confidence', 0):.1%}")
                        st.metric("Flag Score", f"{flag.get('flag_score', 0)}/10")
                        st.write(f"**Business Impact:** {flag.get('business_impact', 'unknown').title()}")
                        st.write(f"**Escalate To:** {flag.get('escalate_to', 'unknown').title()}")
                        st.write(f"**Timeline:** {flag.get('timeline', 'unknown')}")
                        
                        if flag.get('recommended_actions'):
                            st.write("**Recommended Actions:**")
                            for action in flag['recommended_actions']:
                                st.write(f"• {action.replace('_', ' ').title()}")
        else:
            st.info("ℹ️ No flags found for the selected criteria.")
            
    except Exception as e:
        st.error(f"❌ Error loading flags: {e}")

elif page == "🔍 Semantic Search":
    st.header("🔍 AI-Powered Semantic Search")
    
    query = st.text_input(
        "Search for similar customer feedback", 
        placeholder="e.g., portal performance issues, billing problems, authentication errors"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        k_results = st.slider("Number of results", 1, 10, 5)
    
    if query:
        try:
            response = requests.get(f"{API_BASE}/search", params={"query": query, "k": k_results})
            results = response.json()
            
            if results.get('documents'):
                st.success(f"🎯 Found {len(results['documents'])} similar responses")
                
                for i, (doc, metadata, score) in enumerate(zip(
                    results['documents'],
                    results['metadatas'],
                    results.get('scores', [0] * len(results['documents']))
                )):
                    similarity = max(0, 1 - score) if score else 0.5
                    
                    with st.expander(f"Result {i+1} - {metadata.get('customer_name', 'Unknown')} (Similarity: {similarity:.1%})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write("**Response:**")
                            st.write(doc[:400] + "..." if len(doc) > 400 else doc)
                        
                        with col2:
                            st.write(f"**Customer:** {metadata.get('customer_name', 'Unknown')}")
                            st.write(f"**Tier:** {metadata.get('tier', 'Unknown')}")
                            st.write(f"**Score:** {metadata.get('score', 'N/A')}/10")
                            st.write(f"**Sentiment:** {metadata.get('sentiment', 'Unknown')}")
                            
                            if metadata.get('features_mentioned'):
                                features = json.loads(metadata['features_mentioned']) if isinstance(metadata['features_mentioned'], str) else metadata['features_mentioned']
                                if features:
                                    st.write("**Features:** " + ", ".join(features))
            else:
                st.info("🔍 No similar responses found. Try different search terms.")
                
        except Exception as e:
            st.error(f"❌ Search error: {e}")

elif page == "📊 Advanced Analytics":
    st.header("📊 AI Agent Analytics Dashboard")
    
    days_analytics = st.selectbox("Analysis Period", [7, 14, 30, 60, 90], index=2)
    
    try:
        response = requests.get(f"{API_BASE}/flag-analytics", params={"days": days_analytics})
        analytics = response.json()
        
        if analytics.get('total_flags', 0) > 0:
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Flags", analytics['total_flags'])
            with col2:
                st.metric("Avg Confidence", f"{analytics['average_confidence']:.1%}")
            with col3:
                st.metric("High Confidence", f"{analytics['high_confidence_percentage']:.1f}%")
            with col4:
                insight = analytics.get('agent_insights', {}).get('confidence_trend', 'unknown')
                st.metric("Confidence Trend", insight.title())
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Priority breakdown
                priority_data = analytics.get('priority_breakdown', {})
                if priority_data:
                    fig = px.bar(
                        x=list(priority_data.keys()),
                        y=list(priority_data.values()),
                        title="Priority Distribution",
                        color=list(priority_data.keys()),
                        color_discrete_map={
                            'critical': '#ff4444',
                            'high': '#ff8800', 
                            'medium': '#ffaa00',
                            'low': '#44ff44'
                        }
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Business impact
                impact_data = analytics.get('business_impact_breakdown', {})
                if impact_data:
                    fig = px.pie(
                        values=list(impact_data.values()),
                        names=list(impact_data.keys()),
                        title="Business Impact Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Escalation and timeline breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                escalation_data = analytics.get('escalation_breakdown', {})
                if escalation_data:
                    st.subheader("Escalation Targets")
                    for target, count in escalation_data.items():
                        percentage = (count / analytics['total_flags']) * 100
                        st.progress(percentage / 100)
                        st.write(f"{target.title()}: {count} ({percentage:.1f}%)")
            
            with col2:
                timeline_data = analytics.get('timeline_breakdown', {})
                if timeline_data:
                    st.subheader("Required Timeline")
                    for timeline, count in timeline_data.items():
                        percentage = (count / analytics['total_flags']) * 100
                        st.progress(percentage / 100)
                        st.write(f"{timeline}: {count} ({percentage:.1f}%)")
            
            # Agent insights
            st.subheader("🤖 AI Agent Insights")
            insights = analytics.get('agent_insights', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Most Common Priority:** {insights.get('most_common_priority', 'N/A').title()}")
            with col2:
                st.info(f"**Most Common Escalation:** {insights.get('most_common_escalation', 'N/A').title()}")
            with col3:
                st.info(f"**Confidence Trend:** {insights.get('confidence_trend', 'N/A').title()}")
        else:
            st.info(f"📊 No flags found in the last {days_analytics} days to analyze.")
            
    except Exception as e:
        st.error(f"❌ Analytics error: {e}")

elif page == "🧪 RAGAS Evaluation":
    st.header("🧪 RAGAS-Powered Evaluation")
    st.write("Generate synthetic test data and evaluate system performance using RAGAS (RAG Assessment)")
    
    # Synthetic data generation
    st.subheader("🔬 Generate Synthetic Test Data")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        synthetic_size = st.slider("Number of synthetic cases", 10, 100, 30)
    with col2:
        if st.button("🧬 Generate Synthetic Data"):
            with st.spinner("🔄 RAGAS generating synthetic test cases..."):
                try:
                    response = requests.post(f"{API_BASE}/generate-synthetic-data", params={"size": synthetic_size})
                    result = response.json()
                    
                    if result.get('success'):
                        st.success(f"✅ Generated {result['generated_cases']} synthetic test cases")
                        
                        if result.get('sample_cases'):
                            st.subheader("📋 Sample Generated Cases")
                            for i, case in enumerate(result['sample_cases']):
                                with st.expander(f"Sample {i+1}: {case.get('customer_name', 'Unknown')}"):
                                    st.write(f"**Response:** {case.get('response_text', 'N/A')}")
                                    st.write(f"**Score:** {case.get('score', 'N/A')}/10")
                                    st.write(f"**Question Code:** {case.get('question_code', 'N/A')}")
                    else:
                        st.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    # System evaluation
    st.subheader("⚡ Run Comprehensive Evaluation")
    
    if st.button("🚀 Run RAGAS Evaluation", type="primary"):
        with st.spinner("🔄 Running comprehensive evaluation... This may take a few minutes."):
            try:
                response = requests.post(f"{API_BASE}/run-evaluation")
                result = response.json()
                
                if result.get('evaluation_completed'):
                    st.success("✅ Evaluation completed successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Test Cases", result['synthetic_test_cases'])
                    with col2:
                        st.metric("Flagging Accuracy", f"{result['flagging_accuracy']:.1%}")
                    with col3:
                        st.metric("Avg Confidence", f"{result['average_confidence']:.1%}")
                    
                    # Priority distribution
                    priority_dist = result.get('priority_distribution', {})
                    if priority_dist:
                        st.subheader("📊 Test Results Priority Distribution")
                        fig = px.bar(
                            x=list(priority_dist.keys()),
                            y=list(priority_dist.values()),
                            title="Synthetic Test Priority Distribution",
                            color=list(priority_dist.keys())
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.info(f"📄 Detailed results saved to: {result['results_file']}")
                else:
                    st.error(f"❌ Evaluation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Evaluation error: {e}")

elif page == "💬 RAG Analysis":
    st.header("💬 RAG-Powered Survey Analysis")
    st.write("Ask intelligent questions about your survey data using Retrieval-Augmented Generation")
    
    # Sample questions
    st.subheader("💡 Try These Sample Questions")
    sample_questions = [
        "What are the most common portal performance issues?",
        "Which Enterprise customers are mentioning competitors?",
        "What billing-related problems are customers reporting?",
        "How do authentication issues affect different customer tiers?",
        "What patterns do you see in low-scoring responses?",
        "Which features are customers most frustrated with?"
    ]
    
    cols = st.columns(3)
    for i, question in enumerate(sample_questions):
        with cols[i % 3]:
            if st.button(question, key=f"sample_{i}"):
                st.session_state['rag_query'] = question
    
    # Main query input
    query = st.text_area(
        "Ask a question about your survey data:",
        value=st.session_state.get('rag_query', ''),
        placeholder="e.g., What are customers saying about our API performance compared to competitors?",
        height=100
    )
    
    if st.button("🔍 Analyze with RAG", type="primary") and query:
        with st.spinner("🤖 AI analyzing survey data to answer your question..."):
            try:
                response = requests.get(f"{API_BASE}/analyze", params={"query": query})
                result = response.json()
                
                if response.status_code == 200:
                    st.success("✅ Analysis complete!")
                    
                    # Display analysis
                    st.subheader("📝 AI Analysis")
                    st.write(result['analysis'])
                    
                    # Show context info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Context Sources", result['context_count'])
                    with col2:
                        st.metric("Customers Referenced", len(set(result['sources'])))
                    
                    # Show source customers
                    if result['sources']:
                        st.subheader("📊 Source Customers")
                        sources_df = pd.DataFrame({'Customer': result['sources']})
                        source_counts = sources_df['Customer'].value_counts()
                        
                        fig = px.bar(
                            x=source_counts.index,
                            y=source_counts.values,
                            title="Responses by Customer",
                            labels={'x': 'Customer', 'y': 'Number of Responses'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Analysis error: {e}")

# Add footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🤖 Survey Sentinel v0.4.0 - Powered by AI Agents & RAGAS</p>
    <p>Features: Agent-Based Flagging • Synthetic Data Generation • Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)