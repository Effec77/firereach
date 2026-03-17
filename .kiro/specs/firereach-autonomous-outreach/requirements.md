# Requirements Document

## Introduction

FireReach is a comprehensive autonomous outreach engine that automates the complete SDR (Sales Development Representative) workflow from prospect discovery to personalized email delivery. The system implements a 6-stage pipeline that discovers companies matching an Ideal Customer Profile (ICP), harvests buying signals, researches prospects, generates personalized content, and sends targeted outreach emails with PDF attachments.

The system addresses the core challenge of scaling personalized B2B outreach by combining real-time company discovery, multi-source signal harvesting, AI-powered research analysis, and automated email generation. Built with FastAPI backend and modern SaaS frontend, it supports tiered plans (Free: 3 companies, Pro: 10, Enterprise: 25) and integrates with multiple data sources including Tavily API, Apollo.io, Hunter.io, and LinkedIn scraping.

## Glossary

- **System**: The FireReach autonomous outreach engine
- **ICP**: Ideal Customer Profile - description of target customer characteristics
- **Campaign**: A discovery session for a specific ICP and plan tier
- **Prospect**: A discovered company with harvested signals and contact information
- **Signal**: Buying signal indicating company readiness for outreach (S1-S6 types)
- **Agent_Controller**: Main orchestration component managing the 6-stage pipeline
- **Company_Discoverer**: Component responsible for multi-source company discovery
- **Signal_Harvester**: Component that harvests and verifies S1-S6 buying signals
- **Research_Analyst**: Component that generates targeted account briefs using LLM
- **Email_Sender**: Component that generates and sends personalized outreach emails
- **PDF_Generator**: Component that creates professional prospect one-pagers
- **Plan_Tier**: Subscription level determining company discovery limits (free/pro/enterprise)
- **Contact_Discovery**: Multi-source process to find prospect contact information
- **Tavily_API**: Real-time search API for company discovery and signal harvesting
- **Apollo_API**: Professional contact database API
- **Hunter_API**: Email finder and verification API
- **Resend_API**: Email delivery service API
- **Groq_LLM**: Language model API for research analysis and email generation

## Requirements

### Requirement 1: Campaign Management

**User Story:** As a user, I want to create and manage outreach campaigns based on my ICP, so that I can organize my prospecting efforts by target customer profile.

#### Acceptance Criteria

1. WHEN a user submits an ICP and plan tier, THE System SHALL create a new campaign with unique identifier
2. THE System SHALL enforce plan tier limits (free: 3, pro: 10, enterprise: 25 companies)
3. WHEN a campaign is created, THE System SHALL initialize status as "discovering"
4. THE System SHALL track campaign metrics (companies found, approved, sent)
5. WHEN campaign processing completes successfully, THE System SHALL update status to "awaiting_approval"
6. IF campaign processing fails, THEN THE System SHALL update status to "failed" with error message

### Requirement 2: Multi-Source Company Discovery

**User Story:** As a user, I want the system to discover real companies matching my ICP from multiple data sources, so that I can reach actual prospects rather than mock data.

#### Acceptance Criteria

1. WHEN discovering companies, THE Company_Discoverer SHALL query Tavily API for recent company news and funding
2. THE Company_Discoverer SHALL scrape startup directories (AngelList, Crunchbase, Y Combinator)
3. THE Company_Discoverer SHALL search LinkedIn for companies matching ICP criteria
4. THE Company_Discoverer SHALL remove duplicate companies based on name similarity
5. THE Company_Discoverer SHALL filter results for ICP relevance using keyword matching
6. THE Company_Discoverer SHALL return maximum companies per plan tier limit
7. IF no companies are found, THEN THE Company_Discoverer SHALL return empty list with appropriate logging

### Requirement 3: Signal Harvesting and Verification

**User Story:** As a user, I want the system to harvest and verify buying signals for each discovered company, so that I can prioritize outreach based on signal strength and confidence.

#### Acceptance Criteria

1. THE Signal_Harvester SHALL search for S1-S6 signal types using Tavily API
2. WHEN a signal is found, THE Signal_Harvester SHALL extract first sentence as signal text
3. THE Signal_Harvester SHALL verify each signal with second independent search
4. IF signal is corroborated by different source, THEN THE Signal_Harvester SHALL mark confidence as "HIGH"
5. IF signal has single source only, THEN THE Signal_Harvester SHALL mark confidence as "MEDIUM"
6. THE Signal_Harvester SHALL filter signals to include only HIGH and MEDIUM confidence
7. THE Signal_Harvester SHALL return maximum 5 highest-scoring signals per company
8. THE Signal_Harvester SHALL calculate total signal score with maximum of 100 points
9. THE Signal_Harvester SHALL determine target designation from highest-scoring signal type

### Requirement 4: Multi-Source Contact Discovery

**User Story:** As a user, I want the system to find valid contact information for prospects using multiple sources, so that I can reach the right person at each target company.

#### Acceptance Criteria

1. THE Signal_Harvester SHALL attempt contact discovery via Apollo API first
2. IF Apollo fails to find contact, THEN THE Signal_Harvester SHALL try Hunter API
3. IF Hunter fails to find contact, THEN THE Signal_Harvester SHALL try LinkedIn scraping
4. IF LinkedIn fails to find contact, THEN THE Signal_Harvester SHALL try website scraping
5. IF all methods fail, THEN THE Signal_Harvester SHALL return empty contact with source "not_found"
6. WHEN contact is found, THE Signal_Harvester SHALL validate email format if present
7. THE Signal_Harvester SHALL attribute contact source accurately (apollo/hunter/linkedin_scraping/website_scraping)
8. THE Signal_Harvester SHALL include contact name, email, title, LinkedIn URL, and phone when available

### Requirement 5: Research Analysis and Account Brief Generation

**User Story:** As a user, I want the system to generate targeted account briefs using verified signals, so that I can understand each prospect's context and pain points.

#### Acceptance Criteria

1. WHEN generating account brief, THE Research_Analyst SHALL use Groq LLM with company signals and ICP
2. THE Research_Analyst SHALL generate exactly 2 paragraphs in professional GTM analyst tone
3. THE Research_Analyst SHALL focus paragraph 1 on growth signals and strategic direction
4. THE Research_Analyst SHALL focus paragraph 2 on ICP alignment and pain points
5. THE Research_Analyst SHALL reference specific signals in the analysis
6. THE Research_Analyst SHALL maintain consistent terminology from glossary
7. IF LLM request fails, THEN THE Research_Analyst SHALL return error with fallback message

### Requirement 6: Email Generation and Delivery

**User Story:** As a user, I want the system to generate personalized outreach emails and send them via reliable email service, so that I can automate my outreach while maintaining personalization.

#### Acceptance Criteria

1. THE Email_Sender SHALL generate personalized email using Groq LLM with account brief and signals
2. THE Email_Sender SHALL reference at least 2 specific signals in email content
3. THE Email_Sender SHALL create professional subject line relevant to prospect
4. THE Email_Sender SHALL send email via Resend API with PDF attachment if available
5. WHEN email is sent successfully, THE Email_Sender SHALL return status "sent"
6. IF email delivery fails, THEN THE Email_Sender SHALL return status "failed" with error details
7. THE Email_Sender SHALL include unsubscribe link in all outreach emails
8. THE Email_Sender SHALL validate recipient email format before sending

### Requirement 7: PDF Generation

**User Story:** As a user, I want the system to generate professional PDF one-pagers for prospects, so that I can provide valuable content attachments in my outreach.

#### Acceptance Criteria

1. THE PDF_Generator SHALL create professional PDF layout with company information
2. THE PDF_Generator SHALL include contact details and signal visualization
3. THE PDF_Generator SHALL format account brief content in readable layout
4. THE PDF_Generator SHALL return file path for email attachment
5. IF PDF generation fails, THEN THE PDF_Generator SHALL log error and return empty path
6. THE PDF_Generator SHALL clean up temporary files after email sending

### Requirement 8: Database Persistence and State Management

**User Story:** As a system administrator, I want all campaign and prospect data to be reliably persisted, so that the system maintains state across requests and provides audit trails.

#### Acceptance Criteria

1. THE System SHALL persist all campaigns with unique identifiers and timestamps
2. THE System SHALL persist all prospects with complete signal and contact data
3. THE System SHALL maintain referential integrity between campaigns and prospects
4. THE System SHALL cache signal data for 24 hours to reduce API calls
5. THE System SHALL track prospect approval status and outreach results
6. THE System SHALL provide campaign history and metrics retrieval
7. THE System SHALL handle database connection failures gracefully

### Requirement 9: API Integration and Error Handling

**User Story:** As a system administrator, I want robust API integration with proper error handling, so that external service failures don't crash the system.

#### Acceptance Criteria

1. THE System SHALL implement exponential backoff for API rate limiting
2. WHEN external API is unavailable, THE System SHALL log error and continue processing
3. THE System SHALL validate API responses before processing data
4. THE System SHALL handle network timeouts gracefully with appropriate retries
5. THE System SHALL cache successful API responses to reduce redundant calls
6. IF critical API fails, THEN THE System SHALL provide fallback functionality where possible
7. THE System SHALL maintain API key security through environment variables

### Requirement 10: Plan Tier Enforcement and Limits

**User Story:** As a business owner, I want the system to enforce subscription plan limits, so that usage aligns with pricing tiers and prevents abuse.

#### Acceptance Criteria

1. THE System SHALL enforce company discovery limits per plan tier (free: 3, pro: 10, enterprise: 25)
2. THE System SHALL validate plan tier parameter against allowed values
3. THE System SHALL prevent campaign creation if plan tier is invalid
4. THE System SHALL track usage against plan limits in real-time
5. WHEN plan limit is reached, THE System SHALL stop discovery and update campaign status
6. THE System SHALL provide clear error messages when limits are exceeded

### Requirement 11: Frontend Interface and User Experience

**User Story:** As a user, I want an intuitive web interface to manage campaigns and review prospects, so that I can efficiently operate the outreach system.

#### Acceptance Criteria

1. THE System SHALL provide web interface for ICP input and plan tier selection
2. THE System SHALL display discovered prospects with signals and scores for approval
3. THE System SHALL show prospect details including contact information and account brief
4. THE System SHALL display generated emails and delivery status
5. THE System SHALL provide campaign history and sent email tracking
6. THE System SHALL handle loading states and error messages appropriately
7. THE System SHALL be responsive across desktop and mobile devices

### Requirement 12: Security and Data Privacy

**User Story:** As a data protection officer, I want the system to handle personal data securely and comply with privacy regulations, so that we maintain customer trust and legal compliance.

#### Acceptance Criteria

1. THE System SHALL store API keys securely in environment variables only
2. THE System SHALL not log sensitive personal information in application logs
3. THE System SHALL implement secure email authentication (SPF/DKIM)
4. THE System SHALL provide data deletion capabilities for GDPR compliance
5. THE System SHALL validate and sanitize all user inputs to prevent injection attacks
6. THE System SHALL use HTTPS for all external API communications
7. THE System SHALL implement rate limiting to prevent spam and abuse

### Requirement 13: Performance and Scalability

**User Story:** As a system administrator, I want the system to perform efficiently under load, so that users experience fast response times and reliable service.

#### Acceptance Criteria

1. THE System SHALL process company discovery in parallel where possible
2. THE System SHALL implement database connection pooling for concurrent requests
3. THE System SHALL cache frequently accessed data with appropriate TTL
4. THE System SHALL optimize database queries with proper indexing
5. THE System SHALL stream PDF generation for large documents
6. THE System SHALL clean up temporary files and manage memory efficiently
7. THE System SHALL complete full discovery pipeline within 60 seconds for free tier

### Requirement 14: Deployment and Configuration Management

**User Story:** As a DevOps engineer, I want clear deployment procedures and configuration management, so that I can reliably deploy and maintain the system in production.

#### Acceptance Criteria

1. THE System SHALL provide complete deployment instructions for Render and Vercel
2. THE System SHALL use environment variables for all configuration settings
3. THE System SHALL include health check endpoints for monitoring
4. THE System SHALL provide database initialization and migration scripts
5. THE System SHALL include comprehensive error logging for troubleshooting
6. THE System SHALL support both development and production configurations
7. THE System SHALL include dependency management with version pinning

### Requirement 15: Testing and Quality Assurance

**User Story:** As a quality assurance engineer, I want comprehensive testing coverage, so that I can ensure system reliability and catch regressions early.

#### Acceptance Criteria

1. THE System SHALL include unit tests for all core business logic components
2. THE System SHALL include integration tests for external API interactions
3. THE System SHALL include end-to-end tests for complete pipeline workflows
4. THE System SHALL achieve minimum 90% code coverage for critical components
5. THE System SHALL include property-based tests for data validation functions
6. THE System SHALL include mock implementations for external service testing
7. THE System SHALL include performance tests for pipeline execution timing