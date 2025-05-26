function createTooltip(html) {
  const tooltip = document.createElement("div");
  tooltip.className = "eco-tooltip";
  tooltip.innerHTML = html;
  
  // Enhanced CSS styles to ensure visibility
  tooltip.style.cssText = `
    position: absolute !important;
    z-index: 10000 !important;
    background: rgba(0, 0, 0, 0.9) !important;
    color: white !important;
    padding: 12px !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-family: Arial, sans-serif !important;
    line-height: 1.4 !important;
    max-width: 300px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    opacity: 0 !important;
    transition: opacity 0.2s ease !important;
    pointer-events: none !important;
    word-wrap: break-word !important;
  `;
  
  document.body.appendChild(tooltip);
  console.log("🔧 Created tooltip element:", tooltip);
  return tooltip;
}

function attachTooltipEvents(target, html) {
  // Prevent duplicate tooltips on the same element
  if (target.dataset.enhancedTooltipAttached === "true") {
    console.log("⚠️ Tooltip already attached to element, skipping");
    return;
  }
  target.dataset.enhancedTooltipAttached = "true";
  
  const tooltip = createTooltip(html);
  target.style.borderBottom = "2px dotted #10b981"; // Better green color
  
  // Store tooltip reference on the target for cleanup
  target._ecoTooltip = tooltip;
  
  const mouseEnterHandler = () => {
    console.log("🟢 Mouse entered tooltip target");
    
    // Hide any other visible tooltips first
    document.querySelectorAll('.eco-tooltip').forEach(t => {
      if (t !== tooltip) {
        t.style.opacity = '0';
      }
    });
    
    const rect = target.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    // Better positioning with bounds checking
    let top = rect.bottom + scrollTop + 10;
    let left = rect.left + scrollLeft;
    
    // Keep tooltip within viewport
    if (left + 300 > window.innerWidth) {
      left = window.innerWidth - 320;
    }
    if (left < 10) {
      left = 10;
    }
    
    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
    tooltip.style.opacity = '1';
    
    console.log("🟢 Enhanced tooltip showing at:", { top, left });
  };

  const mouseLeaveHandler = () => {
    console.log("🔴 Mouse left tooltip target");
    tooltip.style.opacity = '0';
  };
  
  // Add event listeners with proper cleanup
  target.addEventListener("mouseenter", mouseEnterHandler, { passive: true });
  target.addEventListener("mouseleave", mouseLeaveHandler, { passive: true });
  
  // Store handlers for potential cleanup
  target._ecoTooltipHandlers = { mouseEnterHandler, mouseLeaveHandler };
  
  console.log("✅ Tooltip events attached to element:", target.textContent.substring(0, 30) + "...");
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
  
  // Enhanced category-based guessing with priority order (most specific first)
  const categoryPatterns = [
    // Bags & Backpacks (High Priority - fix aluminum issue)
    { patterns: ['backpack', 'rucksack', 'hiking backpack', 'travel backpack'], material: 'nylon', priority: 10 },
    { patterns: ['bag', 'handbag', 'shoulder bag', 'tote bag'], material: 'leather', priority: 9 },
    { patterns: ['gym bag', 'sports bag', 'duffel bag'], material: 'nylon', priority: 9 },
    { patterns: ['laptop bag', 'briefcase'], material: 'nylon', priority: 9 },
    
    // Textiles & Clothing (High Priority)
    { patterns: ['t-shirt', 'shirt', 'tee', 'top'], material: 'cotton', priority: 10 },
    { patterns: ['jeans', 'denim'], material: 'cotton', priority: 10 },
    { patterns: ['jacket', 'coat', 'hoodie', 'sweater'], material: 'polyester', priority: 9 },
    { patterns: ['pants', 'trousers', 'leggings'], material: 'cotton', priority: 8 },
    { patterns: ['dress', 'skirt'], material: 'polyester', priority: 8 },
    { patterns: ['socks', 'underwear'], material: 'cotton', priority: 9 },
    { patterns: ['shoes', 'sneakers', 'trainers', 'boots'], material: 'leather', priority: 8 },
    
    // Electronics (Medium Priority)
    { patterns: ['headphones', 'earbuds', 'earphones'], material: 'plastic', priority: 8 },
    { patterns: ['phone case', 'case', 'cover', 'protector'], material: 'polycarbonate', priority: 9 },
    { patterns: ['laptop', 'macbook', 'ultrabook', 'notebook computer'], material: 'aluminum', priority: 7 },
    { patterns: ['charger', 'cable', 'adapter', 'cord'], material: 'plastic', priority: 8 },
    { patterns: ['speaker', 'soundbar'], material: 'plastic', priority: 7 },
    { patterns: ['tablet', 'ipad'], material: 'aluminum', priority: 7 },
    
    // Home & Kitchen
    { patterns: ['water bottle', 'bottle', 'flask', 'tumbler'], material: 'steel', priority: 8 },
    { patterns: ['mug', 'cup', 'glass'], material: 'ceramic', priority: 8 },
    { patterns: ['pan', 'pot', 'cookware', 'frying pan'], material: 'aluminum', priority: 8 },
    { patterns: ['cutting board', 'chopping board'], material: 'wood', priority: 9 },
    { patterns: ['plate', 'bowl', 'dish'], material: 'ceramic', priority: 8 },
    { patterns: ['curtain', 'drapes'], material: 'polyester', priority: 7 },
    { patterns: ['towel', 'washcloth'], material: 'cotton', priority: 8 },
    { patterns: ['pillow', 'cushion'], material: 'polyester', priority: 7 },
    { patterns: ['blanket', 'throw'], material: 'cotton', priority: 7 },
    
    // Sports & Outdoors
    { patterns: ['yoga mat', 'exercise mat', 'gym mat'], material: 'rubber', priority: 9 },
    { patterns: ['tent', 'camping'], material: 'nylon', priority: 8 },
    { patterns: ['sleeping bag'], material: 'nylon', priority: 8 },
    
    // Tools & Hardware
    { patterns: ['screwdriver', 'wrench', 'hammer', 'tool'], material: 'steel', priority: 8 },
    { patterns: ['drill', 'power tool'], material: 'plastic', priority: 7 },
    
    // Accessories
    { patterns: ['watch', 'smartwatch'], material: 'steel', priority: 7 },
    { patterns: ['sunglasses', 'glasses'], material: 'polycarbonate', priority: 8 },
    { patterns: ['wallet', 'purse'], material: 'leather', priority: 8 },
    { patterns: ['belt'], material: 'leather', priority: 8 },
    
    // Books & Media
    { patterns: ['book', 'paperback', 'hardcover'], material: 'paper', priority: 9 },
    { patterns: ['notebook', 'journal', 'diary'], material: 'paper', priority: 8 },
    
    // Beauty & Personal Care
    { patterns: ['brush', 'comb'], material: 'plastic', priority: 7 },
    { patterns: ['mirror'], material: 'glass', priority: 8 }
  ];
  
  // Check category patterns with priority (highest priority first)
  let bestMatch = null;
  let highestPriority = 0;
  
  for (const category of categoryPatterns) {
    const matchedPattern = category.patterns.find(pattern => titleLower.includes(pattern));
    if (matchedPattern && category.priority > highestPriority) {
      bestMatch = {
        material: category.material,
        pattern: matchedPattern,
        priority: category.priority
      };
      highestPriority = category.priority;
    }
  }
  
  if (bestMatch) {
    console.log("🎯 Category-based material guess:", bestMatch.material, `(priority: ${bestMatch.priority}, pattern: "${bestMatch.pattern}")`);
    return bestMatch.material;
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

  // Only show tooltips with reasonable confidence (lowered threshold for better coverage)
  const confidence = info.confidence || 70;
  if (confidence < 35) {
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
  console.log("✅ Enhanced tooltip script running");
  
  // Clean up any old tooltips that might be left over
  const oldTooltips = document.querySelectorAll('.eco-tooltip');
  oldTooltips.forEach(tooltip => {
    if (tooltip.style.opacity === '0' || !tooltip.style.opacity) {
      tooltip.remove();
    }
  });
  
  // Remove old tooltip indicators (dotted borders)
  const oldIndicators = document.querySelectorAll('[style*="border-bottom: 2px dotted green"]');
  oldIndicators.forEach(el => {
    el.style.borderBottom = '';
  });
  
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
             !el.dataset.enhancedTooltipAttached && // Prevent duplicates from enhanced system
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
