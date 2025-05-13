// src/components/ProductImpactCard.jsx
import React from "react";
import MLvsDEFRAChart from "./MLvsDefraChart";
import CarbonMetricsCircle from "./CarbonMetricsCircle";

export default function ProductImpactCard({ result, showML, toggleShowML }) {
  const attr = result.attributes || {};
  const originKm = parseFloat(attr.distance_from_origin_km || 0);
  const ukKm = parseFloat(attr.distance_from_uk_hub_km || 0);
  const ecoScore = attr.eco_score_ml;
  const confidence = attr.eco_score_confidence;
  const emoji = {
    "A+": "🌍", A: "🌿", B: "🍃", C: "🌱", D: "⚠️", E: "❌", F: "💀"
  }[ecoScore] || "";

  return (
    <div className="bg-white rounded-2xl shadow-md p-6 space-y-4 border border-gray-200">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-green-800">🌍 Product Impact Summary</h3>
        <button
          onClick={toggleShowML}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-md"
        >
          {showML ? "Switch to DEFRA" : "Switch to ML"}
        </button>
      </div>

      <ul className="text-sm text-gray-700 space-y-1">
        <li><strong>Product:</strong> {result.title}</li>
        <li><strong>Weight:</strong> {attr.raw_product_weight_kg} kg</li>
        <li><strong>+ Packaging:</strong> {attr.weight_kg} kg</li>
        <li><strong>Origin:</strong> {attr.origin}</li>
        <li>
          <strong>Eco Score:</strong> {ecoScore} <span className="ml-1">{emoji}</span>
          <span className="text-yellow-500 ml-2">
            {typeof confidence === "number"
              ? `${confidence.toFixed(1)}% confident`
              : "N/A confident"}
          </span>
        </li>
        <li><strong>Material Type:</strong> {attr.material_type}</li>
        <li><strong>Transport Mode:</strong> {attr.transport_mode}</li>
        <li><strong>Recyclability:</strong> {attr.recyclability}</li>
        <li><strong>Carbon Emissions:</strong> {attr.carbon_kg} kg CO₂</li>
        <li>
          <strong>🌳 Offset Equivalent:</strong>{" "}
          {attr.trees_to_offset} tree{attr.trees_to_offset > 1 ? "s" : ""}
        </li>
        <li><strong>Intl Distance:</strong> {originKm.toFixed(1)} km</li>
        <li><strong>UK Distance:</strong> {ukKm.toFixed(1)} km</li>
      </ul>

      <CarbonMetricsCircle
        carbonKg={attr.carbon_kg}
        ecoScore={attr.eco_score_ml}
        recyclability={attr.recyclability}
        treesToOffset={attr.trees_to_offset}
      />


      <MLvsDEFRAChart
        showML={showML}
        mlScore={attr.eco_score_ml}
        defraCarbonKg={attr.carbon_kg}
        mlCarbonKg={attr.ml_carbon_kg}
      />
    </div>
  );
}
