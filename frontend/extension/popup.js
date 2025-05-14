document.getElementById("analyze").addEventListener("click", async () => {
  const url = document.getElementById("amazon_url").value;
  const postcode = document.getElementById("postcode").value;
  const output = document.getElementById("output");

  if (!url || !postcode) {
    output.textContent = "Please enter both URL and postcode.";
    return;
  }

  const BASE_URL = 
    typeof window !== "undefined" && window.location.hostname === "localhost"
      ? "http://localhost:5000"
      : "https://dsp-environmentaltracker-1.onrender.com";

  try {
    const res = await fetch(`${BASE_URL}/estimate_emissions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amazon_url: url,
        postcode: postcode,
        include_packaging: true
      })
    });

    const json = await res.json();

    if (json?.data?.attributes) {
      const a = json.data.attributes;
      console.log("✅ Full response:", a);
      alert("Rule-based score: " + a.eco_score_rule_based);

      // Optional: truncate very long material names
      const truncate = (text, len = 40) =>
        text?.length > len ? text.slice(0, len) + "…" : text;

      // Optional: emoji map for eco score
      const emoji = {
        "A+": "🌍", "A": "🌿", "B": "🍃",
        "C": "🌱", "D": "⚠️", "E": "❌", "F": "💀"
      };

      output.innerHTML = `
        <strong>Eco Score (ML):</strong> ${a.eco_score_ml || "N/A"} ${emoji[a.eco_score_ml] || ""}<br/>
        <strong>Confidence:</strong> ${a.eco_score_confidence ?? "N/A"}%<br/>
        <strong>Eco Score (Rule-Based):</strong> ${a.eco_score_rule_based || "N/A"} ${emoji[a.eco_score_rule_based] || ""}<br/>
        <strong>Material Type:</strong> ${truncate(a.material_type || "Unknown")}<br/>
        <strong>Transport Mode:</strong> ${a.transport_mode || "N/A"}<br/>
        <strong>Weight (incl. packaging):</strong> ${a.weight_kg || "N/A"} kg<br/>
        <strong>Carbon Emissions:</strong> ${a.carbon_kg || "N/A"} kg CO₂<br/>
        <strong>Distance from Origin:</strong> ${a.distance_from_origin_km || "N/A"} km<br/>
        <strong>Distance from UK Hub:</strong> ${a.distance_from_uk_hub_km || "N/A"} km
      `;
    } else {
      output.textContent = "No data received.";
    }
  } catch (err) {
    output.textContent = "Error contacting API.";
    console.error("❌ Fetch error:", err);
  }
});
