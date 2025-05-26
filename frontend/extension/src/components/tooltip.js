// Smart cleanup function - only cleans up broken/orphaned tooltips
function cleanupBrokenTooltips() {
  console.log("🧹 Cleaning up broken tooltips");
  
  // Find and clean up elements that have the flag but no working handlers
  const enhancedElements = document.querySelectorAll('[data-enhanced-tooltip-attached="true"]');
  enhancedElements.forEach(el => {
    // Check if element still exists in DOM and has working handlers
    if (!document.contains(el) || (!el._ecoTooltip && !el._ecoTooltipHandlers)) {
      // Element is orphaned or broken - clean it up
      if (el._ecoTooltip) {
        el._ecoTooltip.remove();
        el._ecoTooltip = null;
      }
      if (el._ecoTooltipHandlers) {
        el.removeEventListener("mouseenter", el._ecoTooltipHandlers.mouseEnterHandler);
        el.removeEventListener("mouseleave", el._ecoTooltipHandlers.mouseLeaveHandler);
        if (el._ecoTooltipHandlers.mouseMoveHandler) {
          el.removeEventListener("mousemove", el._ecoTooltipHandlers.mouseMoveHandler);
        }
        el._ecoTooltipHandlers = null;
      }
      el.style.borderBottom = '';
      el.dataset.enhancedTooltipAttached = "false";
    }
  });
  
  // Remove orphaned tooltip elements
  const orphanedTooltips = document.querySelectorAll('.eco-tooltip');
  orphanedTooltips.forEach(tooltip => {
    let isAttached = false;
    enhancedElements.forEach(el => {
      if (el._ecoTooltip === tooltip) {
        isAttached = true;
      }
    });
    if (!isAttached) {
      tooltip.remove();
    }
  });
}

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
  // Check if tooltip is already properly attached and working
  if (target.dataset.enhancedTooltipAttached === "true" && target._ecoTooltip && target._ecoTooltipHandlers) {
    console.log("✅ Tooltip already working on element, skipping");
    return;
  }
  
  // Clean up any existing broken tooltip and handlers first
  if (target._ecoTooltip) {
    target._ecoTooltip.remove();
    target._ecoTooltip = null;
  }
  if (target._ecoTooltipHandlers) {
    target.removeEventListener("mouseenter", target._ecoTooltipHandlers.mouseEnterHandler);
    target.removeEventListener("mouseleave", target._ecoTooltipHandlers.mouseLeaveHandler);
    if (target._ecoTooltipHandlers.mouseMoveHandler) {
      target.removeEventListener("mousemove", target._ecoTooltipHandlers.mouseMoveHandler);
    }
    target._ecoTooltipHandlers = null;
  }
  
  target.dataset.enhancedTooltipAttached = "true";
  
  const tooltip = createTooltip(html);
  target.style.borderBottom = "2px dotted #10b981"; // Better green color
  
  // Store tooltip reference on the target for cleanup
  target._ecoTooltip = tooltip;
  
  const mouseEnterHandler = () => {
    console.log("🟢 Mouse entered tooltip target");
    
    // Hide other visible tooltips (but don't affect their event handlers)
    document.querySelectorAll('.eco-tooltip').forEach(t => {
      if (t !== tooltip && t.style.opacity === '1') {
        t.style.opacity = '0';
        setTimeout(() => {
          if (t.style.opacity === '0') {
            t.style.display = 'none';
          }
        }, 150);
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
    
    // Ensure tooltip is positioned and visible
    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
    tooltip.style.display = 'block';
    tooltip.style.opacity = '1';
    tooltip.style.pointerEvents = 'none';
    
    console.log("🟢 Enhanced tooltip showing at:", { top, left });
  };

  const mouseLeaveHandler = () => {
    console.log("🔴 Mouse left tooltip target");
    tooltip.style.opacity = '0';
    // Small delay before hiding to prevent flicker
    setTimeout(() => {
      if (tooltip.style.opacity === '0') {
        tooltip.style.display = 'none';
      }
    }, 150);
  };
  
  // Add event listeners with proper cleanup
  target.addEventListener("mouseenter", mouseEnterHandler, { passive: true });
  target.addEventListener("mouseleave", mouseLeaveHandler, { passive: true });
  
  // Also handle mouse movement for better responsiveness
  const mouseMoveHandler = (e) => {
    if (tooltip.style.opacity === '1') {
      const rect = target.getBoundingClientRect();
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
      
      let top = rect.bottom + scrollTop + 10;
      let left = rect.left + scrollLeft;
      
      if (left + 300 > window.innerWidth) {
        left = window.innerWidth - 320;
      }
      if (left < 10) {
        left = 10;
      }
      
      tooltip.style.top = `${top}px`;
      tooltip.style.left = `${left}px`;
    }
  };
  
  target.addEventListener("mousemove", mouseMoveHandler, { passive: true });
  
  // Store handlers for potential cleanup
  target._ecoTooltipHandlers = { mouseEnterHandler, mouseLeaveHandler, mouseMoveHandler };
  
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
  
  let foundMaterials = [];
  
  for (const selector of selectors) {
    const labels = document.querySelectorAll(selector);
    for (const label of labels) {
      const text = label.innerText.trim().toLowerCase();
      if (text.includes("material") || text.includes("fabric") || text.includes("construction") || text.includes("composition")) {
        const valueEl = label.closest("tr")?.querySelector("td") ||
                        label.parentElement?.nextElementSibling ||
                        label.nextElementSibling;
        if (valueEl) {
          const val = valueEl.innerText.trim().toLowerCase();
          if (val && val !== "material" && val.length > 2) {
            console.log("✅ Found material in product page:", val);
            foundMaterials.push(val);
          }
        }
      }
    }
  }
  
  // Enhanced extraction from feature bullets and descriptions
  const contentSelectors = [
    "#feature-bullets ul li span",
    "#productDescription p",
    ".a-section .a-spacing-medium span",
    "[data-feature-name='featurebullets'] span"
  ];
  
  for (const selector of contentSelectors) {
    const elements = document.querySelectorAll(selector);
    for (const element of elements) {
      const text = element.innerText.toLowerCase();
      
      // Look for detailed material descriptions
      const materialPatterns = [
        /(?:made (?:of|from)|material:?\s*|fabric:?\s*|composition:?\s*)([a-z\s,&%-]+)/i,
        /(?:genuine|real|authentic)\s+(leather|suede|silk|wool|cotton|linen)/i,
        /(\w+)\s+leather/i,
        /(\w+)\s+cotton/i,
        /(recycled|organic|sustainable)\s+(\w+)/i,
        /(?:upper|outer|shell):?\s*([a-z\s,&%-]+)/i
      ];
      
      for (const pattern of materialPatterns) {
        const match = text.match(pattern);
        if (match) {
          const material = match[1] || match[2] || match[0];
          if (material && material.length > 2) {
            console.log("✅ Found detailed material:", material.trim());
            foundMaterials.push(material.trim());
          }
        }
      }
    }
  }
  
  // Return the most detailed/specific material found
  if (foundMaterials.length > 0) {
    // Sort by length (longer = more specific) and return the most specific
    foundMaterials.sort((a, b) => b.length - a.length);
    return foundMaterials[0];
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
  
  let foundMaterials = [];
  
  for (const container of containers) {
    const text = container.innerText || "";
    
    // Enhanced material patterns for more specific detection
    const materialPatterns = [
      /Material Type[:\s]*([A-Za-z,\s&%-]+)/i,
      /Material[:\s]*([A-Za-z,\s&%-]+)/i,
      /Made (?:of|from)[:\s]*([A-Za-z,\s&%-]+)/i,
      /Fabric[:\s]*([A-Za-z,\s&%-]+)/i,
      /(?:genuine|real|authentic)\s+(leather|suede|silk|wool|cotton|linen)/i,
      /(\w+)\s+leather/i,
      /(recycled|organic|sustainable|premium)\s+(\w+)/i,
      /(?:upper|outer|shell)[:\s]*([A-Za-z,\s&%-]+)/i,
      /(vegan|faux|synthetic)\s+(leather|suede)/i
    ];
    
    for (const pattern of materialPatterns) {
      const match = text.match(pattern);
      if (match) {
        const material = (match[1] || match[2] || match[0]).trim().toLowerCase();
        if (material.length > 2 && !material.includes('material')) {
          console.log("✅ Found material in tile:", material);
          foundMaterials.push(material);
        }
      }
    }
  }
  
  // Return most specific material found
  if (foundMaterials.length > 0) {
    foundMaterials.sort((a, b) => b.length - a.length);
    return foundMaterials[0];
  }
  
  return null;
}

async function smartGuessMaterialFromTitle(title) {
  const titleLower = title.toLowerCase();
  
  // Load material insights to get comprehensive list
  const insights = window.materialInsights || await window.loadMaterialInsights?.() || {};
  
  // Enhanced category-based guessing with material specificity
  const categoryPatterns = [
    // Leather products (with specific types)
    { patterns: ['genuine leather', 'real leather', 'full grain'], material: 'leather', priority: 20 },
    { patterns: ['suede', 'nubuck'], material: 'leather', priority: 19 },
    { patterns: ['vegan leather', 'faux leather', 'synthetic leather'], material: 'faux leather', priority: 18 },
    { patterns: ['patent leather'], material: 'leather', priority: 17 },
    
    // Bags & Backpacks (High Priority - prioritize nylon over aluminum)
    { patterns: ['backpack', 'rucksack', 'hiking backpack', 'travel backpack', 'daypack'], material: 'nylon', priority: 15 },
    { patterns: ['gym bag', 'sports bag', 'duffel bag', 'duffle bag'], material: 'nylon', priority: 14 },
    { patterns: ['laptop bag', 'briefcase', 'computer bag'], material: 'nylon', priority: 13 },
    { patterns: ['hiking pack', 'climbing pack', 'outdoor pack'], material: 'nylon', priority: 14 },
    { patterns: ['leather bag', 'leather handbag'], material: 'leather', priority: 12 },
    { patterns: ['bag', 'handbag', 'shoulder bag', 'tote bag'], material: 'leather', priority: 9 },
    
    // Textiles & Clothing (with specific material detection)
    { patterns: ['organic cotton', '100% cotton'], material: 'cotton', priority: 16 },
    { patterns: ['recycled polyester', 'eco polyester'], material: 'recycled polyester', priority: 15 },
    { patterns: ['merino wool', 'pure wool'], material: 'wool', priority: 15 },
    { patterns: ['cashmere'], material: 'cashmere', priority: 15 },
    { patterns: ['silk'], material: 'silk', priority: 14 },
    { patterns: ['linen'], material: 'linen', priority: 14 },
    { patterns: ['t-shirt', 'shirt', 'tee', 'top'], material: 'cotton', priority: 10 },
    { patterns: ['jeans', 'denim'], material: 'cotton', priority: 10 },
    { patterns: ['jacket', 'coat', 'hoodie', 'sweater'], material: 'polyester', priority: 9 },
    { patterns: ['pants', 'trousers', 'leggings'], material: 'cotton', priority: 8 },
    { patterns: ['dress', 'skirt'], material: 'polyester', priority: 8 },
    { patterns: ['socks', 'underwear'], material: 'cotton', priority: 9 },
    { patterns: ['leather shoes', 'leather boots'], material: 'leather', priority: 12 },
    { patterns: ['shoes', 'sneakers', 'trainers', 'boots'], material: 'leather', priority: 8 },
    
    // Electronics (with specific plastic types)
    { patterns: ['silicone case', 'silicone cover'], material: 'silicone', priority: 12 },
    { patterns: ['tpu case'], material: 'polyurethane', priority: 12 },
    { patterns: ['polycarbonate case'], material: 'polycarbonate', priority: 12 },
    { patterns: ['abs plastic'], material: 'abs', priority: 12 },
    { patterns: ['headphones', 'earbuds', 'earphones'], material: 'plastics', priority: 8 },
    { patterns: ['phone case', 'case', 'cover', 'protector'], material: 'plastics', priority: 9 },
    { patterns: ['laptop', 'macbook', 'ultrabook', 'notebook computer'], material: 'aluminum', priority: 7 },
    { patterns: ['charger', 'cable', 'adapter', 'cord'], material: 'plastics', priority: 8 },
    { patterns: ['speaker', 'soundbar'], material: 'plastics', priority: 7 },
    { patterns: ['tablet', 'ipad'], material: 'aluminum', priority: 7 },
    
    // Home & Kitchen (with material specificity)
    { patterns: ['stainless steel bottle', 'steel bottle'], material: 'steel', priority: 12 },
    { patterns: ['glass bottle', 'borosilicate'], material: 'glass', priority: 12 },
    { patterns: ['bamboo cutting board'], material: 'bamboo', priority: 12 },
    { patterns: ['wooden cutting board'], material: 'timber', priority: 11 },
    { patterns: ['ceramic mug', 'porcelain'], material: 'ceramic', priority: 11 },
    { patterns: ['water bottle', 'bottle', 'flask', 'tumbler'], material: 'steel', priority: 8 },
    { patterns: ['mug', 'cup', 'glass'], material: 'ceramic', priority: 8 },
    { patterns: ['pan', 'pot', 'cookware', 'frying pan'], material: 'aluminum', priority: 8 },
    { patterns: ['cutting board', 'chopping board'], material: 'timber', priority: 9 },
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
    { patterns: ['drill', 'power tool'], material: 'plastics', priority: 7 },
    
    // Accessories
    { patterns: ['watch', 'smartwatch'], material: 'steel', priority: 7 },
    { patterns: ['sunglasses', 'glasses'], material: 'plastics', priority: 8 },
    { patterns: ['wallet', 'purse'], material: 'leather', priority: 8 },
    { patterns: ['belt'], material: 'leather', priority: 8 },
    
    // Books & Media
    { patterns: ['book', 'paperback', 'hardcover'], material: 'paper', priority: 9 },
    { patterns: ['notebook', 'journal', 'diary'], material: 'paper', priority: 8 },
    
    // Beauty & Personal Care
    { patterns: ['brush', 'comb'], material: 'plastics', priority: 7 },
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
    { patterns: ['wooden', 'wood'], material: 'timber' },
    { patterns: ['metal', 'metallic'], material: 'steel' },
    { patterns: ['plastic'], material: 'plastics' },
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
  if (confidence < 25) {
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

  // Enhanced tooltip with confidence indicator and material specificity
  const confidenceColor = confidence >= 80 ? "#10b981" 
                         : confidence >= 60 ? "#f59e0b" 
                         : "#ef4444";

  // Enhanced material name display
  const materialName = info.name;
  const isSpecificMaterial = info.isSpecific || materialName.includes(' ') || 
                           ['faux leather', 'recycled', 'organic', 'vegan', 'genuine'].some(prefix => 
                           materialName.toLowerCase().includes(prefix));
  
  const materialIcon = isSpecificMaterial ? "🎯" : "🧬";
  const specificityNote = isSpecificMaterial ? 
    `<div style="font-size: 10px; color: #10b981; margin-top: 2px;">✨ Specific material type detected</div>` : 
    `<div style="font-size: 10px; color: #888; margin-top: 2px;">📈 General material category</div>`;

  // Look for related materials to suggest alternatives
  const relatedMaterials = findRelatedMaterials(materialName);
  const relatedSection = relatedMaterials.length > 0 ? 
    `<div style="font-size: 11px; color: #94a3b8; margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.1);">
      <strong>🔗 Related materials:</strong> ${relatedMaterials.slice(0, 3).join(', ')}
    </div>` : '';

  const html = `
    <div style="border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 8px; margin-bottom: 8px;">
      <strong>${materialIcon} Material: ${capitalizeFirst(materialName)}</strong>
      ${specificityNote}
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
    ${relatedSection}
  `;

  attachTooltipEvents(target, html);
}

// Helper function to find related materials
function findRelatedMaterials(materialName) {
  const insights = window.materialInsights || {};
  const baseName = materialName.toLowerCase();
  const related = [];
  
  // Define material families
  const families = {
    leather: ['leather', 'suede', 'faux leather', 'vegan leather', 'mushroom leather', 'apple leather'],
    plastic: ['plastic', 'pvc', 'abs', 'polycarbonate', 'polyethylene', 'bioplastic'],
    cotton: ['cotton', 'organic cotton', 'recycled cotton'],
    metal: ['aluminum', 'steel', 'brass', 'copper'],
    wood: ['timber', 'bamboo', 'cork']
  };
  
  // Find which family the current material belongs to
  for (const [family, materials] of Object.entries(families)) {
    if (materials.some(m => baseName.includes(m) || m.includes(baseName))) {
      // Add other materials from the same family
      for (const material of materials) {
        if (material !== baseName && insights[material] && !related.includes(material)) {
          related.push(material);
        }
      }
      break;
    }
  }
  
  return related;
}

// Helper function to capitalize first letter
function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

async function enhanceTooltips() {
  console.log("✅ Enhanced tooltip script running");
  
  // Only clean up orphaned tooltips (not attached to any element)
  const allTooltips = document.querySelectorAll('.eco-tooltip');
  const attachedTooltips = new Set();
  
  // Find tooltips that are still attached to elements
  document.querySelectorAll('[data-enhanced-tooltip-attached="true"]').forEach(el => {
    if (el._ecoTooltip) {
      attachedTooltips.add(el._ecoTooltip);
    }
  });
  
  // Remove only orphaned tooltips
  allTooltips.forEach(tooltip => {
    if (!attachedTooltips.has(tooltip)) {
      tooltip.remove();
    }
  });
  
  // Don't clean up working tooltips - only fix broken ones in attachTooltipEvents
  
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
             el.dataset.enhancedTooltipAttached !== "true" && // Prevent duplicates from enhanced system
             // Remove duplicates based on text content
             arr.findIndex(other => other.textContent.trim() === text) === index &&
             // Exclude navigation and UI elements
             !text.toLowerCase().includes('see more') &&
             !text.toLowerCase().includes('view details') &&
             !text.toLowerCase().includes('add to cart') &&
             !text.toLowerCase().includes('check each product page');
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
let isEnhancing = false;
const DEBOUNCE_MS = 1500; // Reduced for more responsiveness
const MIN_INTERVAL_MS = 500; // Minimum time between enhancements

function debouncedEnhanceTooltips() {
  const now = Date.now();
  
  // Don't run if already enhancing
  if (isEnhancing) {
    console.log("⏳ Enhancement already in progress, skipping");
    return;
  }
  
  // Don't run too frequently
  if (now - lastEnhanceRun < MIN_INTERVAL_MS) {
    if (enhanceTimeout) {
      clearTimeout(enhanceTimeout);
    }
    enhanceTimeout = setTimeout(() => {
      debouncedEnhanceTooltips();
    }, MIN_INTERVAL_MS - (now - lastEnhanceRun));
    return;
  }
  
  if (now - lastEnhanceRun > DEBOUNCE_MS) {
    lastEnhanceRun = now;
    isEnhancing = true;
    enhanceTooltips().catch(console.error).finally(() => {
      isEnhancing = false;
    });
  } else {
    // Clear existing timeout and set a new one
    if (enhanceTimeout) {
      clearTimeout(enhanceTimeout);
    }
    enhanceTimeout = setTimeout(() => {
      lastEnhanceRun = Date.now();
      isEnhancing = true;
      enhanceTooltips().catch(console.error).finally(() => {
        isEnhancing = false;
      });
    }, DEBOUNCE_MS);
  }
}

// Smart initialization without aggressive cleanup
let pageInitialized = false;

// Cleanup broken tooltips on page unload
window.addEventListener("beforeunload", cleanupBrokenTooltips);

// Initialize on page load
window.addEventListener("load", () => {
  if (!pageInitialized) {
    pageInitialized = true;
    cleanupBrokenTooltips();
    setTimeout(debouncedEnhanceTooltips, 1000);
  }
});

// Also initialize on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (!pageInitialized) {
      pageInitialized = true;
      cleanupBrokenTooltips();
      setTimeout(debouncedEnhanceTooltips, 500);
    }
  });
} else if (!pageInitialized) {
  pageInitialized = true;
  cleanupBrokenTooltips();
  debouncedEnhanceTooltips();
}

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
