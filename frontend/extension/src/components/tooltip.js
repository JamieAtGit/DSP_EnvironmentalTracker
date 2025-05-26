function createTooltip(html) {
  const tooltip = document.createElement("div");
  tooltip.className = "eco-tooltip";
  tooltip.innerHTML = html;
  document.body.appendChild(tooltip);
  return tooltip;
}

function attachTooltipEvents(target, html) {
  const tooltip = createTooltip(html);
  target.style.borderBottom = "2px dotted green";
  target.addEventListener("mouseenter", () => {
    const rect = target.getBoundingClientRect();
    tooltip.style.top = `${rect.bottom + window.scrollY + 10}px`;
    tooltip.style.left = `${rect.left + window.scrollX}px`;
    tooltip.style.opacity = 1;
    console.log("🟢 Hovering:", html);
  });

  target.addEventListener("mouseleave", () => {
    tooltip.style.opacity = 0;
  });
}

function extractMaterialFromDetailPage() {
  // Enhanced selectors for Amazon's product detail pages
  const selectors = [
    "th, span.a-text-bold",
    ".a-section .a-row span.a-text-bold",
    "#feature-bullets ul span.a-text-bold",
    "#productDetails_techSpec_section_1 th",
    "#productDetails_detailBullets_sections1 th",
    ".pdTab span.a-text-bold"
  ];
  
  for (const selector of selectors) {
    const labels = document.querySelectorAll(selector);
    for (const label of labels) {
      const text = label.innerText.trim().toLowerCase();
      if (text.includes("material") || text.includes("fabric") || text.includes("construction")) {
        const valueEl = label.closest("tr")?.querySelector("td") ||
                        label.parentElement?.nextElementSibling ||
                        label.nextElementSibling;
        if (valueEl) {
          const val = valueEl.innerText.trim().toLowerCase();
          if (val && val !== "material" && val.length > 2) {
            console.log("✅ Found material in product page:", val);
            return val;
          }
        }
      }
    }
  }
  
  // Additional extraction from feature bullets
  const bullets = document.querySelectorAll("#feature-bullets ul li span");
  for (const bullet of bullets) {
    const text = bullet.innerText.toLowerCase();
    const materialMatch = text.match(/(?:made (?:of|from)|material:?\s*|fabric:?\s*)([a-z\s,]+)/i);
    if (materialMatch) {
      const material = materialMatch[1].trim().split(/[,;]/)[0].trim();
      if (material.length > 2) {
        console.log("✅ Found material in bullets:", material);
        return material;
      }
    }
  }
  
  console.warn("⚠️ No material found in detail page.");
  return null;
}


function extractMaterialFromTile(tile) {
  // Look in the tile and its parent containers for material info
  const containers = [
    tile.closest("div"),
    tile.closest("div")?.parentElement,
    tile.closest("[data-component-type='s-search-result']")
  ].filter(Boolean);
  
  for (const container of containers) {
    const text = container.innerText || "";
    
    // Look for explicit material mentions
    const materialPatterns = [
      /Material Type[:\s]*([A-Za-z,\s]+)/i,
      /Material[:\s]*([A-Za-z,\s]+)/i,
      /Made (?:of|from)[:\s]*([A-Za-z,\s]+)/i,
      /Fabric[:\s]*([A-Za-z,\s]+)/i
    ];
    
    for (const pattern of materialPatterns) {
      const match = text.match(pattern);
      if (match) {
        const material = match[1].trim().toLowerCase().split(/[,;]/)[0].trim();
        if (material.length > 2) {
          console.log("✅ Found material in tile:", material);
          return material;
        }
      }
    }
  }
  return null;
}

async function smartGuessMaterialFromTitle(title) {
  const titleLower = title.toLowerCase();
  
  // Load material insights to get comprehensive list
  const insights = window.materialInsights || await window.loadMaterialInsights?.() || {};
  
  // Enhanced category-based guessing with common Amazon product patterns
  const categoryPatterns = [
    // Electronics
    { patterns: ['headphones', 'earbuds', 'earphones'], material: 'plastic' },
    { patterns: ['phone case', 'case', 'cover', 'protector'], material: 'polycarbonate' },
    { patterns: ['laptop', 'macbook', 'ultrabook', 'notebook'], material: 'aluminum' },
    { patterns: ['charger', 'cable', 'adapter'], material: 'plastic' },
    { patterns: ['speaker', 'soundbar'], material: 'plastic' },
    
    // Clothing & Accessories
    { patterns: ['t-shirt', 'shirt', 'tee'], material: 'cotton' },
    { patterns: ['jeans', 'denim'], material: 'cotton' },
    { patterns: ['jacket', 'coat', 'hoodie', 'sweater'], material: 'polyester' },
    { patterns: ['shoes', 'sneakers', 'trainers', 'boots'], material: 'leather' },
    { patterns: ['socks'], material: 'cotton' },
    { patterns: ['watch', 'smartwatch'], material: 'steel' },
    { patterns: ['sunglasses', 'glasses'], material: 'polycarbonate' },
    
    // Home & Kitchen
    { patterns: ['bottle', 'flask', 'tumbler', 'thermos'], material: 'steel' },
    { patterns: ['mug', 'cup'], material: 'ceramic' },
    { patterns: ['pan', 'pot', 'cookware'], material: 'aluminum' },
    { patterns: ['cutting board', 'chopping board'], material: 'wood' },
    { patterns: ['plate', 'bowl', 'dish'], material: 'ceramic' },
    { patterns: ['curtain', 'drapes'], material: 'polyester' },
    { patterns: ['towel'], material: 'cotton' },
    { patterns: ['pillow', 'cushion'], material: 'polyester' },
    
    // Sports & Outdoors
    { patterns: ['yoga mat', 'exercise mat'], material: 'rubber' },
    { patterns: ['water bottle'], material: 'plastic' },
    { patterns: ['backpack', 'bag'], material: 'nylon' },
    { patterns: ['tent'], material: 'nylon' },
    
    // Tools & Hardware
    { patterns: ['screwdriver', 'wrench', 'hammer'], material: 'steel' },
    { patterns: ['drill'], material: 'aluminum' },
    
    // Books & Media
    { patterns: ['book', 'notebook', 'journal'], material: 'paper' },
    
    // Beauty & Personal Care
    { patterns: ['brush', 'comb'], material: 'plastic' },
    { patterns: ['mirror'], material: 'glass' }
  ];
  
  // Check category patterns first
  for (const category of categoryPatterns) {
    if (category.patterns.some(pattern => titleLower.includes(pattern))) {
      console.log("🎯 Category-based material guess:", category.material);
      return category.material;
    }
  }
  
  // Check for direct material mentions in title
  const materialKeywords = Object.keys(insights);
  for (const material of materialKeywords) {
    if (titleLower.includes(material.toLowerCase())) {
      console.log("🔍 Direct material found in title:", material);
      return material;
    }
  }
  
  // Check for common material descriptors
  const materialDescriptors = [
    { patterns: ['wooden', 'wood'], material: 'wood' },
    { patterns: ['metal', 'metallic'], material: 'steel' },
    { patterns: ['plastic'], material: 'plastic' },
    { patterns: ['glass'], material: 'glass' },
    { patterns: ['ceramic'], material: 'ceramic' },
    { patterns: ['rubber'], material: 'rubber' },
    { patterns: ['leather'], material: 'leather' },
    { patterns: ['fabric', 'cloth', 'textile'], material: 'cotton' },
    { patterns: ['carbon fiber', 'carbon fibre'], material: 'carbon fiber' },
    { patterns: ['bamboo'], material: 'bamboo' },
    { patterns: ['silicone'], material: 'silicone' }
  ];
  
  for (const descriptor of materialDescriptors) {
    if (descriptor.patterns.some(pattern => titleLower.includes(pattern))) {
      console.log("📝 Descriptor-based material guess:", descriptor.material);
      return descriptor.material;
    }
  }
  
  console.log("❓ No material guess found for:", title);
  return null;
}

function showTooltipFor(target, info) {
  if (!info || typeof info !== "object" || !info.name || info.name === "unknown") {
    console.warn("⚠️ Skipping tooltip — no valid info provided.");
    return;
  }

  // Only show tooltips with reasonable confidence
  const confidence = info.confidence || 75;
  if (confidence < 45) {
    console.warn("⚠️ Skipping tooltip — confidence too low:", confidence);
    return;
  }

  const emoji = info.impact === "High" ? "🔥"
              : info.impact === "Moderate" ? "⚠️"
              : info.impact === "Low" ? "🌱"
              : info.impact === "Low-Moderate" ? "🌿"
              : "❓";

  const recycle = info.recyclable === true ? "♻️ Recyclable"
                   : info.recyclable === false ? "🚯 Not recyclable"
                   : "❓ Recyclability unknown";

  // Enhanced tooltip with confidence indicator
  const confidenceColor = confidence >= 80 ? "#10b981" 
                         : confidence >= 60 ? "#f59e0b" 
                         : "#ef4444";

  const html = `
    <div style="border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 8px; margin-bottom: 8px;">
      <strong>🧬 Material: ${info.name}</strong>
      <div style="margin-top: 4px; font-size: 11px; color: #888;">
        Confidence: <span style="color: ${confidenceColor};">${Math.round(confidence)}%</span>
      </div>
    </div>
    <div style="margin-bottom: 8px;">
      <strong>${emoji} ${info.impact || "Unknown"} Environmental Impact</strong>
    </div>
    <div style="font-size: 13px; line-height: 1.4; margin-bottom: 8px;">
      ${info.summary || "No summary available."}
    </div>
    <div style="font-size: 12px; color: #ccc;">
      <em>${recycle}</em>
    </div>
  `;

  attachTooltipEvents(target, html);
}

async function enhanceTooltips() {
  console.log("✅ Tooltip script running");
  
  // Ensure material insights are loaded
  if (!window.materialInsights) {
    try {
      const getURL = typeof chrome !== "undefined" && chrome.runtime?.getURL
        ? chrome.runtime.getURL
        : (path) => path;
      const res = await fetch(getURL("material_insights.json"));
      window.materialInsights = await res.json();
      console.log("📚 Loaded material insights:", Object.keys(window.materialInsights).length, "materials");
    } catch (e) {
      console.error("❌ Failed to load material insights:", e);
      window.materialInsights = {};
    }
  }

  const isProductDetail = document.querySelector("#productTitle") !== null;

  if (isProductDetail) {
    const titleEl = document.querySelector("#productTitle");
    console.log("🧩 Found titleEl:", titleEl);
    if (!titleEl || titleEl.dataset.tooltipAttached) return;

    titleEl.dataset.tooltipAttached = "true";
    const title = titleEl.textContent.trim();
    let materialHint = extractMaterialFromDetailPage();

    console.log("🧪 Product Page Title:", title);

    // Fallback 1: Try guessing material from title
    if (!materialHint) {
      const titleLower = title.toLowerCase();
      const materialList = Object.keys(window.materialInsights || {});
      const titleMatch = materialList.find(mat => titleLower.includes(mat.toLowerCase()));

      if (titleMatch) {
        materialHint = titleMatch.toLowerCase();
        console.log("🪵 Fallback from title:", materialHint);
      }
    }

    // Fallback 2: Try guessing material from product description and features
    if (!materialHint) {
      const descSelectors = [
        "#productDescription",
        "#feature-bullets ul",
        "#aplus_feature_div",
        ".a-section.a-spacing-medium"
      ];
      
      for (const selector of descSelectors) {
        const descEl = document.querySelector(selector);
        if (descEl) {
          const descText = descEl.innerText || "";
          const descMatch = descText.match(/\b(aluminum|plastic|metal|wood|steel|rubber|polycarbonate|carbon fiber|cotton|polyester|nylon|leather|ceramic|glass|bamboo|silicone)\b/i);
          if (descMatch) {
            materialHint = descMatch[1].toLowerCase();
            console.log("📜 Fallback from description:", materialHint);
            break;
          }
        }
      }
    }
    
    // Fallback 3: Smart guess from title using enhanced patterns
    if (!materialHint) {
      materialHint = await smartGuessMaterialFromTitle(title);
    }

    if (!materialHint) {
      console.warn("❓ No material found — using 'unknown'");
      materialHint = "unknown";
    }

    console.log("🧪 Final Material Hint:", materialHint);

    const info = await window.ecoLookup(title, materialHint);

    showTooltipFor(titleEl, info || {
      impact: "Unknown",
      summary: "No insight found.",
      recyclable: null
    });

  } else {
    // Comprehensive selectors for different Amazon layouts
    const productSelectors = [
      // Search results page
      "h2.a-size-mini.a-spacing-none.a-color-base span.a-text-normal",
      "h2.s-size-mini.s-spacing-none.s-color-base span",
      "h2 span.a-text-normal",
      "span.a-text-normal",
      
      // Grid view products
      "div[data-component-type='s-search-result'] h2 span",
      "div.puisg-title span",
      "div.puisg-title h2 span",
      
      // Category pages
      "div.a-section.a-spacing-none h2 span",
      "div.s-title-instructions-style h2 span",
      
      // Mobile layouts
      "div._bGlmZ_itemName_19mCu span",
      "h2._bGlmZ_truncate_2bzXt span",
      
      // Today's deals and special pages
      "div.DealLink h2 span",
      "div.deals-shoveler h2 span",
      
      // Recommendation sections
      "div.a-cardui h2 span",
      "div.p13n-sc-truncated span",
      
      // Alternative product title formats
      "a.a-link-normal span.a-text-normal",
      "a[data-image-source-density] span",
      "h3.a-size-base span",
      
      // Fresh/Whole Foods products
      "div.fresh-tile h2 span",
      "div.wf-product-tile h2 span"
    ];
    
    let tiles = [];
    for (const selector of productSelectors) {
      const elements = Array.from(document.querySelectorAll(selector));
      tiles.push(...elements);
    }
    
    // Filter for valid product titles and remove duplicates
    tiles = tiles.filter((el, index, arr) => {
      const text = el.textContent.trim();
      return text.length > 10 && 
             text.length < 200 && 
             !el.dataset.tooltipAttached &&
             // Remove duplicates based on text content
             arr.findIndex(other => other.textContent.trim() === text) === index &&
             // Exclude navigation and UI elements
             !text.toLowerCase().includes('see more') &&
             !text.toLowerCase().includes('view details') &&
             !text.toLowerCase().includes('add to cart');
    });
    
    console.log("✅ Product tiles found:", tiles.length);

    for (const tile of tiles) {
      tile.dataset.tooltipAttached = "true";
      const title = tile.textContent.trim();
      let materialHint = extractMaterialFromTile(tile);
      
      // Enhanced material detection for tiles
      if (!materialHint) {
        materialHint = await smartGuessMaterialFromTitle(title);
      }
      
      const info = await window.ecoLookup(title, materialHint);
      // showTooltipFor now handles confidence checking internally
      showTooltipFor(tile, info);
    }
  }
}




// ⏱️ Improved debounced observer to prevent overload
let lastEnhanceRun = 0;
let enhanceTimeout = null;
const DEBOUNCE_MS = 2000; // Reduced for more responsiveness

function debouncedEnhanceTooltips() {
  const now = Date.now();
  if (now - lastEnhanceRun > DEBOUNCE_MS) {
    lastEnhanceRun = now;
    enhanceTooltips().catch(console.error);
  } else {
    // Clear existing timeout and set a new one
    if (enhanceTimeout) {
      clearTimeout(enhanceTimeout);
    }
    enhanceTimeout = setTimeout(() => {
      lastEnhanceRun = Date.now();
      enhanceTooltips().catch(console.error);
    }, DEBOUNCE_MS);
  }
}

// Initialize on page load
window.addEventListener("load", () => {
  setTimeout(debouncedEnhanceTooltips, 1000);
});

// Monitor for dynamic content changes (common on Amazon)
const observer = new MutationObserver((mutations) => {
  // Only trigger if meaningful changes occurred
  const hasRelevantChanges = mutations.some(mutation => 
    mutation.type === 'childList' && 
    mutation.addedNodes.length > 0 &&
    Array.from(mutation.addedNodes).some(node => 
      node.nodeType === Node.ELEMENT_NODE &&
      (node.tagName === 'DIV' || node.tagName === 'SPAN' || node.tagName === 'H2' || node.tagName === 'H3')
    )
  );
  
  if (hasRelevantChanges) {
    debouncedEnhanceTooltips();
  }
});

observer.observe(document.body, { 
  childList: true, 
  subtree: true,
  attributeFilter: ['class', 'data-component-type'] // Only watch for relevant attribute changes
});

// Also run when URL changes (for SPA navigation)
let currentUrl = window.location.href;
setInterval(() => {
  if (window.location.href !== currentUrl) {
    currentUrl = window.location.href;
    setTimeout(debouncedEnhanceTooltips, 500);
  }
}, 1000);
