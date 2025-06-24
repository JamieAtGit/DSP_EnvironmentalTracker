/**
 * Configuration file for the Carbon Footprint Extension
 */

const CONFIG = {
  // API Configuration
  API_BASE_URL: process.env.NODE_ENV === 'production' 
    ? 'https://your-production-api.com'  // Replace with actual production URL
    : 'http://localhost:5000',
  
  // API Endpoints
  ENDPOINTS: {
    ESTIMATE_EMISSIONS: '/estimate_emissions',
    PREDICT: '/predict',
    HEALTH: '/health'
  },
  
  // Security Configuration
  SECURITY: {
    MAX_RETRIES: 3,
    REQUEST_TIMEOUT: 10000, // 10 seconds
    RATE_LIMIT_DELAY: 1000  // 1 second between requests
  },
  
  // UI Configuration
  UI: {
    TOOLTIP_DELAY: 500,
    ANIMATION_DURATION: 300
  }
};

// Validate configuration
if (!CONFIG.API_BASE_URL) {
  throw new Error('API_BASE_URL must be configured');
}

export default CONFIG;