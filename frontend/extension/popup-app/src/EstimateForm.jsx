import { useEffect, useState } from "react";
import "./refined.css";

function smartGuessMaterial(title = "") {
  const lower = title.toLowerCase();
  const guesses = [
    { keywords: ["headphones", "earbuds"], material: "plastic" },
    { keywords: ["table", "desk", "shelf"], material: "wood" },
    { keywords: ["skateboard", "longboard"], material: "wood" },
    { keywords: ["fan", "air circulator"], material: "plastic" },
    { keywords: ["knife", "cutlery", "blade"], material: "steel" },
    { keywords: ["bottle", "jug"], material: "plastic" },
    { keywords: ["glass", "mirror", "window"], material: "glass" },
  ];
  for (const guess of guesses) {
    if (guess.keywords.some((kw) => lower.includes(kw))) {
      return guess.material;
    }
  }
  return null;
}

export default function EstimateForm() {
  const [userInputUrl, setUserInputUrl] = useState("");
  const [userPostcode, setUserPostcode] = useState(localStorage.getItem("postcode") || "");
  const [includePackaging, setIncludePackaging] = useState(true);
  const [selectedMode, setSelectedMode] = useState("Ship");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [productData, setProductData] = useState(null);
  const [equivalenceView, setEquivalenceView] = useState(0);
  const [materialInsights, setMaterialInsights] = useState({});

  useEffect(() => {
    fetch("/material_insights.json")
      .then((res) => res.json())
      .then(setMaterialInsights)
      .catch((err) => console.warn("Could not load material insights:", err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setProductData(null);
    localStorage.setItem("postcode", userPostcode);

    try {
      const res = await fetch("https://dsp-environmentaltracker-1.onrender.com/estimate_emissions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amazon_url: userInputUrl,
          postcode: userPostcode,
          include_packaging: includePackaging,
          override_transport_mode: selectedMode,
        }),
      });

      const data = await res.json();
      if (data.job_id) {
        checkJobStatus(data.job_id);
      } else {
        throw new Error("Failed to queue job");
      }
    } catch (err) {
      console.error("Submission error:", err);
      setError("Failed to submit estimate job.");
      setLoading(false);
    }
  };

  const checkJobStatus = async (jobId) => {
    try {
      const res = await fetch(`https://dsp-environmentaltracker-1.onrender.com/job_status/${jobId}`);
      const data = await res.json();

      if (data.status === "done") {
        setProductData(data.data);
        setLoading(false);
      } else if (data.status === "error") {
        setError("Scraping failed. Please try a different URL.");
        setLoading(false);
      } else {
        setTimeout(() => checkJobStatus(jobId), 3000);
      }
    } catch (err) {
      console.error("Polling error:", err);
      setError("Could not check job status.");
      setLoading(false);
    }
  };

  const attributes = productData?.data?.attributes || {};
  const productTitle = productData?.data?.title || productData?.title || "Untitled Product";

  const rawMaterial = attributes.material_type?.toLowerCase() || "other";
  let guessedMaterial = rawMaterial;
  if (guessedMaterial === "other" || guessedMaterial === "unknown") {
    const guess = smartGuessMaterial(productTitle);
    if (guess) guessedMaterial = guess;
  }

  const materialAliasMap = {
    plastics: "plastic",
    polyethylene: "plastic",
    aluminium: "aluminum",
    vegtan: "leather",
    "veg tan leather": "leather",
    "buffalo leather": "leather",
    cardboard: "paper",
  };

  const canonicalMaterial = materialAliasMap[guessedMaterial] || guessedMaterial;
  const materialInsight = materialInsights[canonicalMaterial];

  return (
    <div style={{ padding: "1rem" }}>
      <h2 className="text-center">Amazon Shipping <br /> Emissions Estimator</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: "1rem" }}>
        <input
          type="text"
          placeholder="Amazon product URL"
          value={userInputUrl}
          onChange={(e) => setUserInputUrl(e.target.value)}
        />
        <input
          type="text"
          placeholder="Enter your postcode"
          value={userPostcode}
          onChange={(e) => setUserPostcode(e.target.value)}
        />
        <label>
          <input
            type="checkbox"
            checked={includePackaging}
            onChange={(e) => setIncludePackaging(e.target.checked)}
          /> Include packaging weight
        </label>
        <label>
          Transport Mode:
          <select value={selectedMode} onChange={(e) => setSelectedMode(e.target.value)}>
            <option value="Ship">Ship 🚢</option>
            <option value="Air">Air ✈️</option>
            <option value="Truck">Truck 🚚</option>
          </select>
        </label>
        <button type="submit" disabled={loading}>
          {loading ? "Estimating..." : "Estimate Emissions"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {loading && <p>⏳ Scraping product and estimating emissions...</p>}

      {productData && (
        <div className="result-card">
          <div
            className="text-center"
            title={productTitle}
            style={{
              marginBottom: "8px",
              fontWeight: "bold",
              fontSize: "15px",
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
              maxWidth: "100%",
              display: "block",
            }}
          >
            <span role="img" aria-label="package" style={{ verticalAlign: "middle", marginRight: "4px" }}>
              📦
            </span>
            {productTitle}
          </div>

          <div
            style={{
              fontSize: "14px",
              background: "#fefefe",
              border: "1px solid #ccc",
              borderRadius: "8px",
              padding: "1rem",
            }}
          >
            <h3 style={{ marginTop: 0 }}>🔍 Raw & Parsed Values</h3>
            <p>
              <strong>Eco Score (ML):</strong> {attributes.eco_score_ml || "N/A"}
            </p>
            <p>
              <strong>Eco Score (Rule-Based):</strong> {attributes.eco_score_rule_based || "N/A"}
            </p>
            <p>
              <strong>Material Type:</strong>{" "}
              <span title={materialInsight?.description || "No material insight available"}>
                {canonicalMaterial.charAt(0).toUpperCase() + canonicalMaterial.slice(1)}
                {guessedMaterial !== rawMaterial && " (guessed)"}
              </span>
            </p>
            <p>
              <strong>Transport Mode Used in Calculation:</strong>{" "}
              {attributes.transport_mode ?? "N/A"}
            </p>

            <p>
              <strong>Selected Transport Mode:</strong>{" "}
              {attributes.selected_transport_mode
                ? `${attributes.selected_transport_mode} ${
                    attributes.selected_transport_mode === "Air"
                      ? "✈️"
                      : attributes.selected_transport_mode === "Ship"
                      ? "🚢"
                      : attributes.selected_transport_mode === "Truck"
                      ? "🚚"
                      : ""
                  }`
                : "Auto"}
            </p>

            <p>
              <strong>Default Based on Distance:</strong>{" "}
              {attributes.default_transport_mode
                ? `${attributes.default_transport_mode} ${
                    attributes.default_transport_mode === "Air"
                      ? "✈️"
                      : attributes.default_transport_mode === "Ship"
                      ? "🚢"
                      : attributes.default_transport_mode === "Truck"
                      ? "🚚"
                      : ""
                  }`
                : "N/A"}
            </p>


            {attributes.selected_transport_mode &&
              attributes.selected_transport_mode !== attributes.default_transport_mode && (
                <p style={{ color: "orange" }}>
                  ⚠️ You overrode the suggested mode ({attributes.default_transport_mode}) with{" "}
                  {attributes.selected_transport_mode}.
                </p>
            )}

            <p>
              <strong>Weight (incl. packaging):</strong> {attributes.weight_kg ?? "N/A"} kg
            </p>
            <p>
              <strong>Carbon Emissions:</strong> {attributes.carbon_kg ?? "N/A"} kg CO₂
            </p>

            <div className="section-divider"></div>
            <p>
              <strong>Distance from Origin:</strong>{" "}
              {Number.isFinite(parseFloat(attributes?.distance_from_origin_km))
                ? `${parseFloat(attributes.distance_from_origin_km).toFixed(1)} km`
                : "N/A"}
            </p>

            <p>
              <strong>Distance from UK Hub:</strong>{" "}
              {Number.isFinite(parseFloat(attributes?.distance_from_uk_hub_km))
                ? `${parseFloat(attributes.distance_from_uk_hub_km).toFixed(1)} km`
                : "N/A"}
            </p>
          </div>

          <div className="text-center" style={{ marginTop: "10px" }}>
            <button onClick={() => setEquivalenceView((prev) => (prev + 1) % 3)}>
              <span role="img" aria-label="rotate" style={{ verticalAlign: "middle", marginRight: "4px" }}>
                🔁
              </span>
              Show another comparison
            </button>
            <div style={{ marginTop: "8px", fontStyle: "italic" }}>
              {equivalenceView === 0 && result.data?.attributes?.trees_to_offset && (
                <span>≈ {result.data.attributes.trees_to_offset} trees to offset</span>
              )}
              {equivalenceView === 1 && result.data?.attributes?.carbon_kg && (
                <span>≈ {(result.data.attributes.carbon_kg * 4.6).toFixed(1)} km driven</span>
              )}
              {equivalenceView === 2 && result.data?.attributes?.carbon_kg && (
                <span>≈ {Math.round(result.data.attributes.carbon_kg / 0.011)} kettles boiled</span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
