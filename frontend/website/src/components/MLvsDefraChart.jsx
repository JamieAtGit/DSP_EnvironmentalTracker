import { useEffect, useState, useMemo } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

// Custom Tooltip Component matching design system
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    const value = parseFloat(data.value).toFixed(3);
    const isML = label === "AI Prediction";
    
    return (
      <motion.div 
        className="glass-card p-4 border border-slate-600/50 min-w-48"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.2 }}
      >
        <div className="text-center space-y-2">
          <p className="text-sm font-medium text-slate-200">{label}</p>
          <div className="text-2xl font-bold text-cyan-300">
            {value} kg CO₂
          </div>
          {data.payload.methodology && (
            <p className="text-xs text-slate-400 leading-tight">
              {data.payload.methodology}
            </p>
          )}
          {isML && (
            <div className="text-xs text-green-400 font-medium">
              ⚡ Machine Learning
            </div>
          )}
        </div>
      </motion.div>
    );
  }
  return null;
};

export default function MLvsDEFRAChart({ showML, mlScore, defraCarbonKg, mlCarbonKg }) {
  const [reduction, setReduction] = useState(null);
  const [animationKey, setAnimationKey] = useState(0);

  // Memoized chart data with enhanced validation
  const chartData = useMemo(() => {
    const data = [];
    
    // Validate inputs
    const defraValue = parseFloat(defraCarbonKg) || 0;
    const mlValue = parseFloat(mlCarbonKg) || 0;
    
    if (!showML && defraValue > 0) {
      data.push({ 
        name: "Government Baseline", 
        value: defraValue,
        color: "#64748b", // slate-500 for government
        methodology: "DEFRA standard emission factors",
        confidence: "Standard"
      });
    }
    
    if (mlValue > 0) {
      data.push({ 
        name: "AI Prediction", 
        value: mlValue,
        color: "#06d6a0", // accent-mint from design system
        methodology: "XGBoost ML model with 11 features",
        confidence: "High (85.8% accuracy)"
      });
    }
    
    return data;
  }, [mlCarbonKg, defraCarbonKg, showML]);

  // Enhanced reduction calculation with edge cases
  useEffect(() => {
    if (!showML && defraCarbonKg > 0 && mlCarbonKg > 0) {
      const defra = parseFloat(defraCarbonKg);
      const ml = parseFloat(mlCarbonKg);
      const percent = ((defra - ml) / defra) * 100;
      setReduction(percent.toFixed(1));
    } else {
      setReduction(null);
    }
    setAnimationKey(prev => prev + 1); // Trigger re-animation
  }, [mlCarbonKg, defraCarbonKg, showML]);

  // Error handling for missing data
  if (chartData.length === 0) {
    return (
      <motion.div 
        className="glass-card p-6 mt-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="text-center">
          <div className="text-slate-400 mb-2 text-2xl">⚠️</div>
          <p className="text-slate-400 text-sm">Carbon emission data unavailable</p>
          <p className="text-slate-500 text-xs mt-1">Please check your product analysis</p>
        </div>
      </motion.div>
    );
  }

  // Determine which method performs better
  const getBetterMethod = () => {
    if (chartData.length === 2) {
      const defra = chartData.find(d => d.name === "Government Baseline");
      const ml = chartData.find(d => d.name === "AI Prediction");
      if (defra && ml) {
        return ml.value < defra.value ? "AI" : "Government";
      }
    }
    return null;
  };

  const betterMethod = getBetterMethod();

  return (
    <motion.div 
      className="glass-card p-6 mt-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with enhanced typography */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-3">
          <h3 className="text-xl font-display text-slate-200">
            📊 Carbon Emissions Comparison
          </h3>
          {betterMethod && (
            <div className={`px-3 py-1 rounded-full text-xs font-medium ${
              betterMethod === "AI" 
                ? "bg-green-500/20 text-green-400 border border-green-500/30" 
                : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
            }`}>
              {betterMethod === "AI" ? "⚡ AI Optimized" : "📊 Standard Method"}
            </div>
          )}
        </div>
        <p className="text-sm text-slate-400">
          Methodology comparison: <span className="text-cyan-300 font-medium">
            {showML ? "AI prediction only" : "Machine learning vs government standards"}
          </span>
        </p>
      </div>

      {/* Enhanced Horizontal Bar Chart */}
      <div className="mb-6" style={{ height: showML ? "140px" : "180px" }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            key={animationKey}
            data={chartData}
            layout="vertical"
            margin={{ top: 10, right: 100, left: 10, bottom: 10 }}
            barCategoryGap="25%"
          >
            <XAxis 
              type="number" 
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#94a3b8', fontSize: 12 }}
              tickFormatter={(value) => `${value.toFixed(2)} kg`}
              domain={[0, 'dataMax + 0.5']}
            />
            <YAxis 
              type="category" 
              dataKey="name"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#cbd5e1', fontSize: 14, fontWeight: 500 }}
              width={120}
            />
            <Tooltip content={<CustomTooltip />} />
            
            <Bar 
              dataKey="value" 
              radius={[0, 12, 12, 0]}
              animationDuration={1000}
              animationEasing="ease-out"
            >
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.color}
                  stroke={entry.name === "AI Prediction" ? "#06d6a0" : "#64748b"}
                  strokeWidth={2}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Enhanced insights section */}
      <div className="space-y-4 pt-4 border-t border-slate-600/30">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-slate-400">AI Model Score:</span>
            <span className="text-lg font-bold text-cyan-300">{mlScore || "N/A"}</span>
          </div>
          
          {chartData.length === 2 && (
            <div className="flex justify-between items-center">
              <span className="text-sm text-slate-400">Difference:</span>
              <span className={`text-lg font-bold ${
                parseFloat(reduction) > 0 ? "text-green-400" : "text-red-400"
              }`}>
                {Math.abs(parseFloat(reduction))}% {parseFloat(reduction) > 0 ? "lower" : "higher"}
              </span>
            </div>
          )}
        </div>
        
        {reduction && !showML && (
          <motion.div 
            className={`flex items-center gap-3 p-4 rounded-lg border ${
              parseFloat(reduction) > 0 
                ? "bg-green-500/10 border-green-500/30" 
                : "bg-red-500/10 border-red-500/30"
            }`}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.4 }}
          >
            <span className={parseFloat(reduction) > 0 ? "text-green-400" : "text-red-400"} style={{fontSize: "1.2em"}}>
              {parseFloat(reduction) > 0 ? "🌱" : "⚠️"}
            </span>
            <div>
              <p className="text-sm text-slate-300 font-medium">
                AI model predicts <span className={`font-bold ${
                  parseFloat(reduction) > 0 ? "text-green-400" : "text-red-400"
                }`}>{Math.abs(parseFloat(reduction))}%</span> {
                  parseFloat(reduction) > 0 ? "lower" : "higher"
                } emissions than government baseline
              </p>
              <p className="text-xs text-slate-400 mt-1">
                {parseFloat(reduction) > 0 
                  ? "More accurate prediction suggests better environmental impact"
                  : "Government standards may be underestimating emissions"
                }
              </p>
            </div>
          </motion.div>
        )}

        {/* Methodology note for single model view */}
        {showML && (
          <div className="text-sm text-slate-400 text-center p-3 bg-slate-800/30 rounded-lg">
            💡 Toggle comparison mode to see AI prediction vs government baseline methodology
          </div>
        )}
      </div>
    </motion.div>
  );
}
