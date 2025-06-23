# System Flowcharts

## Overview
This document presents comprehensive flowcharts illustrating the data flow, decision processes, and system interactions within the Carbon Footprint Tracking System.

## 1. High-Level System Architecture Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CARBON FOOTPRINT TRACKING SYSTEM                          │
│                               High-Level Architecture Flow                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │   USER      │         │ EXTENSION   │         │ WEB APP     │
    │ (Browser)   │◄────────┤ (Chrome/    │◄────────┤ (React)     │
    │             │         │ Firefox)    │         │             │
    └─────────────┘         └─────────────┘         └─────────────┘
            │                       │                       │
            │                       │                       │
            ▼                       ▼                       ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    API GATEWAY                                   │
    │           (Authentication & Rate Limiting)                       │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                BACKEND API SERVICES                              │
    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
    │  │ Prediction  │  │    Data     │  │    User     │              │
    │  │  Service    │  │ Processing  │  │ Management  │              │
    │  │             │  │   Service   │  │   Service   │              │
    │  └─────────────┘  └─────────────┘  └─────────────┘              │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
    ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
    │   ML PIPELINE   │  │    DATABASE     │  │ EXTERNAL APIs   │
    │                 │  │                 │  │                 │
    │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
    │ │   XGBoost   │ │  │ │ PostgreSQL  │ │  │ │   Amazon    │ │
    │ │   Model     │ │  │ │   Primary   │ │  │ │   Product   │ │
    │ │             │ │  │ │   Database  │ │  │ │     API     │ │
    │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
    │                 │  │                 │  │                 │
    │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │
    │ │ Rule-Based  │ │  │ │    Redis    │ │  │ │   Material  │ │
    │ │  Fallback   │ │  │ │    Cache    │ │  │ │  Database   │ │
    │ │             │ │  │ │             │ │  │ │             │ │
    │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │
    └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 2. Browser Extension Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         BROWSER EXTENSION WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

START: User navigates to Amazon product page
    │
    ▼
┌─────────────────────────┐
│  Content Script Loads   │
│  and Detects Page Type  │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │     Not Product Page    │
│   Is Product Page?      ├─┤         Exit           │
└─────────────────────────┘ └─────────────────────────┘
    │ Yes
    ▼
┌─────────────────────────┐
│  Extract Product Data   │
│  • Product Name        │
│  • Brand               │
│  • Price               │
│  • Images              │
│  • Specifications      │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Validate Extracted    │
│       Data             │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │   Data Incomplete?      │
│  Data Complete?         ├─┤   Show Manual Input     │
└─────────────────────────┘ │       Form             │
    │ Yes                   └─────────────────────────┘
    ▼                               │
┌─────────────────────────┐         │
│  Send Data to Backend   │◄────────┘
│      API Endpoint      │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Process API Request   │
│   • Authenticate       │
│   • Validate Input     │
│   • Rate Limit Check   │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │      API Error?         │
│    API Success?         ├─┤   Show Error Message    │
└─────────────────────────┘ │   & Retry Option        │
    │ Yes                   └─────────────────────────┘
    ▼
┌─────────────────────────┐
│  Receive Prediction     │
│  • Carbon Footprint    │
│  • Confidence Level    │
│  • Breakdown Data      │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Inject Tooltip UI     │
│   into Product Page     │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Display Carbon Data    │
│  with Visual Indicator  │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   User Interactions     │
│  • View Details        │
│  • Provide Feedback    │
│  • Share Results       │
└─────────────────────────┘
    │
    ▼
END: Data displayed to user
```

## 3. Machine Learning Prediction Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                          ML PREDICTION PIPELINE                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

START: Prediction request received
    │
    ▼
┌─────────────────────────┐
│   Input Validation      │
│  • Required fields     │
│  • Data types          │
│  • Value ranges        │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │   Validation Failed?    │
│   Data Valid?           ├─┤   Return Error with     │
└─────────────────────────┘ │   Specific Messages     │
    │ Yes                   └─────────────────────────┘
    ▼
┌─────────────────────────┐
│   Data Enrichment       │
│  • Brand Origin Lookup │
│  • Material Classification│
│  • Transport Method    │
│  • Weight Normalization │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Feature Engineering   │
│  • Encode Categorical  │
│  • Scale Numerical     │
│  • Create Interactions │
│  • Handle Missing      │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Load ML Model         │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │    Model Load Failed?   │
│   Model Available?      ├─┤   Switch to Rule-Based  │
└─────────────────────────┘ │      Calculation        │
    │ Yes                   └─────────────────────────┘
    ▼                               │
┌─────────────────────────┐         │
│  XGBoost Prediction     │         │
│  • Feature Importance  │         │
│  • Confidence Score    │         │
│  • Prediction Value    │         │
└─────────────────────────┘         │
    │                              │
    ▼                              ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│   Post-Processing       │ │   Rule-Based Fallback   │
│  • Scale to CO2 equiv   │ │  • Material factors     │
│  • Calculate breakdown  │ │  • Weight multiplication │
│  • Confidence adjust   │ │  • Transport addition   │
└─────────────────────────┘ └─────────────────────────┘
    │                              │
    └──────────────┬───────────────┘
                   ▼
┌─────────────────────────┐
│   Format Response       │
│  • JSON structure      │
│  • Error handling      │
│  • Metadata inclusion  │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Log Prediction        │
│  • Database storage    │
│  • Analytics tracking  │
│  • Performance metrics │
└─────────────────────────┘
    │
    ▼
END: Return prediction to client
```

## 4. Data Processing Workflow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DATA PROCESSING WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

START: Raw product data input
    │
    ▼
┌─────────────────────────┐
│   Data Ingestion        │
│  • API endpoints       │
│  • File uploads        │
│  • Web scraping        │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Initial Validation    │
│  • Schema compliance   │
│  • Required fields     │
│  • Basic sanitization  │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │   Validation Errors?    │
│   Validation Passed?    ├─┤   Log & Queue for       │
└─────────────────────────┘ │   Manual Review         │
    │ Yes                   └─────────────────────────┘
    ▼
┌─────────────────────────┐
│   Data Cleaning         │
│  • Remove duplicates   │
│  • Fix encoding issues │
│  • Standardize formats │
│  • Handle missing vals │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Data Enhancement      │
│  • Brand origin lookup │
│  • Material inference  │
│  • Category mapping    │
│  • Weight extraction   │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Quality Assessment    │
│  • Completeness score  │
│  • Confidence rating   │
│  • Data consistency    │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │   Quality Too Low?      │
│   Quality Acceptable?   ├─┤   Flag for Human        │
└─────────────────────────┘ │      Review            │
    │ Yes                   └─────────────────────────┘
    ▼
┌─────────────────────────┐
│   Feature Extraction    │
│  • Text processing     │
│  • Numerical features  │
│  • Categorical encoding│
│  • Derived features    │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Storage Preparation   │
│  • Final validation    │
│  • Metadata addition   │
│  • Indexing tags       │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Database Storage      │
│  • Primary tables      │
│  • Search indexes      │
│  • Audit logs          │
└─────────────────────────┘
    │
    ▼
END: Clean data ready for ML pipeline
```

## 5. User Authentication Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           USER AUTHENTICATION FLOW                                  │
└─────────────────────────────────────────────────────────────────────────────────────┘

START: User accesses protected resource
    │
    ▼
┌─────────────────────────┐
│   Check for Token       │
│   in Request Headers    │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │    No Token Present?    │
│   Token Present?        ├─┤   Redirect to Login     │
└─────────────────────────┘ │         Page           │
    │ Yes                   └─────────────────────────┘
    ▼                               │
┌─────────────────────────┐         │
│   Validate Token        │         │
│  • Check signature      │         │
│  • Verify expiration    │         │
│  • Validate issuer      │         │
└─────────────────────────┘         │
    │                              │
    ▼                              ▼
┌─────────────────────────┐ ┌─────────────────────────┐
│   Token Valid?          │ │   LOGIN PROCESS         │
└─────────────────────────┘ │                        │
    │ Yes                   │ User enters credentials │
    ▼                       │         │               │
┌─────────────────────────┐ │         ▼               │
│   Extract User Info     │ │ ┌─────────────────────┐ │
│   from Token Payload    │ │ │  Validate Creds     │ │
└─────────────────────────┘ │ │  • Username/Email   │ │
    │                       │ │  • Password Hash    │ │
    ▼                       │ │  • Account Status   │ │
┌─────────────────────────┐ │ └─────────────────────┘ │
│   Check User Status     │ │         │               │
│  • Account active      │ │         ▼               │
│  • Permissions         │ │ ┌─────────────────────┐ │
│  • Rate limits         │ │ │   Credentials       │ │
└─────────────────────────┘ │ │      Valid?         │ │
    │                       │ └─────────────────────┘ │
    ▼                       │         │ Yes           │
┌─────────────────────────┐ │         ▼               │
│   Authorize Request     │ │ ┌─────────────────────┐ │
│  • Resource access     │ │ │  Generate JWT Token │ │
│  • Operation permitted │ │ │  • User claims      │ │
└─────────────────────────┘ │ │  • Expiration time  │ │
    │                       │ │  • Digital signature│ │
    ▼                       │ └─────────────────────┘ │
┌─────────────────────────┐ │         │               │
│   Grant Access to       │ │         ▼               │
│   Protected Resource    │ │ ┌─────────────────────┐ │
└─────────────────────────┘ │ │  Set Response       │ │
    │                       │ │  • Token in header  │ │
    ▼                       │ │  • User info        │ │
END: User authenticated      │ │  • Redirect URL     │ │
                            │ └─────────────────────┘ │
                            └─────────────────────────┘
                                      │
                                      ▼
                              END: User logged in
```

## 6. Error Handling and Recovery Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        ERROR HANDLING & RECOVERY FLOW                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

START: System operation or request
    │
    ▼
┌─────────────────────────┐
│   Execute Operation     │
│   (API call, DB query,  │
│    ML prediction, etc.) │
└─────────────────────────┘
    │
    ▼                      ┌─────────────────────────┐
┌─────────────────────────┐ │       Success?          │
│   Operation Result      ├─┤   Continue Normal       │
└─────────────────────────┘ │      Processing         │
    │ Error                 └─────────────────────────┘
    ▼
┌─────────────────────────┐
│   Classify Error Type   │
│  • Network timeout     │
│  • Database error      │
│  • Validation error    │
│  • ML model error      │
│  • Authentication     │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│   Determine Severity    │
│  • Critical (system)   │
│  • High (service)      │
│  • Medium (feature)    │
│  • Low (warning)       │
└─────────────────────────┘
    │
    ├─────────────────────┬─────────────────────┬─────────────────────┐
    ▼                     ▼                     ▼                     ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  CRITICAL   │ │    HIGH     │ │   MEDIUM    │ │     LOW     │
│   ERROR     │ │   ERROR     │ │   ERROR     │ │   ERROR     │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
    │                     │                     │                     │
    ▼                     ▼                     ▼                     ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Immediate   │ │ Escalate    │ │ Retry with  │ │ Log & Continue │
│ Alert &     │ │ to On-call  │ │ Fallback    │ │ with Fallback │
│ Shutdown    │ │ Team        │ │ Method      │ │              │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
    │                     │                     │                     │
    └─────────────────────┼─────────────────────┼─────────────────────┘
                          ▼                     ▼
                  ┌─────────────────────────────────┐
                  │       Log Error Details         │
                  │  • Timestamp & user context    │
                  │  • Stack trace & parameters    │
                  │  • System state & metrics      │
                  │  • Recovery action taken       │
                  └─────────────────────────────────┘
                          │
                          ▼
                  ┌─────────────────────────────────┐
                  │      Attempt Recovery           │
                  │  • Retry with backoff          │
                  │  • Fallback to alternative     │
                  │  • Circuit breaker activation  │
                  │  • Graceful degradation        │
                  └─────────────────────────────────┘
                          │
                          ▼                      ┌─────────────────────────┐
                  ┌─────────────────────────────┐ │   Recovery Failed?      │
                  │   Recovery Successful?      ├─┤   Escalate to Admin     │
                  └─────────────────────────────┘ │   & User Notification   │
                          │ Yes                   └─────────────────────────┘
                          ▼
                  ┌─────────────────────────────────┐
                  │    Return Appropriate           │
                  │       Response                  │
                  │  • Success with warning        │
                  │  • Partial failure notice      │
                  │  • User-friendly error msg     │
                  └─────────────────────────────────┘
                          │
                          ▼
                  END: Error handled gracefully
```

## 7. Monitoring and Health Check Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                       SYSTEM MONITORING & HEALTH CHECK FLOW                         │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────┐
│   CONTINUOUS MONITORS   │    │   SCHEDULED CHECKS      │    │   ON-DEMAND HEALTH      │
│                        │    │                        │    │       CHECKS           │
│ • API response times   │    │ • Database integrity   │    │                        │
│ • Error rates          │    │ • ML model accuracy    │    │ • Load balancer        │
│ • Resource utilization │    │ • Data quality         │    │ • Service status       │
│ • User activity        │    │ • Security scans       │    │ • Dependency checks    │
└─────────────────────────┘    └─────────────────────────┘    └─────────────────────────┘
          │                              │                              │
          ▼                              ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                            METRIC COLLECTION SYSTEM                                 │
│                                                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ Performance │  │ Application │  │ Infrastructure│  │  Business   │              │
│  │   Metrics   │  │   Metrics   │  │   Metrics    │  │   Metrics   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│   Threshold Analysis    │
│  • Compare to SLA      │
│  • Historical trends   │
│  • Anomaly detection   │
└─────────────────────────┘
          │
          ▼                      ┌─────────────────────────┐
┌─────────────────────────┐      │   Thresholds Normal?    │
│   Alert Evaluation      ├──────┤   Continue Monitoring   │
└─────────────────────────┘      │                        │
          │ Threshold Exceeded   └─────────────────────────┘
          ▼
┌─────────────────────────┐
│   Generate Alerts       │
│  • Severity assessment │
│  • Affected systems    │
│  • Recommended actions │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│   Notification Routing  │
│  • Email alerts        │
│  • SMS for critical    │
│  • Slack notifications │
│  • Dashboard updates   │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│   Incident Response     │
│  • Auto-remediation    │
│  • Manual intervention │
│  • Escalation matrix   │
└─────────────────────────┘
          │
          ▼
END: Issue resolved or escalated
```

These flowcharts provide a comprehensive view of the system's operational flows, decision points, and error handling mechanisms, essential for understanding the system's behavior and for proper documentation in a dissertation project at the University of the West of England Bristol.