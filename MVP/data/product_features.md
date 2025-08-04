# X Company Product Feature Ontology v2.3
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
