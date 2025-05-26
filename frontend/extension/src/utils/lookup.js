// tooltip.js — Cursor-following eco tooltip

function createFloatingTooltip() {
  const tooltip = document.createElement("div");
  tooltip.className = "eco-tooltip";
  tooltip.style.position = "absolute";
  tooltip.style.pointerEvents = "none";
  tooltip.style.opacity = 0;
  document.body.appendChild(tooltip);
  return tooltip;
}

function guessMaterialFromCategory(title) {
  const lower = title.toLowerCase();
  if (lower.includes("headphones") || lower.includes("earbuds")) return "plastic";
  if (lower.includes("phone case") || lower.includes("cover")) return "polycarbonate";
  if (lower.includes("laptop") || lower.includes("notebook")) return "aluminum";
  if (lower.includes("bottle") || lower.includes("thermos")) return "steel";
  if (lower.includes("jacket") || lower.includes("coat")) return "polyester";
  if (lower.includes("shoes") || lower.includes("trainers")) return "rubber";
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

async function enhanceTooltips() {
  const products = document.querySelectorAll("h2.a-size-mini a.a-link-normal");
  if (!products.length) return;

  const tooltip = createFloatingTooltip();
  const insights = await window.loadMaterialInsights();

  products.forEach((el) => {
    const title = el.textContent.toLowerCase();

    let matched = null;
    for (const key in insights) {
      const regex = new RegExp(`\\b${key}\\b`, "i");
      if (regex.test(title)) {
        matched = { ...insights[key], name: key };
        break;
      }
    }

    if (!matched) return;

    el.addEventListener("mousemove", (e) => {
      tooltip.style.left = `${e.pageX + 15}px`;
      tooltip.style.top = `${e.pageY + 10}px`;
      const confidence = matched.confidence || 75;

      tooltip.innerHTML = `
        <div><strong>🧬 Material: ${matched.name || "Unknown"}</strong></div>
        <div><strong>${matched.impact || "Eco Score"}</strong></div>
        <div>${matched.summary || "No summary available."}</div>
        <div>${matched.recyclable === true ? "♻️ Recyclable" : matched.recyclable === false ? "🚯 Not recyclable" : ""}</div>
        <div style="margin-top: 6px;">
          <div style="font-size: 12px; margin-bottom: 2px;">Confidence:</div>
          <div style="height: 6px; background: #e5e7eb; border-radius: 4px; overflow: hidden;">
            <div style="width: ${confidence}%; background: #4ade80; height: 100%;"></div>
          </div>
        </div>
        <div style="margin-top: 8px;">
          <a href="https://yourdomain.com/insights" target="_blank" style="font-size: 12px; color: #2563eb;">Learn more ↗</a>
        </div>
      `;
      tooltip.style.opacity = 1;
    });

    el.addEventListener("mouseleave", () => {
      tooltip.style.opacity = 0;
    });
  });
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

    // Priority 1: Exact match from materialHint
    if (materialHint && materialHint !== "unknown") {
      for (const key in data) {
        if (materialHint.includes(key.toLowerCase()) || key.toLowerCase().includes(materialHint)) {
          console.log("✅ Matched from material hint:", key);
          return { ...data[key], name: key, confidence: 95 };
        }
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

    // Priority 4: Look for common material descriptors in title
    const commonMaterials = ['plastic', 'metal', 'wood', 'steel', 'aluminum', 'glass', 'ceramic', 'rubber', 'leather', 'cotton', 'polyester'];
    for (const material of commonMaterials) {
      if (title.includes(material) && data[material]) {
        console.log("🎯 Found common material in title:", material);
        return { ...data[material], name: material, confidence: 50 };
      }
    }

    console.log("❓ No material match found for:", title.substring(0, 30) + "...");
    return null;
    
  } catch (error) {
    console.error("❌ Error in ecoLookup:", error);
    return null;
  }
};
