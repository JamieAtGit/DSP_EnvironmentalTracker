# GUI Design Documentation

## Overview
This document presents the comprehensive graphical user interface (GUI) design for the Carbon Footprint Tracking System, including browser extension interfaces, web application layouts, and mobile-responsive designs.

## 1. Design Principles and Guidelines

### 1.1 Core Design Principles

#### Accessibility First
- **WCAG 2.1 AA Compliance**: All interfaces meet accessibility standards
- **Color Contrast**: Minimum 4.5:1 ratio for normal text, 3:1 for large text
- **Keyboard Navigation**: Full functionality available via keyboard
- **Screen Reader Support**: Semantic HTML and ARIA labels

#### Environmental Theme
- **Green Color Palette**: Various shades of green to represent environmental consciousness
- **Clean Aesthetics**: Minimalist design to avoid overwhelming users
- **Data Visualization**: Clear charts and graphs for carbon footprint data
- **Trust Indicators**: Visual cues to build confidence in predictions

#### Responsive Design
- **Mobile-First Approach**: Designed for smallest screens first, enhanced for larger
- **Flexible Layouts**: CSS Grid and Flexbox for adaptive layouts
- **Progressive Enhancement**: Core functionality works without JavaScript

### 1.2 Color Palette and Typography

```css
/* Primary Color Palette */
:root {
  /* Green Theme - Environmental Focus */
  --primary-green: #2E7D32;        /* Primary brand color */
  --secondary-green: #4CAF50;      /* Secondary actions */
  --light-green: #81C784;          /* Success states */
  --dark-green: #1B5E20;           /* Emphasis */
  
  /* Supporting Colors */
  --warning-orange: #FF9800;       /* Medium carbon footprint */
  --danger-red: #F44336;           /* High carbon footprint */
  --info-blue: #2196F3;            /* Informational elements */
  --neutral-gray: #757575;         /* Secondary text */
  
  /* Background Colors */
  --bg-primary: #FFFFFF;           /* Main background */
  --bg-secondary: #F5F5F5;         /* Section backgrounds */
  --bg-accent: #E8F5E8;            /* Highlighted sections */
  
  /* Text Colors */
  --text-primary: #212121;         /* Main text */
  --text-secondary: #757575;       /* Secondary text */
  --text-disabled: #BDBDBD;        /* Disabled text */
}

/* Typography Scale */
:root {
  --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'Fira Code', 'Cascadia Code', monospace;
  
  /* Font Sizes */
  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */
  
  /* Font Weights */
  --font-light: 300;
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}
```

## 2. Browser Extension UI Design

### 2.1 Product Page Integration

#### Carbon Footprint Tooltip
```html
<!-- Tooltip Component -->
<div class="carbon-tooltip" id="carbon-tooltip">
  <div class="tooltip-header">
    <div class="carbon-icon">🌱</div>
    <span class="tooltip-title">Carbon Impact</span>
  </div>
  
  <div class="carbon-value">
    <span class="value">2.4</span>
    <span class="unit">kg CO₂e</span>
  </div>
  
  <div class="confidence-indicator">
    <div class="confidence-bar">
      <div class="confidence-fill" style="width: 85%"></div>
    </div>
    <span class="confidence-text">85% confidence</span>
  </div>
  
  <button class="details-button" onclick="showDetails()">
    View Details
  </button>
</div>
```

```css
/* Tooltip Styling */
.carbon-tooltip {
  position: absolute;
  background: var(--bg-primary);
  border: 2px solid var(--primary-green);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 8px 32px rgba(46, 125, 50, 0.15);
  font-family: var(--font-family-primary);
  z-index: 10000;
  max-width: 280px;
  animation: slideIn 0.3s ease-out;
}

.tooltip-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.carbon-icon {
  font-size: var(--text-lg);
}

.tooltip-title {
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.carbon-value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 12px;
}

.carbon-value .value {
  font-size: var(--text-2xl);
  font-weight: var(--font-bold);
  color: var(--primary-green);
}

.carbon-value .unit {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.confidence-indicator {
  margin-bottom: 12px;
}

.confidence-bar {
  width: 100%;
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--warning-orange), var(--secondary-green));
  transition: width 0.3s ease;
}

.confidence-text {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.details-button {
  width: 100%;
  padding: 8px 16px;
  background: var(--primary-green);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.details-button:hover {
  background: var(--dark-green);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 2.2 Extension Popup Interface

#### Popup Layout
```html
<!-- Extension Popup -->
<div class="popup-container">
  <header class="popup-header">
    <div class="logo">
      <img src="icon32.png" alt="Carbon Tracker" class="logo-icon">
      <h1 class="logo-text">Carbon Tracker</h1>
    </div>
    <button class="settings-btn" onclick="openSettings()">⚙️</button>
  </header>
  
  <main class="popup-main">
    <!-- Current Page Analysis -->
    <section class="current-analysis" id="current-analysis">
      <div class="analysis-card">
        <div class="product-info">
          <img src="" alt="Product" class="product-image" id="product-image">
          <div class="product-details">
            <h3 class="product-name" id="product-name">Loading...</h3>
            <p class="product-brand" id="product-brand">...</p>
          </div>
        </div>
        
        <div class="carbon-display">
          <div class="carbon-main">
            <span class="carbon-number" id="carbon-number">--</span>
            <span class="carbon-unit">kg CO₂e</span>
          </div>
          <div class="carbon-rating" id="carbon-rating">
            <div class="rating-indicator"></div>
            <span class="rating-text">Calculating...</span>
          </div>
        </div>
      </div>
      
      <div class="action-buttons">
        <button class="btn-secondary" onclick="showBreakdown()">
          View Breakdown
        </button>
        <button class="btn-primary" onclick="provideFeedback()">
          Rate Accuracy
        </button>
      </div>
    </section>
    
    <!-- Manual Input Section -->
    <section class="manual-input" style="display: none;" id="manual-input">
      <form class="input-form" onsubmit="submitManualAnalysis(event)">
        <div class="form-group">
          <label for="manual-product-name">Product Name</label>
          <input type="text" id="manual-product-name" required>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="material">Material</label>
            <select id="material" required>
              <option value="">Select...</option>
              <option value="plastic">Plastic</option>
              <option value="metal">Metal</option>
              <option value="wood">Wood</option>
              <option value="textile">Textile</option>
              <option value="glass">Glass</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="weight">Weight (kg)</label>
            <input type="number" id="weight" step="0.1" min="0">
          </div>
        </div>
        
        <button type="submit" class="btn-primary">Analyze Product</button>
      </form>
    </section>
    
    <!-- Recent History -->
    <section class="recent-history">
      <h3 class="section-title">Recent Analyses</h3>
      <div class="history-list" id="history-list">
        <!-- Dynamic content -->
      </div>
    </section>
  </main>
  
  <footer class="popup-footer">
    <div class="tab-navigation">
      <button class="tab-btn active" onclick="switchTab('current')">Current</button>
      <button class="tab-btn" onclick="switchTab('manual')">Manual</button>
      <button class="tab-btn" onclick="switchTab('history')">History</button>
    </div>
  </footer>
</div>
```

```css
/* Popup Styling */
.popup-container {
  width: 380px;
  min-height: 500px;
  background: var(--bg-primary);
  font-family: var(--font-family-primary);
  display: flex;
  flex-direction: column;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--bg-secondary);
  background: var(--bg-accent);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-icon {
  width: 24px;
  height: 24px;
}

.logo-text {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--primary-green);
  margin: 0;
}

.settings-btn {
  background: none;
  border: none;
  font-size: var(--text-lg);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
}

.settings-btn:hover {
  background: var(--bg-secondary);
}

.popup-main {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.analysis-card {
  background: var(--bg-accent);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
}

.product-info {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
}

.product-details {
  flex: 1;
}

.product-name {
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  margin: 0 0 4px 0;
  color: var(--text-primary);
  line-height: 1.3;
}

.product-brand {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  margin: 0;
}

.carbon-display {
  text-align: center;
}

.carbon-main {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 8px;
}

.carbon-number {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  color: var(--primary-green);
}

.carbon-unit {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.carbon-rating {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.rating-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--secondary-green);
}

.rating-indicator.medium {
  background: var(--warning-orange);
}

.rating-indicator.high {
  background: var(--danger-red);
}

.rating-text {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.btn-primary,
.btn-secondary {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: var(--primary-green);
  color: white;
}

.btn-primary:hover {
  background: var(--dark-green);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--neutral-gray);
}

.btn-secondary:hover {
  background: var(--neutral-gray);
  color: white;
}

.popup-footer {
  border-top: 1px solid var(--bg-secondary);
  background: var(--bg-primary);
}

.tab-navigation {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.tab-btn {
  padding: 12px;
  background: none;
  border: none;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn.active {
  color: var(--primary-green);
  background: var(--bg-accent);
}

.tab-btn:hover {
  background: var(--bg-secondary);
}
```

## 3. Web Application UI Design

### 3.1 Dashboard Layout

#### Main Dashboard
```html
<!-- Dashboard Layout -->
<div class="dashboard-container">
  <aside class="sidebar">
    <div class="sidebar-header">
      <img src="logo.svg" alt="Carbon Tracker" class="sidebar-logo">
      <span class="sidebar-title">Carbon Tracker</span>
    </div>
    
    <nav class="sidebar-nav">
      <a href="/dashboard" class="nav-item active">
        <span class="nav-icon">📊</span>
        <span class="nav-text">Dashboard</span>
      </a>
      <a href="/predict" class="nav-item">
        <span class="nav-icon">🔍</span>
        <span class="nav-text">Analyze Product</span>
      </a>
      <a href="/history" class="nav-item">
        <span class="nav-icon">📈</span>
        <span class="nav-text">History</span>
      </a>
      <a href="/insights" class="nav-item">
        <span class="nav-icon">💡</span>
        <span class="nav-text">Insights</span>
      </a>
      <a href="/settings" class="nav-item">
        <span class="nav-icon">⚙️</span>
        <span class="nav-text">Settings</span>
      </a>
    </nav>
    
    <div class="sidebar-footer">
      <div class="user-profile">
        <img src="avatar.jpg" alt="User" class="user-avatar">
        <div class="user-info">
          <span class="user-name">John Doe</span>
          <span class="user-email">john@example.com</span>
        </div>
      </div>
    </div>
  </aside>
  
  <main class="main-content">
    <header class="content-header">
      <div class="header-left">
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">Track your environmental impact</p>
      </div>
      <div class="header-right">
        <button class="btn-icon" onclick="toggleNotifications()">
          <span class="notification-icon">🔔</span>
          <span class="notification-badge">3</span>
        </button>
        <button class="btn-primary" onclick="analyzeNewProduct()">
          + Analyze Product
        </button>
      </div>
    </header>
    
    <div class="dashboard-grid">
      <!-- Summary Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">🌱</div>
          <div class="stat-content">
            <div class="stat-value">142.5</div>
            <div class="stat-label">kg CO₂e Tracked</div>
            <div class="stat-change positive">↓ 12% vs last month</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">📦</div>
          <div class="stat-content">
            <div class="stat-value">23</div>
            <div class="stat-label">Products Analyzed</div>
            <div class="stat-change neutral">+5 this week</div>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-content">
            <div class="stat-value">8.2</div>
            <div class="stat-label">Avg. kg CO₂e per Product</div>
            <div class="stat-change negative">↑ 3% vs last month</div>
          </div>
        </div>
      </div>
      
      <!-- Chart Section -->
      <div class="chart-section">
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">Carbon Footprint Trend</h3>
            <div class="chart-controls">
              <button class="time-filter active">7D</button>
              <button class="time-filter">30D</button>
              <button class="time-filter">90D</button>
            </div>
          </div>
          <div class="chart-container">
            <!-- Chart component here -->
            <canvas id="trendChart"></canvas>
          </div>
        </div>
      </div>
      
      <!-- Recent Activity -->
      <div class="activity-section">
        <div class="activity-card">
          <h3 class="activity-title">Recent Analyses</h3>
          <div class="activity-list">
            <!-- Dynamic content -->
          </div>
        </div>
      </div>
    </div>
  </main>
</div>
```

### 3.2 Product Analysis Form

#### Analysis Interface
```html
<!-- Product Analysis Form -->
<div class="analysis-container">
  <div class="analysis-form-card">
    <header class="form-header">
      <h2 class="form-title">Analyze Product Carbon Footprint</h2>
      <p class="form-subtitle">Enter product details to calculate environmental impact</p>
    </header>
    
    <form class="analysis-form" onsubmit="submitAnalysis(event)">
      <div class="form-section">
        <h3 class="section-title">Basic Information</h3>
        <div class="form-grid">
          <div class="form-group span-2">
            <label for="product-name">Product Name *</label>
            <input type="text" id="product-name" placeholder="e.g., Wireless Bluetooth Headphones" required>
          </div>
          
          <div class="form-group">
            <label for="brand">Brand</label>
            <input type="text" id="brand" placeholder="e.g., Sony">
          </div>
          
          <div class="form-group">
            <label for="category">Category</label>
            <select id="category">
              <option value="">Select category...</option>
              <option value="electronics">Electronics</option>
              <option value="clothing">Clothing</option>
              <option value="home">Home & Garden</option>
              <option value="sports">Sports & Outdoors</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">Physical Properties</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="weight">Weight</label>
            <div class="input-with-unit">
              <input type="number" id="weight" step="0.1" min="0" placeholder="0.5">
              <select class="unit-selector">
                <option value="kg">kg</option>
                <option value="g">g</option>
                <option value="lb">lb</option>
              </select>
            </div>
          </div>
          
          <div class="form-group">
            <label for="material">Primary Material *</label>
            <select id="material" required>
              <option value="">Select material...</option>
              <option value="plastic">Plastic</option>
              <option value="metal">Metal</option>
              <option value="wood">Wood</option>
              <option value="textile">Textile</option>
              <option value="glass">Glass</option>
              <option value="ceramic">Ceramic</option>
              <option value="composite">Composite</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="dimensions">Dimensions (L×W×H)</label>
            <input type="text" id="dimensions" placeholder="e.g., 20×15×10 cm">
          </div>
          
          <div class="form-group">
            <label for="packaging">Packaging Type</label>
            <select id="packaging">
              <option value="">Select packaging...</option>
              <option value="minimal">Minimal</option>
              <option value="standard">Standard</option>
              <option value="excessive">Excessive</option>
            </select>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <h3 class="section-title">Origin & Transport</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="origin">Country of Origin</label>
            <select id="origin">
              <option value="">Select country...</option>
              <option value="CN">China</option>
              <option value="US">United States</option>
              <option value="DE">Germany</option>
              <option value="JP">Japan</option>
              <option value="KR">South Korea</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="transport">Transport Method</label>
            <select id="transport">
              <option value="">Auto-detect</option>
              <option value="air">Air Freight</option>
              <option value="sea">Sea Freight</option>
              <option value="land">Land Transport</option>
              <option value="rail">Rail Transport</option>
            </select>
          </div>
          
          <div class="form-group span-2">
            <label for="additional-info">Additional Information</label>
            <textarea id="additional-info" rows="3" placeholder="Any additional details about the product..."></textarea>
          </div>
        </div>
      </div>
      
      <div class="form-actions">
        <button type="button" class="btn-secondary" onclick="clearForm()">
          Clear Form
        </button>
        <button type="submit" class="btn-primary" id="analyze-btn">
          <span class="btn-text">Analyze Carbon Footprint</span>
          <span class="btn-loading" style="display: none;">
            <span class="spinner"></span>
            Analyzing...
          </span>
        </button>
      </div>
    </form>
  </div>
  
  <!-- Results Section -->
  <div class="results-container" id="results-container" style="display: none;">
    <div class="results-card">
      <header class="results-header">
        <h3 class="results-title">Carbon Footprint Analysis</h3>
        <div class="confidence-score">
          <span class="confidence-label">Confidence:</span>
          <span class="confidence-value" id="confidence-value">85%</span>
        </div>
      </header>
      
      <div class="carbon-result">
        <div class="carbon-main-value">
          <span class="carbon-number" id="result-carbon">12.4</span>
          <span class="carbon-unit">kg CO₂e</span>
        </div>
        <div class="carbon-rating" id="result-rating">
          <div class="rating-indicator medium"></div>
          <span class="rating-text">Medium Impact</span>
        </div>
      </div>
      
      <div class="breakdown-chart">
        <h4 class="breakdown-title">Impact Breakdown</h4>
        <div class="breakdown-bars">
          <div class="breakdown-item">
            <div class="breakdown-label">Materials</div>
            <div class="breakdown-bar">
              <div class="breakdown-fill" style="width: 45%"></div>
            </div>
            <div class="breakdown-value">45%</div>
          </div>
          <div class="breakdown-item">
            <div class="breakdown-label">Manufacturing</div>
            <div class="breakdown-bar">
              <div class="breakdown-fill" style="width: 30%"></div>
            </div>
            <div class="breakdown-value">30%</div>
          </div>
          <div class="breakdown-item">
            <div class="breakdown-label">Transport</div>
            <div class="breakdown-bar">
              <div class="breakdown-fill" style="width: 25%"></div>
            </div>
            <div class="breakdown-value">25%</div>
          </div>
        </div>
      </div>
      
      <div class="results-actions">
        <button class="btn-secondary" onclick="exportResults()">
          Export Results
        </button>
        <button class="btn-secondary" onclick="saveToHistory()">
          Save to History
        </button>
        <button class="btn-primary" onclick="provideFeedback()">
          Rate Accuracy
        </button>
      </div>
    </div>
  </div>
</div>
```

## 4. Responsive Design Patterns

### 4.1 Mobile-First CSS
```css
/* Base Mobile Styles */
.dashboard-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.sidebar {
  order: 2;
  background: var(--bg-primary);
  border-top: 1px solid var(--bg-secondary);
}

.main-content {
  order: 1;
  flex: 1;
  padding: 16px;
}

.dashboard-grid {
  display: grid;
  gap: 16px;
}

.stats-grid {
  display: grid;
  gap: 12px;
}

.stat-card {
  padding: 16px;
  background: var(--bg-accent);
  border-radius: 12px;
}

/* Tablet Styles */
@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-grid {
    gap: 24px;
  }
  
  .main-content {
    padding: 24px;
  }
}

/* Desktop Styles */
@media (min-width: 1024px) {
  .dashboard-container {
    flex-direction: row;
  }
  
  .sidebar {
    order: 1;
    width: 280px;
    border-top: none;
    border-right: 1px solid var(--bg-secondary);
  }
  
  .main-content {
    order: 2;
    padding: 32px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "stats stats"
      "chart activity";
  }
  
  .stats-grid {
    grid-area: stats;
  }
  
  .chart-section {
    grid-area: chart;
  }
  
  .activity-section {
    grid-area: activity;
  }
}

/* Large Desktop */
@media (min-width: 1440px) {
  .main-content {
    padding: 40px;
  }
  
  .dashboard-grid {
    grid-template-columns: 2fr 1fr;
    grid-template-areas:
      "stats activity"
      "chart activity";
  }
}
```

### 4.2 Component Responsiveness
```css
/* Responsive Form Layout */
.analysis-form {
  max-width: 800px;
  margin: 0 auto;
}

.form-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .span-2 {
    grid-column: span 2;
  }
}

/* Responsive Results Layout */
.results-container {
  max-width: 600px;
  margin: 24px auto 0;
}

.breakdown-bars {
  display: grid;
  gap: 12px;
}

@media (min-width: 768px) {
  .carbon-result {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .results-actions {
    display: flex;
    gap: 12px;
  }
  
  .results-actions button {
    flex: 1;
  }
}
```

## 5. Accessibility Features

### 5.1 ARIA Labels and Semantic HTML
```html
<!-- Accessible Navigation -->
<nav class="sidebar-nav" role="navigation" aria-label="Main navigation">
  <a href="/dashboard" class="nav-item" aria-current="page">
    <span class="nav-icon" aria-hidden="true">📊</span>
    <span class="nav-text">Dashboard</span>
  </a>
</nav>

<!-- Accessible Form -->
<form class="analysis-form" role="form" aria-labelledby="form-title">
  <h2 id="form-title" class="form-title">Product Analysis Form</h2>
  
  <div class="form-group">
    <label for="product-name">
      Product Name
      <span class="required" aria-label="required">*</span>
    </label>
    <input 
      type="text" 
      id="product-name" 
      aria-describedby="product-name-help"
      required
    >
    <div id="product-name-help" class="help-text">
      Enter the full product name as it appears on the package
    </div>
  </div>
</form>

<!-- Accessible Chart -->
<div class="chart-container" role="img" aria-labelledby="chart-title" aria-describedby="chart-description">
  <h3 id="chart-title">Carbon Footprint Trend</h3>
  <p id="chart-description" class="sr-only">
    Line chart showing carbon footprint trends over the last 30 days. 
    Values range from 5.2 to 15.8 kg CO₂e with an overall decreasing trend.
  </p>
  <canvas id="trendChart" aria-hidden="true"></canvas>
</div>
```

### 5.2 Focus Management and Keyboard Navigation
```css
/* Focus Indicators */
*:focus {
  outline: 2px solid var(--info-blue);
  outline-offset: 2px;
}

.btn-primary:focus,
.btn-secondary:focus {
  outline: 2px solid var(--info-blue);
  outline-offset: 2px;
  box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.1);
}

/* Skip Links */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-green);
  color: white;
  padding: 8px;
  border-radius: 4px;
  text-decoration: none;
  z-index: 100;
}

.skip-link:focus {
  top: 6px;
}

/* Screen Reader Only Content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## 6. Animation and Interaction Design

### 6.1 Micro-Interactions
```css
/* Button Animations */
.btn-primary {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(0);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(46, 125, 50, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
  transition: all 0.1s;
}

/* Loading States */
.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Card Hover Effects */
.stat-card {
  transition: all 0.3s ease;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

/* Tooltip Animations */
.tooltip {
  opacity: 0;
  transform: translateY(-10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  pointer-events: none;
}

.tooltip.visible {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
```

### 6.2 Progressive Enhancement
```css
/* Base styles work without animations */
.analysis-form {
  opacity: 1;
  transform: none;
}

/* Enhanced animations for capable browsers */
@media (prefers-reduced-motion: no-preference) {
  .analysis-form {
    animation: fadeInUp 0.6s ease-out;
  }
  
  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
}

/* Respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

This comprehensive GUI design documentation ensures a consistent, accessible, and user-friendly interface across all platforms while maintaining the environmental theme and professional academic standards expected for a dissertation project at the University of the West of England Bristol.