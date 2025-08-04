import os
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

class WebSearchAPI:
    """Web Search API integration using ContextualWeb News API for external context retrieval"""
    
    def __init__(self):
        # RapidAPI key for ContextualWeb
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.contextual_web_host = "contextualwebsearch-websearch-v1.p.rapidapi.com"
        
        # Check if API key is available
        if self.rapidapi_key:
            print("🌐 Web Search API initialized using ContextualWeb News API")
        else:
            print("⚠️ No RapidAPI key found. Using mock data.")
            print("   Get your free API key at: https://rapidapi.com/contextualweb/api/web-search")
    
    def search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web for relevant information using ContextualWeb News API"""
        if self.rapidapi_key:
            return self._search_contextual_web(query, num_results)
        else:
            print("⚠️ No RapidAPI key found. Using mock data.")
            return self._mock_search(query, num_results)
    
    def _search_contextual_web(self, query: str, num_results: int) -> List[Dict]:
        """Search using ContextualWeb News API"""
        url = f"https://{self.contextual_web_host}/api/search/NewsSearchAPI"
        
        # Calculate date range (last 3 months for relevant results)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=90)
        
        querystring = {
            "q": query,
            "pageNumber": "1",
            "pageSize": str(num_results),
            "autoCorrect": "true",
            "fromPublishedDate": from_date.strftime("%Y-%m-%d"),
            "toPublishedDate": to_date.strftime("%Y-%m-%d"),
            "withThumbnails": "false"
        }
        
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": self.contextual_web_host
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('value', [])[:num_results]:
                # Extract clean snippet from description
                snippet = item.get('description', '')
                if item.get('body'):
                    # Use body for more detailed content if available
                    snippet = item['body'][:500] + "..." if len(item['body']) > 500 else item['body']
                
                results.append({
                    'title': item.get('title', ''),
                    'snippet': snippet,
                    'link': item.get('url', ''),
                    'source': item.get('provider', {}).get('name', 'ContextualWeb'),
                    'date': item.get('datePublished', datetime.now().isoformat()),
                    'category': item.get('category', 'general'),
                    'full_content_available': bool(item.get('body'))
                })
            
            print(f"✅ Found {len(results)} news articles via ContextualWeb")
            return results
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print("❌ RapidAPI key invalid or rate limit exceeded")
            else:
                print(f"❌ ContextualWeb API HTTP error: {e}")
            return []
        except Exception as e:
            print(f"❌ ContextualWeb API error: {e}")
            return []
    
    def search_industry_news(self, industry: str, topic: str, days_back: int = 30) -> List[Dict]:
        """Search for recent industry-specific news and articles"""
        query = f"{industry} {topic} news analysis trends"
        
        if self.rapidapi_key:
            url = f"https://{self.contextual_web_host}/api/search/NewsSearchAPI"
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            querystring = {
                "q": query,
                "pageNumber": "1",
                "pageSize": "10",
                "autoCorrect": "true",
                "fromPublishedDate": from_date.strftime("%Y-%m-%d"),
                "toPublishedDate": to_date.strftime("%Y-%m-%d"),
                "withThumbnails": "false",
                "safeSearch": "true"
            }
            
            headers = {
                "X-RapidAPI-Key": self.rapidapi_key,
                "X-RapidAPI-Host": self.contextual_web_host
            }
            
            try:
                response = requests.get(url, headers=headers, params=querystring)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get('value', []):
                    results.append({
                        'title': item.get('title', ''),
                        'snippet': item.get('body', item.get('description', ''))[:500],
                        'link': item.get('url', ''),
                        'source': item.get('provider', {}).get('name', 'Unknown'),
                        'date': item.get('datePublished', ''),
                        'category': f"{industry} news",
                        'relevance_score': item.get('score', 0)
                    })
                
                return results
                
            except Exception as e:
                print(f"❌ Industry news search failed: {e}")
                return []
        
        return self._mock_search(query, 5)
    
    def search_competitor_info(self, competitor_name: str) -> List[Dict]:
        """Specialized search for competitor information in news articles"""
        queries = [
            f"{competitor_name} customer service platform features announcement",
            f"{competitor_name} pricing plans {datetime.now().year}",
            f"{competitor_name} market share customer satisfaction"
        ]
        
        all_results = []
        for query in queries:
            results = self.search(query, num_results=3)
            all_results.extend(results)
        
        # Sort by date to get most recent first
        all_results.sort(key=lambda x: x.get('date', ''), reverse=True)
        
        return all_results[:6]  # Return top 6 most recent
    
    def search_customer_success_insights(self, specific_topic: str = None) -> List[Dict]:
        """Search for customer success best practices and insights"""
        base_query = "customer success best practices SaaS B2B enterprise"
        if specific_topic:
            query = f"{base_query} {specific_topic}"
        else:
            query = base_query
        
        # Search for recent articles with insights
        results = self.search(query, num_results=5)
        
        # Filter for high-quality sources if possible
        quality_sources = ['forrester', 'gartner', 'mckinsey', 'harvard', 'mit', 'techcrunch']
        
        # Sort results to prioritize quality sources
        def sort_key(result):
            source_lower = result.get('source', '').lower()
            for i, quality_source in enumerate(quality_sources):
                if quality_source in source_lower:
                    return i
            return len(quality_sources)  # Put others at the end
        
        results.sort(key=sort_key)
        return results
    
    def enrich_survey_context(self, survey_text: str, customer_industry: str) -> Dict:
        """Enrich survey response with external web context"""
        # Extract key topics from survey
        topics = self._extract_topics(survey_text)
        
        enriched_data = {
            'original_text': survey_text,
            'external_context': [],
            'industry_insights': [],
            'best_practices': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Search for each topic with industry context
        for topic in topics[:3]:  # Limit to top 3 topics
            results = self.search(f"{customer_industry} {topic} trends challenges", num_results=2)
            enriched_data['external_context'].extend(results)
        
        # Get industry-specific insights
        industry_results = self.search_industry_news(customer_industry, "digital transformation customer experience", days_back=60)
        enriched_data['industry_insights'] = industry_results[:3]
        
        # Get customer success best practices
        cs_insights = self.search_customer_success_insights(topics[0] if topics else None)
        enriched_data['best_practices'] = cs_insights[:2]
        
        return enriched_data
    
    def _extract_topics(self, text: str) -> List[str]:
        """Enhanced topic extraction for better search queries"""
        # Keywords that often indicate important topics in customer feedback
        topic_keywords = {
            'portal': ['portal', 'dashboard', 'interface', 'ui', 'ux', 'navigation'],
            'billing': ['billing', 'invoice', 'payment', 'charge', 'cost', 'pricing'],
            'performance': ['slow', 'performance', 'speed', 'lag', 'loading', 'timeout'],
            'support': ['support', 'help', 'service', 'response', 'ticket'],
            'integration': ['integration', 'api', 'connect', 'sync', 'webhook'],
            'security': ['security', 'authentication', 'sso', 'saml', '2fa', 'password'],
            'outage': ['down', 'outage', 'unavailable', 'error', 'crash', 'broken']
        }
        
        text_lower = text.lower()
        topics = []
        
        # Check for each topic category
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        # Check for competitor mentions
        competitor_indicators = ['competitor', 'alternative', 'switch', 'considering', 'comparing']
        if any(indicator in text_lower for indicator in competitor_indicators):
            topics.append("competitor analysis")
        
        # Check for feature requests
        if any(phrase in text_lower for phrase in ['would be nice', 'wish', 'need', 'want', 'missing']):
            topics.append("feature request")
        
        return topics
    
    def _mock_search(self, query: str, num_results: int) -> List[Dict]:
        """Enhanced mock search results for testing without API"""
        # Generate more realistic mock data based on query
        mock_templates = [
            {
                'title': f'How Leading SaaS Companies Address {query}',
                'snippet': f'Recent analysis from Gartner shows that top-performing SaaS companies approach {query} with a combination of proactive monitoring, automated alerts, and dedicated customer success teams. The key is early detection and rapid response...',
                'source': 'Gartner Research',
                'category': 'Industry Analysis'
            },
            {
                'title': f'Best Practices for {query} in Enterprise Software',
                'snippet': f'According to Forrester\'s latest report, enterprises handling {query} should focus on three key areas: real-time analytics, predictive modeling, and cross-functional collaboration. Companies seeing the best results...',
                'source': 'Forrester',
                'category': 'Best Practices'
            },
            {
                'title': f'{query}: Lessons from Digital Transformation Leaders',
                'snippet': f'McKinsey\'s study of digital transformation leaders reveals that {query} is critical for customer retention. Top performers invest 2.5x more in customer experience platforms and see 40% higher satisfaction scores...',
                'source': 'McKinsey Digital',
                'category': 'Digital Transformation'
            },
            {
                'title': f'The Future of {query} - AI and Automation Trends',
                'snippet': f'TechCrunch reports on emerging trends in {query}, highlighting how AI-powered systems are revolutionizing customer success. Early adopters are seeing 60% reduction in response times and 35% improvement in issue resolution...',
                'source': 'TechCrunch',
                'category': 'Technology Trends'
            },
            {
                'title': f'Customer Success Metrics: Measuring {query} Impact',
                'snippet': f'Harvard Business Review analysis shows that companies effectively managing {query} see 23% higher customer lifetime value. The key metrics to track include response time, resolution rate, and customer effort score...',
                'source': 'Harvard Business Review',
                'category': 'Business Strategy'
            }
        ]
        
        results = []
        for i, template in enumerate(mock_templates[:num_results]):
            result = {
                **template,
                'link': f'https://example.com/article-{i+1}',
                'date': (datetime.now() - timedelta(days=i*7)).isoformat(),
                'full_content_available': True
            }
            results.append(result)
        
        return results