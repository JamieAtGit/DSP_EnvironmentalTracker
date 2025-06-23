# Use Cases Documentation

## Overview
This document outlines the comprehensive use cases for the Carbon Footprint Tracking System, detailing interactions between different actors and the system components.

## Primary Actors

### 1. End User (Consumer)
- Individual shoppers using the browser extension
- Environmentally conscious consumers seeking carbon footprint information
- General public interested in sustainability metrics

### 2. System Administrator
- Technical personnel managing the system infrastructure
- Data scientists maintaining ML models
- DevOps engineers handling deployments

### 3. Data Analyst
- Researchers analyzing carbon footprint trends
- Business intelligence professionals
- Environmental researchers

### 4. External Systems
- Amazon product pages (data source)
- Environmental databases (reference data)
- Third-party APIs (brand origin data)

## Core Use Cases

### UC-001: Browser Extension Product Analysis

**Primary Actor**: End User  
**Goal**: Obtain carbon footprint information for a product while browsing Amazon  
**Preconditions**: 
- Browser extension installed and enabled
- User is on an Amazon product page
- Internet connection available

**Main Success Scenario**:
1. User navigates to Amazon product page
2. Extension automatically detects product information
3. System extracts product details (name, brand, material, weight)
4. System enriches data with brand origin and transport information
5. ML model predicts carbon footprint
6. Extension displays tooltip with carbon footprint estimate
7. User can view detailed breakdown by clicking tooltip
8. User optionally provides feedback on prediction accuracy

**Alternative Flows**:
- **3a**: Product information incomplete
  - 3a1: System prompts user for missing information
  - 3a2: User provides additional details
  - 3a3: System continues with enhanced data
- **5a**: ML model unavailable
  - 5a1: System falls back to rule-based calculation
  - 5a2: Display prediction with lower confidence indicator
- **6a**: Extension blocked by page security
  - 6a1: Display notification to user
  - 6a2: Provide alternative manual input option

**Postconditions**:
- Carbon footprint information displayed to user
- Interaction logged for system improvement
- Optional user feedback collected

---

### UC-002: Manual Product Carbon Footprint Prediction

**Primary Actor**: End User  
**Goal**: Get carbon footprint prediction for any product via web interface  
**Preconditions**: 
- User has access to web application
- User account created (optional for basic usage)

**Main Success Scenario**:
1. User accesses web application prediction form
2. User enters product details:
   - Product name
   - Material composition
   - Weight
   - Brand/manufacturer
   - Country of origin (if known)
3. System validates input data
4. System processes data through ML pipeline
5. System returns carbon footprint prediction with:
   - Total CO₂ equivalent
   - Confidence level
   - Breakdown by factors (material, transport, manufacturing)
   - Comparison to similar products
6. User can save prediction to personal dashboard
7. User can export results (PDF/CSV)

**Alternative Flows**:
- **3a**: Validation errors
  - 3a1: System highlights invalid fields
  - 3a2: User corrects information
  - 3a3: Continue with validation
- **4a**: Prediction confidence too low
  - 4a1: System requests additional information
  - 4a2: User provides more details
  - 4a3: Re-run prediction with enhanced data

**Postconditions**:
- Prediction results available to user
- Data stored for model improvement
- Optional personal dashboard updated

---

### UC-003: Batch Product Analysis

**Primary Actor**: Data Analyst  
**Goal**: Analyze carbon footprints for multiple products simultaneously  
**Preconditions**: 
- Analyst has appropriate system access
- Product data available in CSV format
- Sufficient system resources for batch processing

**Main Success Scenario**:
1. Analyst logs into admin interface
2. Analyst uploads CSV file with product data
3. System validates file format and data structure
4. System processes products in batches
5. For each product:
   - Extract and enhance features
   - Generate carbon footprint prediction
   - Calculate confidence metrics
6. System generates comprehensive report including:
   - Individual product predictions
   - Aggregate statistics
   - Distribution analysis
   - Outlier identification
7. Analyst downloads results and visualizations

**Alternative Flows**:
- **3a**: File format invalid
  - 3a1: System provides error details and template
  - 3a2: Analyst corrects file and re-uploads
- **4a**: Processing fails for some products
  - 4a1: System continues with valid products
  - 4a2: Generate error report for failed items
  - 4a3: Provide suggestions for data correction

**Postconditions**:
- Batch analysis results available
- System performance metrics updated
- Error logs generated for troubleshooting

---

### UC-004: Model Training and Deployment

**Primary Actor**: System Administrator  
**Goal**: Update ML model with new training data and deploy to production  
**Preconditions**: 
- New training data available
- Model training environment prepared
- Deployment pipeline configured

**Main Success Scenario**:
1. Administrator initiates model training workflow
2. System loads latest training dataset
3. System performs data preprocessing and feature engineering
4. System trains new XGBoost model with hyperparameter optimization
5. System evaluates model performance against test set
6. System generates performance metrics and validation report
7. If performance meets criteria:
   - Administrator approves model for deployment
   - System creates model deployment package
   - System deploys to staging environment
   - System runs integration tests
   - Administrator promotes to production
8. System updates model version and monitoring

**Alternative Flows**:
- **5a**: Model performance below threshold
  - 5a1: System alerts administrator
  - 5a2: Administrator reviews training data and parameters
  - 5a3: Adjust training configuration and retry
- **8a**: Deployment tests fail
  - 8a1: System rollback to previous model version
  - 8a2: Alert administrator with failure details
  - 8a3: Administrator investigates and resolves issues

**Postconditions**:
- New model deployed to production
- Model performance baseline established
- Monitoring alerts configured

---

### UC-005: User Feedback Integration

**Primary Actor**: End User  
**Goal**: Provide feedback on prediction accuracy to improve system  
**Preconditions**: 
- User has received a carbon footprint prediction
- Feedback mechanism available

**Main Success Scenario**:
1. User views carbon footprint prediction
2. User clicks feedback option
3. System presents feedback form:
   - Accuracy rating (1-5 stars)
   - Prediction too high/low/about right
   - Additional comments
   - Actual carbon footprint (if known)
4. User submits feedback
5. System validates and stores feedback
6. System links feedback to original prediction
7. System updates user's feedback history
8. System queues data for model retraining

**Alternative Flows**:
- **4a**: User provides actual carbon footprint
  - 4a1: System calculates prediction error
  - 4a2: Flag for high-priority model improvement
- **5a**: Spam/invalid feedback detected
  - 5a1: System flags for manual review
  - 5a2: Apply content filtering

**Postconditions**:
- Feedback stored in system
- Model improvement queue updated
- User engagement metrics updated

---

### UC-006: System Health Monitoring

**Primary Actor**: System Administrator  
**Goal**: Monitor system performance and health metrics  
**Preconditions**: 
- Monitoring infrastructure deployed
- Administrator has monitoring dashboard access

**Main Success Scenario**:
1. Administrator accesses monitoring dashboard
2. System displays real-time metrics:
   - API response times
   - Prediction accuracy trends
   - System resource utilization
   - Error rates and types
   - User engagement statistics
3. Administrator reviews performance indicators
4. System alerts on anomalies or threshold breaches
5. Administrator investigates alerts and takes corrective action
6. System logs administrative actions

**Alternative Flows**:
- **4a**: Critical system alert triggered
  - 4a1: System sends immediate notification
  - 4a2: Administrator escalates to on-call team
  - 4a3: Implement emergency response procedures
- **5a**: Performance degradation detected
  - 5a1: Administrator analyzes root cause
  - 5a2: Implement scaling or optimization measures
  - 5a3: Monitor improvement

**Postconditions**:
- System health status confirmed
- Issues resolved or escalated
- Performance trends documented

## Secondary Use Cases

### UC-007: Data Export and Reporting
**Goal**: Export system data for external analysis  
**Actors**: Data Analyst, Researcher  
**Key Functions**: Data extraction, format conversion, privacy compliance

### UC-008: User Account Management
**Goal**: Manage user registration, authentication, and preferences  
**Actors**: End User, System Administrator  
**Key Functions**: Registration, login, profile management, access control

### UC-009: API Integration
**Goal**: Provide third-party access to carbon footprint predictions  
**Actors**: External Developers, Partner Systems  
**Key Functions**: API authentication, rate limiting, response formatting

### UC-010: Educational Content Delivery
**Goal**: Provide users with educational information about carbon footprints  
**Actors**: End User, Content Administrator  
**Key Functions**: Content management, user engagement tracking

## Use Case Relationships

### Include Relationships
- UC-001, UC-002 include "Validate Input Data"
- UC-001, UC-002 include "Generate Prediction"
- UC-003 includes "Batch Process Products"
- All use cases include "Log User Interaction"

### Extend Relationships
- "Handle Prediction Errors" extends UC-001, UC-002
- "Provide Alternative Calculations" extends UC-001, UC-002
- "Send Notifications" extends UC-004, UC-006

### Generalization Relationships
- UC-001, UC-002 are specializations of "Product Analysis"
- UC-004, UC-006 are specializations of "System Administration"

## Traceability Matrix

| Requirement ID | Use Case | Priority | Status |
|---------------|----------|----------|---------|
| REQ-001 | UC-001 | High | Implemented |
| REQ-002 | UC-002 | High | Implemented |
| REQ-003 | UC-003 | Medium | Implemented |
| REQ-004 | UC-004 | High | Implemented |
| REQ-005 | UC-005 | Medium | Partially Implemented |
| REQ-006 | UC-006 | High | Implemented |
| REQ-007 | UC-007 | Low | Planned |
| REQ-008 | UC-008 | Medium | Implemented |
| REQ-009 | UC-009 | Low | Planned |
| REQ-010 | UC-010 | Low | Planned |