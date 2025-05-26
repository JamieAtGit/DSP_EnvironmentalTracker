// tooltip.js — Cursor-following eco tooltip

// ⚠️ LEGACY createFloatingTooltip - DISABLED
function createFloatingTooltip() {
  console.log("⚠️ Legacy createFloatingTooltip() called but DISABLED");
  return null;
}

function guessMaterialFromCategory(title) {
  const lower = title.toLowerCase();
  if (lower.includes("headphones") || lower.includes("earbuds")) return "plastics";
  if (lower.includes("phone case") || lower.includes("cover")) return "plastics";
  if (lower.includes("laptop") || lower.includes("notebook")) return "aluminum";
  if (lower.includes("bottle") || lower.includes("thermos")) return "steel";
  if (lower.includes("jacket") || lower.includes("coat")) return "polyester";
  if (lower.includes("shoes") || lower.includes("trainers")) return "rubber";
  if (lower.includes("backpack") || lower.includes("rucksack") || lower.includes("hiking")) return "nylon";
  if (lower.includes("bag") && !lower.includes("sleeping")) return "nylon";
  return null;
}

// ✅ Enhanced material insights loader
window.loadMaterialInsights = async function () {
  try {
    const getURL = typeof chrome !== "undefined" && chrome.runtime?.getURL
      ? chrome.runtime.getURL
      : (path) => path;
    const res = await fetch(getURL('material_insights.json'));
    const insights = await res.json();
    console.log("📚 Material insights loaded:", Object.keys(insights).length, "materials");
    return insights;
  } catch (e) {
    console.error("❌ Failed to load insights:", e);
    return {};
  }
};

// ⚠️ LEGACY enhanceTooltips function - DISABLED
// This has been moved to /src/components/tooltip.js with major improvements
// Keeping this file only for the ecoLookup function and utilities

async function enhanceTooltips() {
  // DISABLED - Using enhanced tooltip.js implementation instead
  console.log("⚠️ Legacy enhanceTooltips() called but DISABLED - using enhanced tooltip.js instead");
  return;
}

window.ecoLookup = async function (title, materialHint) {
  try {
    // Use cached data if available
    let data = window.materialInsights;
    if (!data) {
      const getURL = typeof chrome !== "undefined" && chrome.runtime?.getURL
        ? chrome.runtime.getURL
        : (path) => path;

      const res = await fetch(getURL("material_insights.json"));
      data = await res.json();
      window.materialInsights = data; // Cache for future use
    }

    // Normalize inputs
    title = (title || "").toLowerCase();
    materialHint = (materialHint || "")
      .replace(/[\u200E\u200F\u202A-\u202E]/g, "") // Strip hidden Unicode chars
      .trim()
      .toLowerCase();

    console.log("🔍 Looking up title:", title.substring(0, 50) + "...");
    if (materialHint) console.log("🧪 Material hint:", materialHint);

    // Priority 1: Exact match from materialHint with fallback mapping
    if (materialHint && materialHint !== "unknown") {
      // First try exact match
      for (const key in data) {
        if (materialHint.includes(key.toLowerCase()) || key.toLowerCase().includes(materialHint)) {
          console.log("✅ Matched from material hint:", key);
          return { ...data[key], name: key, confidence: 95 };
        }
      }
      
      // Fallback mapping for common mismatches
      const materialFallbacks = {
        'polycarbonate': 'plastics',
        'plastic': 'plastics', 
        'pvc': 'plastics',
        'abs': 'plastics',
        'metal': 'steel',
        'metallic': 'aluminum',
        'wood': 'timber',
        'fabric': 'cotton',
        'cloth': 'cotton',
        'synthetic': 'polyester'
      };
      
      const fallback = materialFallbacks[materialHint.toLowerCase()];
      if (fallback && data[fallback]) {
        console.log("🔄 Using fallback mapping:", materialHint, "→", fallback);
        return { ...data[fallback], name: fallback, confidence: 85 };
      }
    }

    // Priority 2: Enhanced fuzzy match from title
    let bestMatch = null;
    let highestConfidence = 0;

    for (const key in data) {
      const keyLower = key.toLowerCase();
      
      // Check for exact word boundary matches first
      const exactRegex = new RegExp(`\\b${keyLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, "i");
      if (exactRegex.test(title)) {
        const confidence = 90 + (keyLower.length / title.length) * 10; // Longer matches get higher confidence
        if (confidence > highestConfidence) {
          bestMatch = { ...data[key], name: key, confidence: Math.min(confidence, 100) };
          highestConfidence = confidence;
        }
      }
      
      // Then check for partial matches
      else if (title.includes(keyLower) && keyLower.length > 3) {
        const confidence = 70 + (keyLower.length / title.length) * 20;
        if (confidence > highestConfidence) {
          bestMatch = { ...data[key], name: key, confidence: Math.min(confidence, 85) };
          highestConfidence = confidence;
        }
      }
    }

    if (bestMatch && highestConfidence > 60) {
      console.log("🔍 Fuzzy matched from title:", bestMatch.name, "confidence:", bestMatch.confidence);
      return bestMatch;
    }

    // Priority 3: Enhanced category guessing
    const fallback = guessMaterialFromCategory(title);
    if (fallback && data[fallback]) {
      console.log("🔁 Using fallback category material:", fallback);
      return { ...data[fallback], name: fallback, confidence: 60 };
    }

    // Priority 4: Look for common material descriptors in title with proper mapping
    const commonMaterials = [
      { search: 'plastic', material: 'plastics' },
      { search: 'metal', material: 'steel' },
      { search: 'wood', material: 'timber' },
      { search: 'steel', material: 'steel' },
      { search: 'aluminum', material: 'aluminum' },
      { search: 'glass', material: 'glass' },
      { search: 'ceramic', material: 'ceramic' },
      { search: 'rubber', material: 'rubber' },
      { search: 'leather', material: 'leather' },
      { search: 'cotton', material: 'cotton' },
      { search: 'polyester', material: 'polyester' },
      { search: 'nylon', material: 'nylon' }
    ];
    
    for (const item of commonMaterials) {
      if (title.includes(item.search) && data[item.material]) {
        console.log("🎯 Found common material in title:", item.material);
        return { ...data[item.material], name: item.material, confidence: 50 };
      }
    }

    console.log("❓ No material match found for:", title.substring(0, 30) + "...");
    return null;
    
  } catch (error) {
    console.error("❌ Error in ecoLookup:", error);
    return null;
  }
};
