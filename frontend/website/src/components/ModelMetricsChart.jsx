import React, { useEffect, useState } from "react";
const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function ModelMetricsChart() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    fetch(`${BASE_URL}/all-model-metrics`)
      .then((res) => res.json())
      .then((data) => {
        if (
          data.error ||
          !data.random_forest ||
          !data.xgboost ||
          !data.random_forest.labels ||
          !data.random_forest.confusion_matrix
        ) {
          setError(true);
        } else {
          setMetrics(data);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch model metrics:", err);
        setError(true);
      });
  }, []);

  if (error) return <p className="text-red-500 text-sm">❌ Failed to load model metrics.</p>;
  if (!metrics) return <p className="text-sm text-gray-500">Loading model performance...</p>;

  const rf = metrics.random_forest;
  const xgb = metrics.xgboost;

  return (
    <div className="bg-white mt-12 p-6 rounded-lg shadow-md">
      <h3 className="text-2xl font-semibold mb-4">📈 Model Comparison</h3>

      <table className="table-auto w-full text-sm mb-6">
        <thead>
          <tr>
            <th className="text-left">Metric</th>
            <th className="text-left">Random Forest</th>
            <th className="text-left">XGBoost</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Accuracy</td>
            <td>{(rf.accuracy * 100).toFixed(2)}%</td>
            <td>{(xgb.accuracy * 100).toFixed(2)}%</td>
          </tr>
          <tr>
            <td>F1 Score</td>
            <td>{(rf.f1_score * 100).toFixed(2)}%</td>
            <td>{(xgb.f1_score * 100).toFixed(2)}%</td>
          </tr>
        </tbody>
      </table>

      <h4 className="text-lg font-medium mb-2">🧪 Random Forest Confusion Matrix</h4>
      <div className="overflow-x-auto mb-8">
        <table className="table-auto text-sm border">
          <thead>
            <tr>
              <th className="p-2 border bg-gray-100">True ↓ / Pred →</th>
              {rf.labels.map((label, idx) => (
                <th key={idx} className="p-2 border bg-gray-100">{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rf.confusion_matrix.map((row, i) => (
              <tr key={i}>
                <td className="p-2 border bg-gray-50 font-medium">{rf.labels[i]}</td>
                {row.map((val, j) => (
                  <td key={j} className="p-2 border text-center">{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h4 className="text-lg font-medium mb-2">⚡ XGBoost Confusion Matrix</h4>
      <div className="overflow-x-auto">
        <table className="table-auto text-sm border">
          <thead>
            <tr>
              <th className="p-2 border bg-gray-100">True ↓ / Pred →</th>
              {xgb.labels.map((label, idx) => (
                <th key={idx} className="p-2 border bg-gray-100">{label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {xgb.confusion_matrix.map((row, i) => (
              <tr key={i}>
                <td className="p-2 border bg-gray-50 font-medium">{xgb.labels[i]}</td>
                {row.map((val, j) => (
                  <td key={j} className="p-2 border text-center">{val}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
