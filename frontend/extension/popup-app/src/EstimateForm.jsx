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
          <h3>📦 {productTitle}</h3>
          <p><strong>Eco Score (ML):</strong> {attributes.eco_score_ml}</p>
          <p><strong>Rule-based Score:</strong> {attributes.eco_score_rule_based}</p>
          <p><strong>Material:</strong> {canonicalMaterial}</p>
          <p><strong>Weight:</strong> {attributes.weight_kg} kg</p>
          <p><strong>Transport Mode:</strong> {attributes.transport_mode}</p>
          <p><strong>CO₂ Emissions:</strong> {attributes.carbon_kg} kg</p>
          <p><strong>Distance from Origin:</strong> {attributes.distance_from_origin_km} km</p>
          <p><strong>Distance from UK Hub:</strong> {attributes.distance_from_uk_hub_km} km</p>
        </div>
      )}
    </div>
  );
}
