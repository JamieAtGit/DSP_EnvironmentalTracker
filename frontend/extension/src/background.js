// Import configuration
import CONFIG from './config.js';

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "FETCH_ECO_INSIGHT") {
      const { href } = request.payload;
      
      // Validate URL
      if (!href || typeof href !== 'string') {
        sendResponse({
          impact: "Error",
          summary: "Invalid URL provided",
          recyclable: null
        });
        return;
      }
  
      fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.ESTIMATE_EMISSIONS}`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          // Add security headers
          "X-Requested-With": "XMLHttpRequest"
        },
        body: JSON.stringify({
          amazon_url: href,
          include_packaging: true,
          postcode: "BS16 1QY"  // Default postcode for UWE Bristol
        }),
        // Add timeout
        signal: AbortSignal.timeout(CONFIG.SECURITY.REQUEST_TIMEOUT)
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error(`HTTP ${res.status}: ${res.statusText}`);
          }
          return res.json();
        })
        .then((json) => {
          // Validate response structure
          if (!json || typeof json !== 'object') {
            throw new Error('Invalid response format');
          }
          
          const a = json.data?.attributes || {};
          sendResponse({
            impact: a.eco_score_ml || "Unknown",
            summary: `CO₂: ${a.carbon_kg ?? "?"}kg, Material: ${a.material_type || "N/A"}`,
            recyclable: a.recyclability === "High"
              ? true
              : a.recyclability === "Low"
              ? false
              : null,
            confidence: a.eco_score_ml_confidence || null
          });
        })
        .catch((err) => {
          console.error("API fetch error:", err);
          
          // Different error messages based on error type
          let errorMessage = "Service temporarily unavailable";
          if (err.name === 'TimeoutError') {
            errorMessage = "Request timed out";
          } else if (err.message.includes('HTTP 401')) {
            errorMessage = "Authentication required";
          } else if (err.message.includes('HTTP 429')) {
            errorMessage = "Rate limit exceeded";
          }
          
          sendResponse({
            impact: "Error",
            summary: errorMessage,
            recyclable: null,
            error: true
          });
        });
  
      return true; // keep message channel open for async reply
    }
  });
  