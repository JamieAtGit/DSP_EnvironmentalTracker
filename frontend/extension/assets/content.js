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

// Enhanced material type detection function with comprehensive families
function detectSpecificMaterialType(materialHint, data) {
  if (!materialHint) return null;
  
  const hint = materialHint.toLowerCase();
  
  // Define comprehensive material families and their specific types
  const materialFamilies = {
    // METALS - Comprehensive metal family
    metals: {
      'precious_metals': ['gold', 'silver', 'platinum', 'palladium'],
      'common_metals': ['aluminum', 'aluminium', 'steel', 'iron', 'copper', 'brass', 'bronze', 'zinc', 'tin', 'lead'],
      'specialty_metals': ['titanium', 'titanium alloys', 'stainless steel', 'carbon steel', 'tool steel', 'low-alloy steel', 'cast iron', 'nickel alloys'],
      'metal_composites': ['metal', 'alloy', 'metallic']
    },
    
    // POLYMERS - Reorganized and expanded polymer family
    polymers: {
      'thermoplastics': ['polyethylene', 'polypropylene', 'polystyrene', 'pvc', 'abs', 'polycarbonate', 'pmma', 'acrylic'],
      'thermosets': ['polyurethane', 'epoxy', 'phenolic', 'ptfe'],
      'bio_polymers': ['pla', 'pha', 'pbat', 'bioplastic'],
      'recycled_polymers': ['recovered plastic', 'recycled plastic', 'plastics'],
      'specialty_polymers': ['kevlar', 'qmonos', 'vinyl']
    },
    
    // ELASTOMERS - Rubber and elastic materials
    elastomers: {
      'natural_rubber': ['rubber', 'natural rubber', 'latex'],
      'synthetic_elastomers': ['silicone', 'neoprene', 'epdm', 'reclaimed rubber'],
      'elastic_fibers': ['elastane', 'spandex', 'lycra']
    },
    
    // CERAMICS - Clay-based and technical ceramics
    ceramics: {
      'traditional_ceramics': ['ceramic', 'ceramics', 'porcelain', 'stoneware', 'earthenware', 'terracotta'],
      'construction_ceramics': ['brick', 'tile', 'clay'],
      'technical_ceramics': ['alumina', 'zirconia', 'silicon carbide']
    },
    
    // GLASSES - Various glass types
    glasses: {
      'common_glass': ['glass', 'tempered glass', 'laminated glass'],
      'specialty_glass': ['borosilicate', 'optical glass', 'crystal'],
      'glass_composites': ['fiberglass', 'glass fiber']
    },
    
    // STONE/MINERAL - Natural and processed stone materials
    stone_mineral: {
      'natural_stone': ['granite', 'marble', 'limestone', 'sandstone', 'slate', 'stone', 'quartz'],
      'processed_stone': ['concrete', 'cement', 'terrazzo', 'plaster']
    },
    
    // TEXTILES - Comprehensive textile families
    textiles: {
      'natural_plant_fibers': ['cotton', 'linen', 'hemp', 'jute', 'ramie', 'sisal', 'abaca', 'nettle fiber', 'coir', 'coconut fiber'],
      'natural_animal_fibers': ['wool', 'silk', 'cashmere', 'alpaca', 'mohair', 'merino wool', 'down', 'angora'],
      'synthetic_fibers': ['polyester', 'nylon', 'acrylic', 'spandex', 'elastane', 'lycra', 'viscose', 'rayon', 'modal', 'lyocell', 'lyocell tencel'],
      'innovative_bio_fibers': ['milk fiber', 'orange fiber', 'rose fiber', 'soy fabric', 'lotus fiber', 'seacell', 'econyl', 's.cafe'],
      'recycled_textiles': ['recycled cotton', 'recycled polyester', 'recycled wool', 'recycled nylon'],
      'fabric_constructions': ['denim', 'canvas', 'velvet', 'satin', 'chiffon', 'georgette', 'organza', 'tulle', 'corduroy', 'flannel', 'fleece', 'jersey', 'crepe', 'seersucker']
    },
    
    // LEATHER - Expanded leather family
    leather: {
      'genuine_leather': ['leather', 'genuine leather', 'real leather', 'full grain leather', 'top grain leather', 'nubuck', 'suede', 'patent leather'],
      'alternative_leather': ['faux leather', 'vegan leather', 'synthetic leather', 'pleather'],
      'innovative_leather': ['mushroom leather', 'mycelium', 'apple leather', 'grape leather', 'cactus leather', 'palm leather', 'piñatex'],
      'recycled_leather': ['recycled leather', 'bonded leather']
    },
    
    // WOOD/PLANT - Wood and plant-based materials
    wood_plant: {
      'solid_wood': ['timber', 'wood', 'lumber', 'hardwood', 'softwood'],
      'engineered_wood': ['plywood', 'mdf', 'chipboard', 'osb', 'oriented strand board'],
      'sustainable_wood': ['bamboo', 'cork', 'reclaimed wood', 'rattan'],
      'plant_materials': ['kapok', 'bagasse', 'rice hulls', 'wheat straw', 'sunflower hulls']
    },
    
    // PAPER/CELLULOSE - Paper-based materials
    paper_cellulose: {
      'paper_products': ['paper', 'cardboard', 'wood pulp'],
      'specialty_paper': ['tapa cloth', 'kraft paper']
    },
    
    // COMPOSITES/HYBRIDS - Advanced composite materials
    composites: {
      'fiber_composites': ['carbon fiber', 'fiberglass', 'kevlar', 'aramid'],
      'bio_composites': ['bananatex', 'hemp composite'],
      'engineered_composites': ['composite', 'hybrid material']
    },
    
    // CONSTRUCTION - Building and construction materials
    construction: {
      'structural': ['concrete', 'cement', 'brick', 'drywall', 'plaster'],
      'finishing': ['paint', 'paints', 'water-based paint', 'roofing', 'siding', 'insulation'],
      'adhesives': ['adhesives', 'glues', 'epoxy']
    },
    
    // CHEMICAL/PROCESSING - Chemical and processing materials
    chemical: {
      'processing_agents': ['dyeing agents', 'tanning agents'],
      'surface_materials': ['linoleum', 'sanding dust']
    }
  };
  
  // Check for specific material types across all families
  for (const [familyName, subcategories] of Object.entries(materialFamilies)) {
    for (const [subcategoryName, types] of Object.entries(subcategories)) {
      for (const type of types) {
        if (hint.includes(type) && data[type]) {
          console.log(`🎯 Found specific ${familyName} (${subcategoryName}):`, type);
          return { 
            material: type, 
            confidence: 95, 
            isSpecific: true, 
            family: familyName,
            subcategory: subcategoryName 
          };
        }
      }
    }
  }
  
  // Enhanced compound material detection with comprehensive patterns
  const compoundPatterns = [
    // Metal compounds
    /(stainless|carbon|tool|low-alloy)\s+steel/,
    /(titanium|nickel|aluminum)\s+(alloy|alloys)/,
    /(cast|wrought)\s+iron/,
    
    // Polymer compounds
    /(recycled|bio|recovered)\s+(plastic|polymer)/,
    /(thermoplastic|thermoset)\s+(\w+)/,
    
    // Textile compounds
    /(organic|recycled|sustainable|premium)\s+(cotton|wool|silk|polyester|nylon)/,
    /(merino|cashmere|alpaca|mohair)\s+wool/,
    /(genuine|real|authentic|full\s+grain|top\s+grain)\s+(leather)/,
    /(vegan|faux|synthetic|artificial)\s+(leather|suede)/,
    /(recycled|organic)\s+(cotton|polyester|wool|nylon)/,
    
    // Glass compounds
    /(tempered|laminated|borosilicate)\s+glass/,
    /(fiber|fibre)\s+glass/,
    
    // Wood compounds
    /(reclaimed|engineered|solid)\s+(wood|timber)/,
    /(oriented\s+strand|particle)\s+board/,
    
    // Stone compounds
    /(natural|artificial|engineered)\s+(stone|marble|granite)/,
    
    // Ceramic compounds
    /(technical|advanced|traditional)\s+(ceramic|ceramics)/,
    
    // General modifiers
    /(premium|high-grade|industrial|medical-grade|food-grade)\s+(\w+)/,
    /(\w+)\s+(fiber|fibre|composite|blend)/
  ];
  
  for (const pattern of compoundPatterns) {
    const match = hint.match(pattern);
    if (match) {
      const compound = match[0].trim();
      const modifier = match[1];
      const base = match[2] || match[1];
      
      // Check if we have the specific compound material
      if (data[compound]) {
        console.log('🧬 Found compound material:', compound);
        return { 
          material: compound, 
          confidence: 90, 
          isSpecific: true,
          compound: true,
          modifier: modifier
        };
      }
      
      // Check for close matches in our database
      const closeMatches = Object.keys(data).filter(key => 
        key.toLowerCase().includes(compound.toLowerCase()) || 
        compound.toLowerCase().includes(key.toLowerCase())
      );
      
      if (closeMatches.length > 0) {
        const bestMatch = closeMatches[0];
        console.log('🔍 Found close compound match:', compound, '→', bestMatch);
        return { 
          material: bestMatch, 
          confidence: 85, 
          isSpecific: true,
          compound: true,
          originalHint: compound
        };
      }
      
      // Fall back to base material
      if (base && data[base]) {
        console.log('🔄 Using base material for compound:', compound, '→', base);
        return { 
          material: base, 
          confidence: 75, 
          isSpecific: false,
          compound: true,
          baseOf: compound
        };
      }
    }
  }
  
  return null;
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

    // Priority 1: Try to detect specific material type first
    if (materialHint && materialHint !== "unknown") {
      const specificResult = detectSpecificMaterialType(materialHint, data);
      if (specificResult) {
        return { 
          ...data[specificResult.material], 
          name: specificResult.material, 
          confidence: specificResult.confidence,
          isSpecific: specificResult.isSpecific,
          family: specificResult.family,
          subcategory: specificResult.subcategory,
          compound: specificResult.compound,
          modifier: specificResult.modifier,
          originalHint: specificResult.originalHint,
          baseOf: specificResult.baseOf
        };
      }
      
      // Enhanced exact matching
      for (const key in data) {
        if (materialHint.includes(key.toLowerCase()) || key.toLowerCase().includes(materialHint)) {
          console.log("✅ Matched from material hint:", key);
          return { ...data[key], name: key, confidence: 95 };
        }
      }
      
      // Enhanced fallback mapping for common mismatches
      const materialFallbacks = {
        'polycarbonate': 'plastics',
        'plastic': 'plastics', 
        'pvc': 'pvc',
        'abs': 'abs',
        'polyethylene': 'polyethylene',
        'polypropylene': 'polypropylene',
        'metal': 'steel',
        'metallic': 'aluminum',
        'wood': 'timber',
        'fabric': 'cotton',
        'cloth': 'cotton',
        'synthetic': 'polyester',
        'genuine': 'leather',
        'real leather': 'leather',
        'suede': 'leather'
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
};// Smart cleanup function - only cleans up broken/orphaned tooltips
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
    position: absolute;
    z-index: 99999;
    background: rgba(0, 0, 0, 0.92);
    color: white;
    padding: 15px;
    border-radius: 8px;
    font-size: 13px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
    line-height: 1.5;
    max-width: 320px;
    min-width: 200px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.15);
    pointer-events: none;
    word-wrap: break-word;
    visibility: hidden;
    opacity: 0;
    display: none;
    transition: opacity 0.3s ease, visibility 0.3s ease;
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
  
  console.log("🎯 Attaching tooltip to:", target.textContent.substring(0, 50));
  
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
    
    // Hide other visible tooltips
    document.querySelectorAll('.eco-tooltip.visible').forEach(t => {
      if (t !== tooltip) {
        t.classList.remove('visible');
      }
    });
    
    const rect = target.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
    
    // Better positioning with bounds checking
    let top = rect.bottom + scrollTop + 10;
    let left = rect.left + scrollLeft;
    
    // Keep tooltip within viewport
    if (left + 320 > window.innerWidth) {
      left = window.innerWidth - 340;
    }
    if (left < 10) {
      left = 10;
    }
    
    // If tooltip would go below viewport, show above instead
    if (top + 200 > window.innerHeight + scrollTop) {
      top = rect.top + scrollTop - 10;
      // Position above element
      const tooltipHeight = 150; // Approximate height
      top = top - tooltipHeight;
    }
    
    // Ensure tooltip is positioned and visible
    tooltip.style.top = `${top}px`;
    tooltip.style.left = `${left}px`;
    tooltip.style.visibility = 'visible';
    tooltip.style.display = 'block';
    tooltip.style.opacity = '1';
    
    // Add visible class for CSS
    tooltip.classList.add('visible');
    
    console.log("🟢 Enhanced tooltip showing at:", { top, left });
  };

  const mouseLeaveHandler = () => {
    console.log("🔴 Mouse left tooltip target");
    tooltip.classList.remove('visible');
    tooltip.style.opacity = '0';
    tooltip.style.visibility = 'hidden';
    // Small delay before hiding to prevent flicker
    setTimeout(() => {
      if (!tooltip.classList.contains('visible')) {
        tooltip.style.display = 'none';
      }
    }, 300);
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
  
  // Enhanced category-based guessing with comprehensive material families
  const categoryPatterns = [
    // LEATHER PRODUCTS (Comprehensive leather detection)
    { patterns: ['genuine leather', 'real leather', 'full grain leather', 'top grain leather'], material: 'leather', priority: 22 },
    { patterns: ['suede', 'nubuck', 'patent leather'], material: 'leather', priority: 21 },
    { patterns: ['vegan leather', 'faux leather', 'synthetic leather', 'pleather'], material: 'faux leather', priority: 20 },
    { patterns: ['mushroom leather', 'mycelium leather'], material: 'mushroom leather', priority: 20 },
    { patterns: ['apple leather', 'grape leather', 'cactus leather'], material: 'apple leather', priority: 20 },
    { patterns: ['recycled leather', 'bonded leather'], material: 'recycled leather', priority: 19 },
    
    // METALS (Comprehensive metal detection)
    { patterns: ['stainless steel', 'surgical steel'], material: 'stainless steel', priority: 22 },
    { patterns: ['carbon steel', 'high carbon steel'], material: 'carbon steel', priority: 21 },
    { patterns: ['titanium alloy', 'titanium'], material: 'titanium alloys', priority: 21 },
    { patterns: ['cast iron', 'wrought iron'], material: 'cast iron', priority: 20 },
    { patterns: ['brass', 'bronze', 'copper'], material: 'brass', priority: 19 },
    
    // BAGS & BACKPACKS (High Priority - prioritize nylon over aluminum)
    { patterns: ['backpack', 'rucksack', 'hiking backpack', 'travel backpack', 'daypack'], material: 'nylon', priority: 18 },
    { patterns: ['gym bag', 'sports bag', 'duffel bag', 'duffle bag'], material: 'nylon', priority: 17 },
    { patterns: ['laptop bag', 'briefcase', 'computer bag'], material: 'nylon', priority: 16 },
    { patterns: ['hiking pack', 'climbing pack', 'outdoor pack'], material: 'nylon', priority: 17 },
    { patterns: ['leather bag', 'leather handbag', 'leather purse'], material: 'leather', priority: 15 },
    { patterns: ['canvas bag', 'canvas backpack'], material: 'canvas', priority: 14 },
    { patterns: ['bag', 'handbag', 'shoulder bag', 'tote bag'], material: 'leather', priority: 9 },
    
    // TEXTILES & CLOTHING (Comprehensive textile detection)
    // Natural Plant Fibers
    { patterns: ['organic cotton', '100% cotton', 'pure cotton'], material: 'cotton', priority: 18 },
    { patterns: ['recycled cotton', 'sustainable cotton'], material: 'recycled cotton', priority: 17 },
    { patterns: ['linen', 'flax', 'irish linen'], material: 'linen', priority: 17 },
    { patterns: ['hemp', 'hemp fiber', 'industrial hemp'], material: 'hemp', priority: 17 },
    { patterns: ['jute', 'burlap', 'hessian'], material: 'jute', priority: 16 },
    { patterns: ['bamboo fiber', 'bamboo fabric'], material: 'bamboo', priority: 16 },
    
    // Animal Fibers  
    { patterns: ['merino wool', 'pure wool', 'virgin wool'], material: 'merino wool', priority: 18 },
    { patterns: ['cashmere', 'kashmir wool'], material: 'cashmere', priority: 18 },
    { patterns: ['alpaca', 'alpaca wool'], material: 'alpaca', priority: 17 },
    { patterns: ['mohair', 'angora mohair'], material: 'mohair', priority: 17 },
    { patterns: ['silk', 'mulberry silk', 'pure silk'], material: 'silk', priority: 17 },
    { patterns: ['down', 'goose down', 'duck down'], material: 'down', priority: 16 },
    
    // Synthetic Fibers
    { patterns: ['recycled polyester', 'eco polyester', 'rPET'], material: 'recycled polyester', priority: 17 },
    { patterns: ['recycled nylon', 'econyl'], material: 'recycled nylon', priority: 17 },
    { patterns: ['lyocell', 'tencel', 'modal'], material: 'lyocell tencel', priority: 16 },
    { patterns: ['viscose', 'rayon'], material: 'viscose', priority: 15 },
    
    // Clothing Items
    { patterns: ['denim jeans', 'denim jacket'], material: 'denim', priority: 15 },
    { patterns: ['canvas shoes', 'canvas sneakers'], material: 'canvas', priority: 14 },
    { patterns: ['t-shirt', 'shirt', 'tee', 'top'], material: 'cotton', priority: 10 },
    { patterns: ['jeans', 'denim'], material: 'denim', priority: 10 },
    { patterns: ['jacket', 'coat', 'hoodie', 'sweater'], material: 'polyester', priority: 9 },
    { patterns: ['pants', 'trousers', 'leggings'], material: 'cotton', priority: 8 },
    { patterns: ['dress', 'skirt'], material: 'polyester', priority: 8 },
    { patterns: ['socks', 'underwear'], material: 'cotton', priority: 9 },
    { patterns: ['leather shoes', 'leather boots'], material: 'leather', priority: 12 },
    { patterns: ['shoes', 'sneakers', 'trainers', 'boots'], material: 'leather', priority: 8 },
    
    // ELECTRONICS & TECH (Comprehensive tech material detection)
    // Phone Cases & Accessories
    { patterns: ['silicone case', 'silicone cover', 'silicone protector'], material: 'silicone', priority: 16 },
    { patterns: ['tpu case', 'thermoplastic polyurethane'], material: 'polyurethane', priority: 16 },
    { patterns: ['polycarbonate case', 'pc case'], material: 'polycarbonate', priority: 16 },
    { patterns: ['abs case', 'abs plastic case'], material: 'abs', priority: 16 },
    { patterns: ['leather case', 'leather phone case'], material: 'leather', priority: 15 },
    { patterns: ['aluminum case', 'metal case'], material: 'aluminum', priority: 15 },
    
    // Devices
    { patterns: ['titanium watch', 'titanium phone'], material: 'titanium alloys', priority: 16 },
    { patterns: ['stainless steel watch', 'steel watch'], material: 'stainless steel', priority: 15 },
    { patterns: ['carbon fiber case', 'carbon fiber phone'], material: 'carbon fiber', priority: 15 },
    { patterns: ['ceramic watch', 'ceramic phone'], material: 'ceramic', priority: 14 },
    { patterns: ['headphones', 'earbuds', 'earphones'], material: 'plastics', priority: 8 },
    { patterns: ['phone case', 'case', 'cover', 'protector'], material: 'plastics', priority: 9 },
    { patterns: ['laptop', 'macbook', 'ultrabook', 'notebook computer'], material: 'aluminum', priority: 7 },
    { patterns: ['charger', 'cable', 'adapter', 'cord'], material: 'plastics', priority: 8 },
    { patterns: ['speaker', 'soundbar'], material: 'plastics', priority: 7 },
    { patterns: ['tablet', 'ipad'], material: 'aluminum', priority: 7 },
    
    // HOME & KITCHEN (Comprehensive home goods detection)
    // Drinkware
    { patterns: ['stainless steel bottle', 'steel water bottle', 'insulated steel'], material: 'stainless steel', priority: 17 },
    { patterns: ['glass bottle', 'borosilicate glass', 'tempered glass'], material: 'glass', priority: 16 },
    { patterns: ['ceramic mug', 'porcelain mug', 'stoneware mug'], material: 'ceramic', priority: 16 },
    { patterns: ['bamboo tumbler', 'bamboo cup'], material: 'bamboo', priority: 15 },
    { patterns: ['silicone bottle', 'collapsible bottle'], material: 'silicone', priority: 14 },
    
    // Cookware  
    { patterns: ['cast iron pan', 'cast iron skillet'], material: 'cast iron', priority: 17 },
    { patterns: ['stainless steel pan', 'steel cookware'], material: 'stainless steel', priority: 16 },
    { patterns: ['carbon steel pan', 'carbon steel wok'], material: 'carbon steel', priority: 16 },
    { patterns: ['ceramic cookware', 'ceramic pan'], material: 'ceramic', priority: 15 },
    { patterns: ['copper cookware', 'copper pan'], material: 'copper', priority: 15 },
    
    // Cutting Boards
    { patterns: ['bamboo cutting board', 'bamboo chopping board'], material: 'bamboo', priority: 16 },
    { patterns: ['wooden cutting board', 'wood chopping board'], material: 'timber', priority: 15 },
    { patterns: ['plastic cutting board', 'polyethylene board'], material: 'polyethylene', priority: 14 },
    
    // General Items
    { patterns: ['water bottle', 'bottle', 'flask', 'tumbler'], material: 'stainless steel', priority: 8 },
    { patterns: ['mug', 'cup'], material: 'ceramic', priority: 8 },
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

  // Enhanced material name display with family information
  const materialName = info.name;
  const isSpecificMaterial = info.isSpecific || materialName.includes(' ') || 
                           ['faux leather', 'recycled', 'organic', 'vegan', 'genuine', 'stainless', 'carbon'].some(prefix => 
                           materialName.toLowerCase().includes(prefix));
  
  // Enhanced material categorization with family info
  const familyInfo = info.family ? ` (${info.family.replace('_', ' ')})` : '';
  const subcategoryInfo = info.subcategory ? ` - ${info.subcategory.replace('_', ' ')}` : '';
  
  // Material type icons based on family
  const familyIcons = {
    metals: '🔩',
    polymers: '🧪',
    elastomers: '🔄',
    ceramics: '🏺',
    glasses: '🔍',
    stone_mineral: '🪨',
    textiles: '🧵',
    leather: '💼',
    wood_plant: '🌳',
    paper_cellulose: '📄',
    composites: '⚙️',
    construction: '🏠',
    chemical: '⚗️'
  };
  
  const materialIcon = info.family && familyIcons[info.family] ? familyIcons[info.family] : 
                      (isSpecificMaterial ? "🎯" : "🧬");
  
  const specificityNote = isSpecificMaterial ? 
    `<div style="font-size: 10px; color: #10b981; margin-top: 2px;">✨ Specific material type detected${familyInfo}</div>` : 
    `<div style="font-size: 10px; color: #888; margin-top: 2px;">📈 General material category${familyInfo}</div>`;

  // Enhanced compound material info
  const compoundInfo = info.compound && info.originalHint ? 
    `<div style="font-size: 10px; color: #a78bfa; margin-top: 2px;">🧬 Detected from: "${info.originalHint}"</div>` : '';

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
      ${compoundInfo}
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

// Enhanced helper function to find related materials using comprehensive families
function findRelatedMaterials(materialName) {
  const insights = window.materialInsights || {};
  const baseName = materialName.toLowerCase();
  const related = [];
  
  // Define comprehensive material families for related materials
  const materialFamilies = {
    // METALS
    metals: ['aluminum', 'steel', 'stainless steel', 'carbon steel', 'titanium alloys', 'brass', 'copper', 'iron', 'zinc', 'tin'],
    
    // LEATHER FAMILY
    leather: ['leather', 'suede', 'faux leather', 'vegan leather', 'mushroom leather', 'apple leather', 'grape leather', 'cactus leather', 'palm leather', 'recycled leather'],
    
    // POLYMERS/PLASTICS
    polymers: ['plastics', 'polyethylene', 'polypropylene', 'polystyrene', 'pvc', 'abs', 'polycarbonate', 'polyurethane', 'bioplastic', 'recovered plastic', 'acrylic'],
    
    // NATURAL PLANT FIBERS
    plant_fibers: ['cotton', 'linen', 'hemp', 'jute', 'ramie', 'sisal', 'organic cotton', 'recycled cotton'],
    
    // ANIMAL FIBERS
    animal_fibers: ['wool', 'silk', 'cashmere', 'alpaca', 'mohair', 'merino wool', 'down'],
    
    // SYNTHETIC FIBERS
    synthetic_fibers: ['polyester', 'nylon', 'acrylic', 'spandex', 'viscose', 'rayon', 'recycled polyester', 'recycled nylon'],
    
    // ELASTOMERS
    elastomers: ['rubber', 'silicone', 'elastane', 'spandex', 'reclaimed rubber'],
    
    // WOOD/PLANT MATERIALS
    wood_materials: ['timber', 'bamboo', 'cork', 'plywood', 'reclaimed wood', 'wood'],
    
    // CERAMICS
    ceramics: ['ceramic', 'ceramics', 'porcelain', 'stoneware', 'brick'],
    
    // GLASS
    glass_materials: ['glass', 'fiberglass'],
    
    // STONE/MINERAL
    stone_materials: ['granite', 'marble', 'limestone', 'concrete', 'cement', 'stone'],
    
    // PAPER/CELLULOSE
    paper_materials: ['paper', 'cardboard', 'wood pulp'],
    
    // COMPOSITES
    composites: ['carbon fiber', 'fiberglass', 'kevlar']
  };
  
  // Find which family the current material belongs to
  for (const [familyName, materials] of Object.entries(materialFamilies)) {
    const materialMatch = materials.find(m => {
      return baseName.includes(m) || m.includes(baseName) || 
             // Handle compound materials
             (baseName.includes(' ') && m.includes(baseName.split(' ')[0])) ||
             (m.includes(' ') && baseName.includes(m.split(' ')[0]));
    });
    
    if (materialMatch) {
      // Add other materials from the same family
      for (const material of materials) {
        if (material !== materialMatch && 
            material !== baseName && 
            insights[material] && 
            !related.includes(material)) {
          related.push(material);
        }
      }
      
      // Also look for variations with prefixes (recycled, organic, etc.)
      const baseMaterial = baseName.replace(/(recycled|organic|sustainable|premium|eco|bio)\s+/, '');
      const prefixes = ['recycled', 'organic', 'sustainable', 'eco', 'bio'];
      
      for (const prefix of prefixes) {
        const variation = `${prefix} ${baseMaterial}`;
        if (insights[variation] && !related.includes(variation) && variation !== baseName) {
          related.push(variation);
        }
      }
      
      break;
    }
  }
  
  // If no family match, look for direct variations
  if (related.length === 0) {
    const allMaterials = Object.keys(insights);
    const baseMaterial = baseName.replace(/(recycled|organic|sustainable|premium|eco|bio)\s+/, '');
    
    for (const material of allMaterials) {
      const materialLower = material.toLowerCase();
      if ((materialLower.includes(baseMaterial) || baseMaterial.includes(materialLower)) &&
          materialLower !== baseName &&
          related.length < 5) {
        related.push(material);
      }
    }
  }
  
  return related.slice(0, 4); // Limit to 4 related materials
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


// Extension loaded successfully
console.log("🌱 Environmental Tracker extension loaded - sophisticated tooltip system active");
