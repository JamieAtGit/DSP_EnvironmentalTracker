# Entity Relationship Diagrams

## Overview
This document provides comprehensive Entity Relationship Diagrams (ERDs) for the Carbon Footprint Tracking System, illustrating data structures and relationships between system entities.

## Primary ERD - Complete System

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CARBON FOOTPRINT TRACKING SYSTEM                          │
│                                 Entity Relationship Diagram                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                                    │      USER       │
                                    ├─────────────────┤
                                    │ PK user_id      │
                                    │    username     │
                                    │    email        │
                                    │    password_hash│
                                    │    created_at   │
                                    │    last_login   │
                                    │    is_active    │
                                    │    role         │
                                    └─────────────────┘
                                            │
                                            │ 1:N
                                            ▼
                                    ┌─────────────────┐
                                    │   USER_SESSION  │
                                    ├─────────────────┤
                                    │ PK session_id   │
                                    │ FK user_id      │
                                    │    token        │
                                    │    expires_at   │
                                    │    ip_address   │
                                    │    user_agent   │
                                    └─────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    PRODUCT      │         │   PREDICTION    │         │     BRAND       │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ PK product_id   │◄────────┤ PK prediction_id│         │ PK brand_id     │
│    name         │ 1:N     │ FK product_id   │         │    name         │
│    description  │         │ FK user_id      │         │    origin_country│
│    asin         │         │    carbon_footprint       │    founded_year │
│    category     │         │    confidence   │         │    website      │
│    subcategory  │         │    method_used  │         │    is_verified  │
│    url          │         │    created_at   │         └─────────────────┘
│    image_url    │         │    model_version│                 │
│    brand_id     ├─────────┤    prediction_breakdown    │         │ N:1
│    created_at   │ N:1     │    user_feedback│         │         │
│    updated_at   │         │    processing_time         │         │
└─────────────────┘         └─────────────────┘         │         │
        │                           │                   │         │
        │ 1:N                       │ 1:N               │         │
        ▼                           ▼                   │         │
┌─────────────────┐         ┌─────────────────┐         │         │
│ PRODUCT_FEATURE │         │   USER_FEEDBACK │         │         │
├─────────────────┤         ├─────────────────┤         │         │
│ PK feature_id   │         │ PK feedback_id  │         │         │
│ FK product_id   │         │ FK prediction_id│         │         │
│    material     │         │ FK user_id      │         │         │
│    weight       │         │    rating       │         │         │
│    dimensions   │         │    accuracy_feedback      │         │
│    packaging    │         │    comments     │         │         │
│    recyclability│         │    actual_footprint       │         │
│    transport_method       │    created_at   │         │         │
│    origin_country│         │    is_verified  │         │         │
│    created_at   │         └─────────────────┘         │         │
│    updated_at   │                                     │         │
└─────────────────┘                                     │         │
                                                        │         │
                                                        ▼         │
                            ┌─────────────────┐         ┌─────────┴───────┐
                            │   ML_MODEL      │         │ PRODUCT_BRAND   │
                            ├─────────────────┤         ├─────────────────┤
                            │ PK model_id     │         │ FK product_id   │
                            │    name         │         │ FK brand_id     │
                            │    version      │         │    confidence   │
                            │    algorithm    │         │    created_at   │
                            │    created_at   │         └─────────────────┘
                            │    deployed_at  │
                            │    is_active    │
                            │    metrics      │
                            │    file_path    │
                            └─────────────────┘
                                    │
                                    │ 1:N
                                    ▼
                            ┌─────────────────┐
                            │ MODEL_METRICS   │
                            ├─────────────────┤
                            │ PK metric_id    │
                            │ FK model_id     │
                            │    accuracy     │
                            │    precision    │
                            │    recall       │
                            │    f1_score     │
                            │    confusion_matrix│
                            │    created_at   │
                            └─────────────────┘

        ┌─────────────────┐                 ┌─────────────────┐
        │ CARBON_FACTOR   │                 │   AUDIT_LOG     │
        ├─────────────────┤                 ├─────────────────┤
        │ PK factor_id    │                 │ PK log_id       │
        │    material     │                 │ FK user_id      │
        │    co2_per_kg   │                 │    action       │
        │    source       │                 │    table_name   │
        │    region       │                 │    record_id    │
        │    created_at   │                 │    old_values   │
        │    updated_at   │                 │    new_values   │
        │    is_verified  │                 │    ip_address   │
        └─────────────────┘                 │    timestamp    │
                                           └─────────────────┘
```

## Detailed Entity Descriptions

### 1. USER Entity
```sql
CREATE TABLE user (
    user_id         SERIAL PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login      TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE,
    role            ENUM('user', 'admin', 'analyst') DEFAULT 'user'
);

-- Indexes
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_user_active ON user(is_active);
```

**Relationships:**
- One-to-Many with USER_SESSION
- One-to-Many with PREDICTION
- One-to-Many with USER_FEEDBACK
- One-to-Many with AUDIT_LOG

### 2. PRODUCT Entity
```sql
CREATE TABLE product (
    product_id      SERIAL PRIMARY KEY,
    name            VARCHAR(500) NOT NULL,
    description     TEXT,
    asin            VARCHAR(20) UNIQUE,
    category        VARCHAR(100),
    subcategory     VARCHAR(100),
    url             VARCHAR(1000),
    image_url       VARCHAR(1000),
    brand_id        INT REFERENCES brand(brand_id),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_product_asin ON product(asin);
CREATE INDEX idx_product_category ON product(category);
CREATE INDEX idx_product_brand ON product(brand_id);
CREATE FULLTEXT INDEX idx_product_name ON product(name);
```

**Relationships:**
- Many-to-One with BRAND
- One-to-Many with PRODUCT_FEATURE
- One-to-Many with PREDICTION

### 3. PREDICTION Entity
```sql
CREATE TABLE prediction (
    prediction_id       SERIAL PRIMARY KEY,
    product_id          INT REFERENCES product(product_id),
    user_id             INT REFERENCES user(user_id),
    carbon_footprint    DECIMAL(10,4) NOT NULL,
    confidence          DECIMAL(5,4) CHECK (confidence BETWEEN 0 AND 1),
    method_used         ENUM('ml_model', 'rule_based', 'hybrid') NOT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_version       VARCHAR(20),
    prediction_breakdown JSON,
    user_feedback       ENUM('accurate', 'too_high', 'too_low', 'unsure'),
    processing_time     DECIMAL(8,4)
);

-- Indexes
CREATE INDEX idx_prediction_product ON prediction(product_id);
CREATE INDEX idx_prediction_user ON prediction(user_id);
CREATE INDEX idx_prediction_date ON prediction(created_at);
CREATE INDEX idx_prediction_method ON prediction(method_used);
```

**Relationships:**
- Many-to-One with PRODUCT
- Many-to-One with USER
- One-to-Many with USER_FEEDBACK

### 4. PRODUCT_FEATURE Entity
```sql
CREATE TABLE product_feature (
    feature_id          SERIAL PRIMARY KEY,
    product_id          INT REFERENCES product(product_id),
    material            VARCHAR(100),
    weight              DECIMAL(8,3),
    dimensions          VARCHAR(50),
    packaging           VARCHAR(100),
    recyclability       ENUM('high', 'medium', 'low', 'none'),
    transport_method    ENUM('air', 'sea', 'land', 'rail', 'mixed'),
    origin_country      VARCHAR(100),
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_feature_product ON product_feature(product_id);
CREATE INDEX idx_feature_material ON product_feature(material);
CREATE INDEX idx_feature_origin ON product_feature(origin_country);
```

**Relationships:**
- Many-to-One with PRODUCT

### 5. BRAND Entity
```sql
CREATE TABLE brand (
    brand_id        SERIAL PRIMARY KEY,
    name            VARCHAR(200) UNIQUE NOT NULL,
    origin_country  VARCHAR(100),
    founded_year    INT,
    website         VARCHAR(500),
    is_verified     BOOLEAN DEFAULT FALSE
);

-- Indexes
CREATE INDEX idx_brand_name ON brand(name);
CREATE INDEX idx_brand_country ON brand(origin_country);
```

**Relationships:**
- One-to-Many with PRODUCT

## Advanced ERD - Machine Learning Components

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ML MODEL MANAGEMENT SYSTEM                             │
│                                 Entity Relationship Diagram                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   ML_MODEL      │
                    ├─────────────────┤
                    │ PK model_id     │
                    │    name         │
                    │    version      │
                    │    algorithm    │
                    │    created_at   │
                    │    deployed_at  │
                    │    is_active    │
                    │    metrics      │
                    │    file_path    │
                    │    config       │
                    └─────────────────┘
                            │
                            │ 1:N
                            ▼
            ┌─────────────────┐               ┌─────────────────┐
            │ MODEL_METRICS   │               │ TRAINING_RUN    │
            ├─────────────────┤               ├─────────────────┤
            │ PK metric_id    │               │ PK run_id       │
            │ FK model_id     │               │ FK model_id     │
            │    accuracy     │               │    start_time   │
            │    precision    │               │    end_time     │
            │    recall       │               │    status       │
            │    f1_score     │               │    dataset_size │
            │    confusion_matrix            │    hyperparams  │
            │    roc_auc      │               │    loss_values  │
            │    created_at   │               │    created_at   │
            └─────────────────┘               └─────────────────┘
                    ▲                                 │
                    │ 1:N                             │ 1:N
                    │                                 ▼
            ┌─────────────────┐               ┌─────────────────┐
            │ FEATURE_IMPORTANCE│              │ TRAINING_DATASET│
            ├─────────────────┤               ├─────────────────┤
            │ PK importance_id│               │ PK dataset_id   │
            │ FK model_id     │               │ FK run_id       │
            │    feature_name │               │    file_path    │
            │    importance_score            │    size_mb      │
            │    rank         │               │    num_samples  │
            │    created_at   │               │    version      │
            └─────────────────┘               │    checksum     │
                                             │    created_at   │
                                             └─────────────────┘
```

## Data Validation and Constraints

### 1. Primary Key Constraints
- All entities have auto-incrementing primary keys
- Primary keys are immutable once assigned
- Foreign key relationships enforce referential integrity

### 2. Business Rules Constraints
```sql
-- Carbon footprint must be positive
ALTER TABLE prediction ADD CONSTRAINT chk_positive_footprint 
CHECK (carbon_footprint >= 0);

-- Confidence must be between 0 and 1
ALTER TABLE prediction ADD CONSTRAINT chk_confidence_range 
CHECK (confidence BETWEEN 0 AND 1);

-- Weight must be positive
ALTER TABLE product_feature ADD CONSTRAINT chk_positive_weight 
CHECK (weight > 0);

-- Founded year must be reasonable
ALTER TABLE brand ADD CONSTRAINT chk_reasonable_year 
CHECK (founded_year BETWEEN 1800 AND EXTRACT(YEAR FROM CURRENT_DATE));
```

### 3. Data Integrity Rules
```sql
-- Ensure prediction has either product or manual input
ALTER TABLE prediction ADD CONSTRAINT chk_prediction_source
CHECK (product_id IS NOT NULL OR prediction_breakdown IS NOT NULL);

-- Model must be active to make predictions
CREATE TRIGGER trg_active_model_only
BEFORE INSERT ON prediction
FOR EACH ROW
WHEN (NEW.model_version IS NOT NULL)
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM ml_model 
    WHERE version = NEW.model_version AND is_active = TRUE
  ) THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Model version is not active';
  END IF;
END;
```

## Normalization Analysis

### Current Normalization Level: 3NF (Third Normal Form)

**1NF Compliance:**
- ✅ All attributes contain atomic values
- ✅ No repeating groups
- ✅ Primary keys defined for all entities

**2NF Compliance:**
- ✅ All non-key attributes fully dependent on primary key
- ✅ Composite keys avoided where possible
- ✅ Partial dependencies eliminated

**3NF Compliance:**
- ✅ No transitive dependencies
- ✅ All non-key attributes depend only on primary key
- ✅ Functional dependencies preserved

### Denormalization Considerations

**Performance Optimizations:**
```sql
-- Materialized view for frequent queries
CREATE MATERIALIZED VIEW product_summary AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    b.name as brand_name,
    b.origin_country,
    pf.material,
    pf.weight,
    AVG(pred.carbon_footprint) as avg_footprint,
    COUNT(pred.prediction_id) as prediction_count
FROM product p
LEFT JOIN brand b ON p.brand_id = b.brand_id
LEFT JOIN product_feature pf ON p.product_id = pf.product_id
LEFT JOIN prediction pred ON p.product_id = pred.product_id
GROUP BY p.product_id, p.name, p.category, b.name, b.origin_country, pf.material, pf.weight;
```

## Security and Privacy Considerations

### 1. Sensitive Data Protection
```sql
-- Encrypt sensitive user data
ALTER TABLE user MODIFY password_hash VARBINARY(255);
ALTER TABLE user_session MODIFY token VARBINARY(512);

-- Add data classification
ALTER TABLE product_feature ADD COLUMN data_classification 
ENUM('public', 'internal', 'confidential') DEFAULT 'internal';
```

### 2. Audit Trail Implementation
```sql
-- Comprehensive audit logging
CREATE TABLE audit_log (
    log_id          SERIAL PRIMARY KEY,
    user_id         INT REFERENCES user(user_id),
    action          ENUM('CREATE', 'READ', 'UPDATE', 'DELETE'),
    table_name      VARCHAR(50) NOT NULL,
    record_id       INT,
    old_values      JSON,
    new_values      JSON,
    ip_address      INET,
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3. Data Retention Policies
```sql
-- Implement data retention
ALTER TABLE prediction ADD COLUMN expires_at TIMESTAMP;
ALTER TABLE user_feedback ADD COLUMN expires_at TIMESTAMP;

-- Cleanup procedure
DELIMITER //
CREATE PROCEDURE cleanup_expired_data()
BEGIN
    DELETE FROM prediction WHERE expires_at < NOW();
    DELETE FROM user_feedback WHERE expires_at < NOW();
    DELETE FROM audit_log WHERE timestamp < DATE_SUB(NOW(), INTERVAL 2 YEAR);
END //
DELIMITER ;
```