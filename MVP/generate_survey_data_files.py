#!/usr/bin/env python3
"""
Survey Sentinel Sample Data Generator
Creates all the necessary files for the Survey Sentinel project
"""

import csv
import json
import os
from datetime import datetime

def create_survey_responses():
    """Create survey_responses.csv"""
    survey_data = [
        ["survey_id", "customer_id", "question_code", "score", "response_text", "timestamp"],
        ["SR001", "CUST-ENT-001", "Portal_Experience", "3", "The portal is extremely slow during peak hours. We're losing productivity and considering alternatives. Page loads take 30+ seconds for basic operations.", "2024-01-15T09:23:00Z"],
        ["SR002", "CUST-SMB-012", "Portal_Experience", "8", "Generally happy with the portal. Minor hiccups with the mobile view but nothing major. Would love dark mode!", "2024-01-15T10:45:00Z"],
        ["SR003", "CUST-ENT-002", "P_Feedback_general", "2", "Your product's billing API broke again this week. This is the third time this month. Unacceptable for our scale. We process 10K invoices daily.", "2024-01-15T11:00:00Z"],
        ["SR004", "CUST-ENT-001", "CSM_Review", "4", "Our CSM used to respond within hours, now it's days. Sarah is great but seems overloaded. We need more proactive support for our account size.", "2024-01-15T14:22:00Z"],
        ["SR005", "CUST-MID-005", "Portal_Experience", "9", "Love the new dashboard features in the portal! The real-time analytics are exactly what we needed. Great job on the UI refresh.", "2024-01-15T15:30:00Z"],
        ["SR006", "CUST-ENT-003", "S_Feedback_general", "5", "Service delivery workflows are clunky. CompetitorX has a much smoother process. Takes us 15 steps to do what they do in 5.", "2024-01-16T08:15:00Z"],
        ["SR007", "CUST-SMB-023", "Technical_Workshop", "7", "Decent workshop but wish the API documentation examples were clearer. Presenter knew their stuff though.", "2024-01-16T09:00:00Z"],
        ["SR008", "CUST-ENT-004", "SA_Feedback_general", "1", "Complete outage last night cost us $50K in lost sales. No proactive communication from Service Assurance. Evaluating other vendors.", "2024-01-16T10:30:00Z"],
        ["SR009", "CUST-MID-008", "Portal_Experience", "6", "Portal auth system keeps logging us out randomly. Frustrating but not a dealbreaker yet. Happens 5-6 times daily.", "2024-01-16T11:45:00Z"],
        ["SR010", "CUST-ENT-002", "Portal_Experience", "4", "The portal performance issues are getting worse. Dashboard widgets timeout constantly. Can't run reports during business hours.", "2024-01-16T13:00:00Z"],
        ["SR011", "CUST-SMB-034", "General_Experience", "10", "Best decision we made was switching to X. Everything just works! Your team is fantastic.", "2024-01-16T14:15:00Z"],
        ["SR012", "CUST-ENT-005", "BILL_Feedback_general", "3", "Billing discrepancies every month. Invoice downloads fail 50% of the time. Your billing portal doesn't match what we're charged.", "2024-01-16T15:30:00Z"],
        ["SR013", "CUST-MID-011", "Portal_Experience", "7", "Solid portal but the SSO integration is overly complicated for our users. Too many redirects.", "2024-01-17T08:00:00Z"],
        ["SR014", "CUST-ENT-001", "P_Feedback_general", "2", "Product reliability is killing us. 3 outages this week alone. Senior management is asking about alternatives. We need an executive escalation.", "2024-01-17T09:30:00Z"],
        ["SR015", "CUST-SMB-045", "AM_Business_Review", "8", "Quick question from our business review - when will the new reporting features be available? Our AM couldn't give us a date.", "2024-01-17T10:00:00Z"],
        ["SR016", "CUST-ENT-006", "S_Feedback_general", "5", "Service delivery module needs work. Too many manual approvals. Your competitors have this automated.", "2024-01-17T11:15:00Z"],
        ["SR017", "CUST-MID-014", "CSM_Review", "9", "Great CSM meeting! They resolved our integration issue quickly and followed up proactively.", "2024-01-17T13:00:00Z"],
        ["SR018", "CUST-ENT-003", "Portal_Experience", "3", "Portal is practically unusable during business hours. API response times > 10s for simple queries. This is impacting our customer SLAs.", "2024-01-17T14:30:00Z"],
        ["SR019", "CUST-SMB-056", "General_Experience", "6", "X works but feels outdated compared to newer solutions. UI needs a refresh.", "2024-01-17T15:45:00Z"],
        ["SR020", "CUST-ENT-007", "P_Feedback_general", "4", "Login issues affecting 200+ users. SAML integration keeps failing without clear error messages. Need better error handling.", "2024-01-17T16:00:00Z"],
        ["SR021", "CUST-MID-017", "Portal_Experience", "7", "Happy with portal overall but the mobile experience needs improvement. Tables don't render properly.", "2024-01-18T08:30:00Z"],
        ["SR022", "CUST-ENT-004", "PM_Feedback_general", "1", "Another unplanned outage during your 'planned maintenance'. This is becoming a pattern. Board is questioning our vendor choice.", "2024-01-18T09:00:00Z"],
        ["SR023", "CUST-SMB-067", "Technical_Workshop", "9", "Loving the API workshop! Instructor made complex integrations simple. More of these please!", "2024-01-18T10:15:00Z"],
        ["SR024", "CUST-ENT-008", "BILL_Feedback_general", "3", "Billing API performance is abysmal. Takes 45+ seconds to generate invoices. We're building workarounds which defeats the purpose.", "2024-01-18T11:30:00Z"],
        ["SR025", "CUST-MID-020", "Portal_Experience", "5", "2FA flow in the portal is confusing our users. Many complaints about SMS delays and backup codes not working.", "2024-01-18T13:00:00Z"],
        ["SR026", "CUST-ENT-002", "SA_Feedback_general", "2", "Service Assurance team is unresponsive. Portal issues persist for weeks. Our productivity is down 30% due to system slowness.", "2024-01-18T14:15:00Z"],
        ["SR027", "CUST-SMB-078", "Quoting_Ordering", "8", "Good value for money on the quoting tool. A few UI quirks but nothing major. Quotes generate quickly.", "2024-01-18T15:00:00Z"],
        ["SR028", "CUST-ENT-009", "S_Feedback_general", "4", "Service delivery automation promised in sales pitch still not delivered after 6 months. Manual processes are killing efficiency.", "2024-01-18T16:30:00Z"],
        ["SR029", "CUST-MID-023", "CSM_Review", "10", "Your CSM team went above and beyond during our migration. Couldn't be happier! Lisa anticipated every issue.", "2024-01-18T17:00:00Z"],
        ["SR030", "CUST-ENT-001", "General_Experience", "2", "Third survey this month with the same feedback: THE PORTAL IS TOO SLOW. Please escalate to leadership. We're a $125K/month customer!", "2024-01-18T17:30:00Z"],
        ["SR031", "CUST-ENT-010", "BILL_Feedback_general", "3", "Billing portal crashes when downloading large invoice batches. Been an issue for 3 months. Finance team is furious.", "2024-01-19T08:00:00Z"],
        ["SR032", "CUST-MID-026", "Technical_Workshop", "6", "Workshop content was good but examples used old API versions. Confusing when our integration uses v3.", "2024-01-19T09:15:00Z"],
        ["SR033", "CUST-ENT-011", "P_Feedback_general", "2", "Product uptime SLA breached 4 months straight. Considering legal action. This isn't what we signed up for.", "2024-01-19T10:30:00Z"],
        ["SR034", "CUST-SMB-089", "AM_Business_Review", "9", "Our AM is fantastic! Always prepared and brings valuable insights about industry trends.", "2024-01-19T11:45:00Z"],
        ["SR035", "CUST-ENT-012", "Portal_Experience", "4", "Portal search is broken. Can't find our own data. Elasticsearch errors everywhere. How is this enterprise software?", "2024-01-19T13:00:00Z"],
        ["SR036", "CUST-MID-029", "S_Feedback_general", "7", "Service delivery is smooth but communication could be better. We find out about delays after the fact.", "2024-01-19T14:15:00Z"],
        ["SR037", "CUST-ENT-013", "PM_Feedback_general", "3", "'Planned' maintenance always runs over. Last window was 2 hours, actual downtime was 6. Cost us significant revenue.", "2024-01-19T15:30:00Z"],
        ["SR038", "CUST-SMB-095", "General_Experience", "8", "X platform does what we need. Support is responsive. Happy customer here!", "2024-01-19T16:45:00Z"],
        ["SR039", "CUST-ENT-001", "SA_Feedback_general", "1", "URGENT: Portal down AGAIN. Service assurance hasn't responded to 5 tickets. Escalating to our executive sponsor.", "2024-01-19T17:00:00Z"],
        ["SR040", "CUST-MID-032", "Quoting_Ordering", "5", "Quoting tool is okay but lacks bulk operations. We have to create quotes one by one which is time consuming.", "2024-01-19T17:30:00Z"]
    ]
    
    with open('survey_responses.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(survey_data)
    print("✓ Created survey_responses.csv")

def create_customer_master():
    """Create customer_master.csv"""
    customer_data = [
        ["customer_id", "company_name", "tier", "mrr", "segment", "tenure_months", "account_owner", "industry"],
        ["CUST-ENT-001", "MegaCorp Industries", "Enterprise", "125000", "Financial Services", "36", "Sarah Johnson", "Banking"],
        ["CUST-ENT-002", "GlobalTech Solutions", "Enterprise", "85000", "Technology", "24", "Mike Chen", "SaaS"],
        ["CUST-ENT-003", "National Retail Chain", "Enterprise", "95000", "Retail", "18", "Lisa Anderson", "E-commerce"],
        ["CUST-ENT-004", "FinanceMax Corp", "Enterprise", "150000", "Financial Services", "42", "Tom Wilson", "Investment"],
        ["CUST-ENT-005", "DataDrive Systems", "Enterprise", "110000", "Technology", "30", "Emma Davis", "Analytics"],
        ["CUST-ENT-006", "Continental Logistics", "Enterprise", "90000", "Logistics", "22", "James Brown", "Shipping"],
        ["CUST-ENT-007", "SecureNet Inc", "Enterprise", "105000", "Technology", "28", "Rachel Green", "Security"],
        ["CUST-ENT-008", "MediCare Plus", "Enterprise", "120000", "Healthcare", "34", "David Miller", "Insurance"],
        ["CUST-ENT-009", "EduTech Global", "Enterprise", "80000", "Education", "20", "Nina Patel", "EdTech"],
        ["CUST-ENT-010", "TelecomGiant", "Enterprise", "140000", "Telecommunications", "38", "Carlos Rodriguez", "Telecom"],
        ["CUST-ENT-011", "InsureCorp", "Enterprise", "130000", "Insurance", "40", "Michelle Lee", "Insurance"],
        ["CUST-ENT-012", "BankingPro", "Enterprise", "115000", "Financial Services", "32", "Robert Taylor", "Banking"],
        ["CUST-ENT-013", "MediaStream Co", "Enterprise", "100000", "Media", "26", "Jennifer Kim", "Streaming"],
        ["CUST-MID-005", "RegionalBank Co", "Mid-Market", "35000", "Financial Services", "15", "Alex Turner", "Banking"],
        ["CUST-MID-008", "TechStartup Pro", "Mid-Market", "25000", "Technology", "12", "Chris Lee", "Software"],
        ["CUST-MID-011", "LocalRetail Group", "Mid-Market", "30000", "Retail", "18", "Maria Garcia", "Retail"],
        ["CUST-MID-014", "HealthFirst Clinic", "Mid-Market", "28000", "Healthcare", "14", "Robert Kim", "Medical"],
        ["CUST-MID-017", "Shipping Express", "Mid-Market", "32000", "Logistics", "16", "Jennifer Wu", "Delivery"],
        ["CUST-MID-020", "CyberShield LLC", "Mid-Market", "27000", "Technology", "11", "Mark Thompson", "Security"],
        ["CUST-MID-023", "Learning Hub", "Mid-Market", "29000", "Education", "13", "Sofia Rodriguez", "Training"],
        ["CUST-MID-026", "CloudFirst", "Mid-Market", "33000", "Technology", "15", "Derek Zhang", "Cloud"],
        ["CUST-MID-029", "LogiTech Solutions", "Mid-Market", "31000", "Logistics", "17", "Amanda White", "Supply Chain"],
        ["CUST-MID-032", "MarketPro", "Mid-Market", "26000", "Marketing", "10", "Kevin Park", "Digital Marketing"],
        ["CUST-SMB-012", "SmallBiz Tools", "SMB", "5000", "Technology", "8", "Jake Martinez", "Software"],
        ["CUST-SMB-023", "LocalStore.com", "SMB", "3500", "Retail", "6", "Amy Chen", "E-commerce"],
        ["CUST-SMB-034", "QuickAccounting", "SMB", "4500", "Financial Services", "10", "Brian Johnson", "Accounting"],
        ["CUST-SMB-045", "MiniMart Chain", "SMB", "4000", "Retail", "7", "Carol White", "Retail"],
        ["CUST-SMB-056", "AppDev Studio", "SMB", "6000", "Technology", "9", "Dan Brown", "Mobile"],
        ["CUST-SMB-067", "HealthyLife App", "SMB", "3000", "Healthcare", "5", "Eva Green", "Wellness"],
        ["CUST-SMB-078", "EduApp Pro", "SMB", "3800", "Education", "6", "Frank Lee", "EdTech"],
        ["CUST-SMB-089", "LocalFinance", "SMB", "4200", "Financial Services", "8", "Grace Liu", "Finance"],
        ["CUST-SMB-095", "TechSupport Co", "SMB", "5500", "Technology", "11", "Henry Adams", "IT Services"]
    ]
    
    with open('customer_master.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(customer_data)
    print("✓ Created customer_master.csv")

def create_question_codes():
    """Create question_codes.json"""
    question_data = {
        "question_codes": {
            "General_Experience": {
                "full_text": "How can we improve your experience with X?",
                "category": "General",
                "weight": "high"
            },
            "Portal_Experience": {
                "full_text": "Thank you for your feedback! Please tell us how we can improve the customer platform Portal for you.",
                "category": "Product",
                "weight": "high"
            },
            "AM_Business_Review": {
                "full_text": "Please tell us about your Business Review experience with your Account Manager.",
                "category": "Relationship",
                "weight": "medium"
            },
            "Technical_Workshop": {
                "full_text": "Please share your feedback regarding these technical workshops",
                "category": "Training",
                "weight": "low"
            },
            "CSM_Review": {
                "full_text": "Please tell us about your review meeting experience with your Customer Success Manager.",
                "category": "Relationship",
                "weight": "high"
            },
            "Quoting_Ordering": {
                "full_text": "Is there anything else you would like to tell us about the X Quoting & Ordering process?",
                "category": "Sales Process",
                "weight": "medium"
            },
            "S_Feedback_general": {
                "full_text": "Is there anything else you would like to tell us about the X Service Delivery process or Service Delivery team?",
                "category": "Service",
                "weight": "high"
            },
            "P_Feedback_general": {
                "full_text": "Is there anything else you would like to tell us about your experience with the product?",
                "category": "Product",
                "weight": "high"
            },
            "SA_Feedback_general": {
                "full_text": "Is there anything else you would like to tell us about X Service Assurance team?",
                "category": "Support",
                "weight": "high"
            },
            "PM_Feedback_general": {
                "full_text": "Is there anything else you would like to tell us about the Planned Maintenance process?",
                "category": "Operations",
                "weight": "medium"
            },
            "BILL_Feedback_general": {
                "full_text": "Is there anything else you would like to tell us about your X Billing & Payment experience?",
                "category": "Billing",
                "weight": "high"
            }
        }
    }
    
    with open('question_codes.json', 'w', encoding='utf-8') as file:
        json.dump(question_data, file, indent=2)
    print("✓ Created question_codes.json")

def create_product_features():
    """Create product_features.md"""
    content = """# X Company Product Feature Ontology v2.3
Last Updated: 2024-01-10

## Core Platform

### Customer Portal
- **Aliases**: portal, dashboard, web portal, main interface, UI, customer platform
- **Description**: Main web interface for accessing all X platform features
- **Components**:
  - Dashboard widgets
  - Search functionality (Elasticsearch)
  - Report generation
  - User preferences
  - Mobile responsive views

### Authentication System
- **Aliases**: auth, login, signin, sign-in, SSO, SAML, 2FA, two-factor, authentication
- **Description**: User authentication and access control
- **Components**:
  - Single Sign-On (SSO/SAML)
  - Two-factor authentication (2FA)
  - SMS verification
  - Backup codes
  - Session management

## APIs

### Billing API
- **Aliases**: billing API, invoicing API, payment API, billing portal, invoice downloads
- **Description**: API for managing billing, invoices, and payments
- **Endpoints**:
  - /api/v3/invoices
  - /api/v3/invoice-batch
  - /api/v3/payment-methods
  - /api/v3/billing-history
- **Known Issues**: Performance degradation with batch operations >1000 items

### Core Product API
- **Aliases**: REST API, product API, main API, API v3
- **Description**: Core data access and manipulation APIs
- **Versions**: v1 (deprecated), v2 (legacy), v3 (current)
- **Rate Limits**: 1000 req/min for Enterprise, 100 req/min for others

## Service Modules

### Service Delivery
- **Aliases**: service delivery workflows, delivery automation, workflow engine, provisioning
- **Description**: Automated service provisioning and delivery
- **Features**:
  - Workflow designer
  - Approval chains
  - Automated provisioning
  - Progress tracking
  - SLA monitoring

### Quoting & Ordering
- **Aliases**: quoting tool, quote generator, ordering system, CPQ
- **Description**: Quote creation and order management
- **Features**:
  - Quote templates
  - Bulk operations
  - Approval workflows
  - Order tracking

## Support & Operations

### Service Assurance
- **Aliases**: SA team, service assurance, incident management, support tickets
- **Description**: Incident response and service quality assurance
- **SLAs**: 
  - Enterprise: 1hr response
  - Mid-Market: 4hr response
  - SMB: 24hr response

### Planned Maintenance
- **Aliases**: PM windows, maintenance windows, scheduled downtime
- **Description**: Scheduled system maintenance and updates
- **Schedule**: Monthly, typically Sunday 2-4 AM UTC
- **Communication**: 72hr advance notice required

## Teams

### Customer Success Manager (CSM)
- **Aliases**: CSM, success manager, customer success
- **Responsibilities**: Strategic guidance, quarterly reviews, escalations

### Account Manager (AM)
- **Aliases**: AM, account manager, business review
- **Responsibilities**: Commercial discussions, contract renewals, upsells

## Technical Resources

### Technical Workshops
- **Aliases**: training, workshops, technical training, API workshops
- **Format**: Virtual and in-person options
- **Topics**: API integration, Portal advanced features, Best practices

## Known Competitors
- CompetitorX: Market leader in enterprise solutions
- QuickFlow: Known for smooth service delivery  
- DataPro: Strong API performance
- CloudFirst: Modern UI/UX
"""
    
    with open('product_features.md', 'w', encoding='utf-8') as file:
        file.write(content)
    print("✓ Created product_features.md")

def create_golden_test_data():
    """Create golden_test_data.json"""
    test_data = {
        "test_cases": [
            {
                "survey_id": "TEST001",
                "question_code": "Portal_Experience",
                "response_text": "The portal is extremely slow during peak hours. We're losing productivity.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "low",
                    "features": ["customer portal"],
                    "issues": ["performance", "slow", "peak hours"],
                    "should_flag": True,
                    "flag_reasons": ["low_score", "performance_issue", "enterprise_tier", "productivity_impact"]
                }
            },
            {
                "survey_id": "TEST002", 
                "question_code": "P_Feedback_general",
                "response_text": "Love the new dashboard features! The real-time analytics are exactly what we needed.",
                "customer_tier": "Mid-Market",
                "expected": {
                    "sentiment": "positive",
                    "score_band": "high",
                    "features": ["customer portal", "dashboard widgets"],
                    "issues": [],
                    "should_flag": False,
                    "flag_reasons": []
                }
            },
            {
                "survey_id": "TEST003",
                "question_code": "BILL_Feedback_general",
                "response_text": "Billing API broke again. Third time this month. Invoice downloads fail constantly.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "low",
                    "features": ["billing api", "invoice downloads"],
                    "issues": ["outage", "reliability", "recurring_issue"],
                    "should_flag": True,
                    "flag_reasons": ["low_score", "recurring_issue", "api_failure", "enterprise_tier"]
                }
            },
            {
                "survey_id": "TEST004",
                "question_code": "S_Feedback_general",
                "response_text": "CompetitorX has a much smoother process for service delivery. Too many manual steps here.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "medium",
                    "features": ["service delivery"],
                    "issues": ["manual_process", "efficiency"],
                    "competitors_mentioned": ["CompetitorX"],
                    "should_flag": True,
                    "flag_reasons": ["competitor_comparison", "enterprise_tier", "process_inefficiency"]
                }
            },
            {
                "survey_id": "TEST005",
                "question_code": "Portal_Experience",
                "response_text": "SAML integration keeps failing without clear error messages. Affecting 200+ users.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "low",
                    "features": ["authentication system", "sso"],
                    "issues": ["integration_failure", "error_handling", "user_impact"],
                    "should_flag": True,
                    "flag_reasons": ["technical_issue", "auth_problem", "large_user_impact", "enterprise_tier"]
                }
            },
            {
                "survey_id": "TEST006",
                "question_code": "CSM_Review",
                "response_text": "CSM is overloaded. Response time degraded from hours to days. Need more support.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "low",
                    "features": ["customer success manager"],
                    "issues": ["response_time", "support_capacity"],
                    "should_flag": True,
                    "flag_reasons": ["relationship_risk", "support_degradation", "enterprise_tier"]
                }
            },
            {
                "survey_id": "TEST007",
                "question_code": "SA_Feedback_general",
                "response_text": "Complete outage last night cost us $50K. No proactive communication.",
                "customer_tier": "Enterprise",
                "expected": {
                    "sentiment": "negative",
                    "score_band": "very_low",
                    "features": ["service assurance"],
                    "issues": ["outage", "communication", "revenue_impact"],
                    "revenue_impact": 50000,
                    "should_flag": True,
                    "flag_reasons": ["critical_outage", "revenue_loss", "communication_failure", "enterprise_tier"]
                }
            }
        ]
    }
    
    with open('golden_test_data.json', 'w', encoding='utf-8') as file:
        json.dump(test_data, file, indent=2)
    print("✓ Created golden_test_data.json")

def create_alert_rules():
    """Create alert_rules.json"""
    alert_data = {
        "alert_rules": [
            {
                "rule_id": "R001",
                "name": "Enterprise Low Score Alert",
                "conditions": {
                    "customer_tier": ["Enterprise"],
                    "score_band": ["low", "very_low"]
                },
                "actions": ["email_csm", "slack_urgent", "create_ticket"],
                "priority": "P1"
            },
            {
                "rule_id": "R002", 
                "name": "Revenue Impact Alert",
                "conditions": {
                    "revenue_impact": {">": 10000}
                },
                "actions": ["email_csm", "email_am", "slack_executive", "create_incident"],
                "priority": "P0"
            },
            {
                "rule_id": "R003",
                "name": "Competitor Mention Alert",
                "conditions": {
                    "competitors_mentioned": {"exists": True},
                    "customer_tier": ["Enterprise", "Mid-Market"]
                },
                "actions": ["email_csm", "slack_competitive"],
                "priority": "P2"
            },
            {
                "rule_id": "R004",
                "name": "Recurring Issue Alert",
                "conditions": {
                    "issues": {"contains": "recurring_issue"},
                    "customer_tier": ["Enterprise"]
                },
                "actions": ["email_csm", "create_escalation"],
                "priority": "P1"
            },
            {
                "rule_id": "R005",
                "name": "Portal Performance Alert",
                "conditions": {
                    "features": {"contains": "customer portal"},
                    "issues": {"contains_any": ["slow", "performance", "timeout"]},
                    "score_band": ["low", "medium"]
                },
                "actions": ["aggregate_similar", "email_product_team"],
                "priority": "P2"
            }
        ]
    }
    
    with open('alert_rules.json', 'w', encoding='utf-8') as file:
        json.dump(alert_data, file, indent=2)
    print("✓ Created alert_rules.json")

def main():
    """Generate all files"""
    print("Survey Sentinel Sample Data Generator")
    print("=====================================")
    
    # Create directory if it doesn't exist
    os.makedirs('survey_data', exist_ok=True)
    os.chdir('survey_data')
    
    # Generate all files
    create_survey_responses()
    create_customer_master()
    create_question_codes()
    create_product_features()
    create_golden_test_data()
    create_alert_rules()
    
    print("\n🎉 All files created successfully!")
    print(f"Files generated in: {os.getcwd()}")
    print("\nFiles created:")
    print("- survey_responses.csv")
    print("- customer_master.csv") 
    print("- question_codes.json")
    print("- product_features.md")
    print("- golden_test_data.json")
    print("- alert_rules.json")

if __name__ == "__main__":
    main()