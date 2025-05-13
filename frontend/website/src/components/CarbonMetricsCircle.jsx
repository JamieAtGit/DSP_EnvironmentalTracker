import React from "react";
import {
  CircularProgressbar,
  buildStyles,
} from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

function normalizeEcoScore(score) {
  const scale = ["F", "E", "D", "C", "B", "A", "A+"];
  const index = scale.indexOf(score?.toUpperCase());
  return index >= 0 ? ((index + 1) / scale.length) * 100 : 0;
}

export default function CarbonMetricsCircle({
  carbonKg,
  ecoScore,
  recyclability,
  treesToOffset,
}) {
  const carbonPct = Math.min((carbonKg / 25) * 100, 100); // Normalize to 25kg cap
  const treePct = Math.min((treesToOffset / 10) * 100, 100); // Normalize to 10 trees
  const recyclePct =
    typeof recyclability === "number"
      ? recyclability
      : recyclability === "High"
      ? 90
      : recyclability === "Medium"
      ? 60
      : 30;
  const ecoPct = normalizeEcoScore(ecoScore);

  const metrics = [
    { label: "CO₂", value: carbonPct, text: `${carbonKg?.toFixed(1) ?? "N/A"} kg` },
    { label: "Recyclability", value: recyclePct, text: `${recyclePct.toFixed(0)}%` },
    { label: "Eco Score", value: ecoPct, text: ecoScore ?? "N/A" },
    { label: "Offset Trees", value: treePct, text: `${treesToOffset ?? 0} trees` },
  ];

  return (
    <div className="mt-6">
      {/* Title and Info Tooltip */}
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-gray-800">
          🧮 Environmental Breakdown
        </h4>
        <div className="relative group cursor-pointer">
          <span className="text-sm text-gray-500 hover:text-gray-700">ℹ️</span>
          <div className="absolute right-0 top-6 w-64 text-xs text-gray-600 bg-white border border-gray-200 rounded shadow-md p-3 hidden group-hover:block z-10">
            Each circle shows a normalized percentage:
            <ul className="list-disc pl-4 mt-1 space-y-1">
              <li><strong>CO₂:</strong> % of 25kg emissions cap</li>
              <li><strong>Recyclability:</strong> High = 90%, Medium = 60%</li>
              <li><strong>Eco Score:</strong> Scaled from F (0%) to A+ (100%)</li>
              <li><strong>Trees:</strong> Based on a 10-tree offset cap</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Chart Grid */}
      <div className="grid grid-cols-2 gap-6">
        {metrics.map((m, i) => (
          <div key={i} className="flex flex-col items-center">
            <div className="w-24 h-24">
              <CircularProgressbar
                value={m.value}
                text={m.text}
                styles={buildStyles({
                  textSize: "10px",
                  pathColor: "#15803d",
                  textColor: "#1f2937",
                  trailColor: "#e5e7eb",
                })}
              />
            </div>
            <p className="mt-2 text-sm font-medium text-gray-700">{m.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
