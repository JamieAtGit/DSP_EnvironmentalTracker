import React, { useState } from "react";
import { Link } from "react-router-dom";
import PaperPlaneTrail from "../components/PaperPlaneTrail";
import ProductImpactCard from "../components/ProductImpactCard";
import InsightsDashboard from "../components/InsightsDashboard";
import EcoLogTable from "../components/EcoLogTable";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function HomePage() {
  const [url, setUrl] = useState("");
  const [postcode, setPostcode] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [showML, setShowML] = useState(true);

  const handleSearch = async () => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await fetch(`${BASE_URL}/estimate_emissions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          amazon_url: url,
          postcode: postcode || "SW1A 1AA",
          include_packaging: true,
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Unknown error");

      setResult(data.data);
    } catch (err) {
      setError(err.message || "Failed to contact backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-white">
      <PaperPlaneTrail />

      <div className="relative z-10 flex flex-col items-center justify-start p-6 font-sans text-gray-900">
        {/* Header */}
        <header className="w-full max-w-6xl py-6 flex justify-between items-center border-b">
          <h1 className="text-2xl font-bold text-green-700">🌿 Impact Tracker</h1>
          <nav className="space-x-6 text-gray-600 text-sm">
            <Link to="/">Home</Link>
            <Link to="/learn">Learn</Link>
            <Link to="/predict">Predict</Link>
            <Link to="/login">Login</Link>
            <Link to="/extension">Extension</Link>
          </nav>
        </header>

        {/* Hero */}
        <section className="text-center mt-20 mb-10">
          <h2 className="text-3xl font-semibold mb-4">
            Ready to learn about your products?
          </h2>
          <p className="text-gray-500 max-w-lg mx-auto">
            Enter an Amazon product URL and postcode to reveal its environmental footprint.
          </p>
        </section>

        {/* Input */}
        <div className="flex flex-col sm:flex-row gap-3 w-full max-w-2xl mb-10">
          <input
            type="text"
            placeholder="Amazon product URL"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="border border-gray-300 rounded px-4 py-2 flex-1 shadow-sm"
          />
          <input
            type="text"
            placeholder="Postcode (optional)"
            value={postcode}
            onChange={(e) => setPostcode(e.target.value)}
            className="border border-gray-300 rounded px-4 py-2 w-full sm:w-48 shadow-sm"
          />
          <button
            onClick={handleSearch}
            disabled={loading || !url}
            className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 transition disabled:opacity-50"
          >
            {loading ? "Loading..." : "Search"}
          </button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 mb-4">{error}</p>}

        {/* Result Card */}
        {result && (
          <ProductImpactCard
            result={result}
            showML={showML}
            toggleShowML={() => setShowML(!showML)}
          />
        )}

        {/* Dashboard + Logs */}
        <InsightsDashboard />
        <h3 className="text-xl font-bold mt-10 mb-4">
          📋 Explore Logged Product Estimates
        </h3>
        <EcoLogTable />

        {/* Footer */}
        <footer className="w-full border-t py-4 text-sm text-center text-gray-400 mt-auto">
          © 2025 EcoTrack. Built with 💚 for a greener future.
        </footer>
      </div>
    </div>
  );
}
