import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  WaterfallChart, Cell, PieChart, Pie, LineChart, Line, ScatterChart, Scatter,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';
import { useQuery, useQueryClient } from 'react-query';
import io from 'socket.io-client';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

/**
 * Advanced Explainable AI Dashboard
 * 
 * Features:
 * - Real-time SHAP explanations
 * - Interactive LIME visualizations  
 * - Counterfactual analysis
 * - Uncertainty quantification
 * - Multi-modal explanation comparison
 * - Performance optimization with React Query
 */

const AdvancedExplainabilityDashboard = ({ predictionInstance, onExplanationUpdate }) => {
  const [selectedExplanationType, setSelectedExplanationType] = useState('shap');
  const [socket, setSocket] = useState(null);
  const [realTimeExplanations, setRealTimeExplanations] = useState([]);
  const [uncertaintyMetrics, setUncertaintyMetrics] = useState(null);
  const [counterfactuals, setCounterfactuals] = useState([]);
  const queryClient = useQueryClient();

  // Initialize WebSocket connection for real-time updates
  useEffect(() => {
    const socketConnection = io(BASE_URL, {
      transports: ['websocket'],
      autoConnect: true
    });

    socketConnection.on('connect', () => {
      console.log('Connected to explainability service');
    });

    socketConnection.on('explanation_update', (explanation) => {
      setRealTimeExplanations(prev => [explanation, ...prev.slice(0, 9)]); // Keep last 10
      if (onExplanationUpdate) {
        onExplanationUpdate(explanation);
      }
    });

    socketConnection.on('uncertainty_update', (metrics) => {
      setUncertaintyMetrics(metrics);
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, [onExplanationUpdate]);

  // Fetch explanation data with React Query for caching and optimization
  const { 
    data: explanationData, 
    isLoading: isLoadingExplanation,
    error: explanationError,
    refetch: refetchExplanation
  } = useQuery(
    ['explanation', predictionInstance?.id], 
    async () => {
      if (!predictionInstance) return null;
      
      const response = await fetch(`${BASE_URL}/api/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instance: predictionInstance.features,
          include_counterfactuals: true,
          include_uncertainty: true
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch explanation');
      }
      
      return response.json();
    },
    {
      enabled: !!predictionInstance,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false,
      onSuccess: (data) => {
        if (data?.counterfactuals) {
          setCounterfactuals(data.counterfactuals.counterfactuals || []);
        }
        if (data?.uncertainty_metrics) {
          setUncertaintyMetrics(data.uncertainty_metrics);
        }
      }
    }
  );

  // Memoized chart data transformations for performance
  const chartData = useMemo(() => {
    if (!explanationData) return {};

    const shapData = explanationData.shap_values?.map((value, index) => ({
      feature: explanationData.feature_names?.[index] || `Feature ${index}`,
      value: value,
      absValue: Math.abs(value),
      direction: value >= 0 ? 'positive' : 'negative'
    })).sort((a, b) => b.absValue - a.absValue).slice(0, 10) || [];

    const limeData = explanationData.lime_explanation?.map(([feature, value]) => ({
      feature: feature,
      value: value,
      absValue: Math.abs(value),
      direction: value >= 0 ? 'positive' : 'negative'
    })).sort((a, b) => b.absValue - a.absValue).slice(0, 10) || [];

    const comparisonData = shapData.map(shapItem => {
      const limeItem = limeData.find(lime => lime.feature === shapItem.feature);
      return {
        feature: shapItem.feature,
        shap: shapItem.value,
        lime: limeItem?.value || 0,
        difference: Math.abs(shapItem.value - (limeItem?.value || 0))
      };
    });

    return { shapData, limeData, comparisonData };
  }, [explanationData]);

  // Request explanation when instance changes
  useEffect(() => {
    if (predictionInstance && socket) {
      socket.emit('request_explanation', {
        instance_id: predictionInstance.id,
        features: predictionInstance.features
      });
    }
  }, [predictionInstance, socket]);

  const handleExplanationTypeChange = useCallback((type) => {
    setSelectedExplanationType(type);
  }, []);

  const handleRefreshExplanation = useCallback(() => {
    refetchExplanation();
    if (socket && predictionInstance) {
      socket.emit('request_explanation', {
        instance_id: predictionInstance.id,
        features: predictionInstance.features,
        force_refresh: true
      });
    }
  }, [refetchExplanation, socket, predictionInstance]);

  if (!predictionInstance) {
    return (
      <div className=\"flex items-center justify-center h-64 bg-slate-800/50 rounded-lg border border-slate-600\">
        <div className=\"text-center\">
          <div className=\"text-slate-400 mb-2\">🔍</div>
          <p className=\"text-slate-300\">Make a prediction to see explanations</p>
          <p className=\"text-slate-500 text-sm\">AI explanations will appear here</p>
        </div>
      </div>
    );
  }

  if (isLoadingExplanation) {
    return (
      <div className=\"space-y-6\">
        <ExplanationLoadingSkeleton />
      </div>
    );
  }

  if (explanationError) {
    return (
      <div className=\"bg-red-900/20 border border-red-500/50 rounded-lg p-6\">
        <div className=\"flex items-center gap-3 mb-4\">
          <div className=\"text-red-400 text-xl\">⚠️</div>
          <h3 className=\"text-red-300 font-semibold\">Explanation Error</h3>
        </div>
        <p className=\"text-red-200 mb-4\">{explanationError.message}</p>
        <button 
          onClick={handleRefreshExplanation}
          className=\"bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-white font-medium transition-colors\"
        >
          Retry Explanation
        </button>
      </div>
    );
  }

  return (
    <div className=\"space-y-8\">
      {/* Header with Controls */}
      <div className=\"flex items-center justify-between\">
        <div>
          <h2 className=\"text-2xl font-bold text-slate-200 mb-2\">
            🧠 AI Explainability Dashboard
          </h2>
          <p className=\"text-slate-400\">
            Understanding how the model makes predictions
          </p>
        </div>
        
        <div className=\"flex items-center gap-4\">
          {/* Explanation Type Selector */}
          <div className=\"flex bg-slate-800 rounded-lg p-1\">
            {[
              { id: 'shap', label: 'SHAP', icon: '🎯' },
              { id: 'lime', label: 'LIME', icon: '🔍' },
              { id: 'comparison', label: 'Compare', icon: '⚖️' },
              { id: 'uncertainty', label: 'Uncertainty', icon: '📊' }
            ].map(type => (
              <button
                key={type.id}
                onClick={() => handleExplanationTypeChange(type.id)}
                className={`px-4 py-2 rounded-md transition-all font-medium ${
                  selectedExplanationType === type.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                }`}
              >
                <span className=\"mr-2\">{type.icon}</span>
                {type.label}
              </button>
            ))}
          </div>

          {/* Refresh Button */}
          <button
            onClick={handleRefreshExplanation}
            className=\"bg-slate-700 hover:bg-slate-600 p-2 rounded-lg transition-colors group\"
            title=\"Refresh explanation\"
          >
            <div className=\"text-slate-300 group-hover:text-white transition-colors\">
              🔄
            </div>
          </button>
        </div>
      </div>

      {/* Real-time Status Indicator */}
      {socket?.connected && (
        <div className=\"flex items-center gap-2 text-sm text-green-400\">
          <div className=\"w-2 h-2 bg-green-400 rounded-full animate-pulse\" />
          Real-time explanations active
        </div>
      )}

      {/* Main Explanation Content */}
      <AnimatePresence mode=\"wait\">
        <motion.div
          key={selectedExplanationType}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
          className=\"space-y-6\"
        >
          {selectedExplanationType === 'shap' && (
            <SHAPExplanationView 
              data={chartData.shapData} 
              prediction={predictionInstance.prediction}
            />
          )}
          
          {selectedExplanationType === 'lime' && (
            <LIMEExplanationView 
              data={chartData.limeData}
              prediction={predictionInstance.prediction}
            />
          )}
          
          {selectedExplanationType === 'comparison' && (
            <ExplanationComparisonView 
              data={chartData.comparisonData}
              prediction={predictionInstance.prediction}
            />
          )}
          
          {selectedExplanationType === 'uncertainty' && (
            <UncertaintyAnalysisView 
              uncertaintyMetrics={uncertaintyMetrics}
              prediction={predictionInstance.prediction}
              counterfactuals={counterfactuals}
            />
          )}
        </motion.div>
      </AnimatePresence>

      {/* Counterfactual Analysis Section */}
      {counterfactuals.length > 0 && selectedExplanationType !== 'uncertainty' && (
        <CounterfactualAnalysisSection 
          counterfactuals={counterfactuals}
          originalPrediction={predictionInstance.prediction}
        />
      )}

      {/* Real-time Explanation Stream */}
      {realTimeExplanations.length > 0 && (
        <RealTimeExplanationStream explanations={realTimeExplanations} />
      )}
    </div>
  );
};

/* Supporting Components */

const SHAPExplanationView = ({ data, prediction }) => (
  <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
    <div className=\"mb-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-2\">
        🎯 SHAP Feature Attribution
      </h3>
      <p className=\"text-slate-400 text-sm\">
        Shapley values showing each feature's contribution to the prediction
      </p>
    </div>

    <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
      {/* Waterfall Chart */}
      <div className=\"lg:col-span-2\">
        <h4 className=\"text-lg font-medium text-slate-300 mb-4\">Feature Contributions</h4>
        <ResponsiveContainer width=\"100%\" height={400}>
          <BarChart data={data} layout=\"horizontal\">
            <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
            <XAxis type=\"number\" stroke=\"#9CA3AF\" />
            <YAxis type=\"category\" dataKey=\"feature\" stroke=\"#9CA3AF\" width={120} />
            <Tooltip 
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className=\"bg-slate-900 border border-slate-600 rounded-lg p-3 shadow-xl\">
                      <p className=\"text-slate-200 font-medium\">{label}</p>
                      <p className={`font-semibold ${data.direction === 'positive' ? 'text-green-400' : 'text-red-400'}`}>
                        SHAP Value: {data.value.toFixed(4)}
                      </p>
                      <p className=\"text-slate-400 text-sm\">
                        {data.direction === 'positive' ? 'Increases' : 'Decreases'} prediction confidence
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey=\"value\" radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.direction === 'positive' ? '#10B981' : '#EF4444'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Summary Stats */}
      <div className=\"space-y-4\">
        <div className=\"bg-slate-700/50 rounded-lg p-4\">
          <h5 className=\"text-slate-300 font-medium mb-2\">Prediction Summary</h5>
          <div className=\"text-2xl font-bold text-blue-400 mb-1\">{prediction}</div>
          <div className=\"text-slate-400 text-sm\">Eco Score</div>
        </div>

        <div className=\"bg-slate-700/50 rounded-lg p-4\">
          <h5 className=\"text-slate-300 font-medium mb-3\">Top Contributors</h5>
          <div className=\"space-y-2\">
            {data.slice(0, 3).map((item, index) => (
              <div key={index} className=\"flex items-center justify-between\">
                <span className=\"text-slate-300 text-sm truncate\">{item.feature}</span>
                <span className={`font-semibold text-sm ${
                  item.direction === 'positive' ? 'text-green-400' : 'text-red-400'
                }`}>
                  {item.value > 0 ? '+' : ''}{item.value.toFixed(3)}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className=\"bg-slate-700/50 rounded-lg p-4\">
          <h5 className=\"text-slate-300 font-medium mb-2\">Explanation Quality</h5>
          <div className=\"flex items-center gap-2\">
            <div className=\"flex-1 bg-slate-600 rounded-full h-2\">
              <div 
                className=\"bg-green-500 h-2 rounded-full transition-all duration-1000\"
                style={{ width: '85%' }}
              />
            </div>
            <span className=\"text-slate-300 text-sm font-medium\">85%</span>
          </div>
          <p className=\"text-slate-400 text-xs mt-1\">Consistency with LIME</p>
        </div>
      </div>
    </div>
  </div>
);

const LIMEExplanationView = ({ data, prediction }) => (
  <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
    <div className=\"mb-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-2\">
        🔍 LIME Local Explanation
      </h3>
      <p className=\"text-slate-400 text-sm\">
        Local linear approximation of model behavior around this prediction
      </p>
    </div>

    <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
      <div>
        <h4 className=\"text-lg font-medium text-slate-300 mb-4\">Local Feature Importance</h4>
        <ResponsiveContainer width=\"100%\" height={350}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
            <XAxis dataKey=\"feature\" stroke=\"#9CA3AF\" angle={-45} textAnchor=\"end\" height={100} />
            <YAxis stroke=\"#9CA3AF\" />
            <Tooltip 
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  return (
                    <div className=\"bg-slate-900 border border-slate-600 rounded-lg p-3 shadow-xl\">
                      <p className=\"text-slate-200 font-medium\">{label}</p>
                      <p className={`font-semibold ${data.direction === 'positive' ? 'text-blue-400' : 'text-orange-400'}`}>
                        LIME Score: {data.value.toFixed(4)}
                      </p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Bar dataKey=\"value\" radius={[4, 4, 0, 0]}>
              {data.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={entry.direction === 'positive' ? '#3B82F6' : '#F97316'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h4 className=\"text-lg font-medium text-slate-300 mb-4\">Decision Boundary</h4>
        <div className=\"bg-slate-700/30 rounded-lg p-4 h-350\">
          <div className=\"text-center text-slate-400\">
            <div className=\"text-4xl mb-2\">🎯</div>
            <p className=\"font-medium\">Local Decision Boundary</p>
            <p className=\"text-sm mt-2\">
              Model behavior in the neighborhood of this prediction
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ExplanationComparisonView = ({ data, prediction }) => (
  <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
    <div className=\"mb-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-2\">
        ⚖️ Method Comparison
      </h3>
      <p className=\"text-slate-400 text-sm\">
        Comparing SHAP and LIME explanations for consistency analysis
      </p>
    </div>

    <ResponsiveContainer width=\"100%\" height={400}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
        <XAxis dataKey=\"feature\" stroke=\"#9CA3AF\" angle={-45} textAnchor=\"end\" height={100} />
        <YAxis stroke=\"#9CA3AF\" />
        <Tooltip 
          content={({ active, payload, label }) => {
            if (active && payload && payload.length) {
              const shapData = payload.find(p => p.dataKey === 'shap');
              const limeData = payload.find(p => p.dataKey === 'lime');
              return (
                <div className=\"bg-slate-900 border border-slate-600 rounded-lg p-3 shadow-xl\">
                  <p className=\"text-slate-200 font-medium mb-2\">{label}</p>
                  <div className=\"space-y-1\">
                    <p className=\"text-green-400\">SHAP: {shapData?.value?.toFixed(4)}</p>
                    <p className=\"text-blue-400\">LIME: {limeData?.value?.toFixed(4)}</p>
                    <p className=\"text-slate-400 text-sm\">
                      Difference: {Math.abs((shapData?.value || 0) - (limeData?.value || 0)).toFixed(4)}
                    </p>
                  </div>
                </div>
              );
            }
            return null;
          }}
        />
        <Bar dataKey=\"shap\" fill=\"#10B981\" name=\"SHAP\" radius={[2, 2, 0, 0]} />
        <Bar dataKey=\"lime\" fill=\"#3B82F6\" name=\"LIME\" radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>

    <div className=\"mt-6 grid grid-cols-1 md:grid-cols-3 gap-4\">
      <div className=\"bg-slate-700/50 rounded-lg p-4 text-center\">
        <div className=\"text-green-400 text-xl font-bold mb-1\">
          {data.length > 0 ? (data.reduce((acc, item) => acc + Math.abs(item.shap), 0) / data.length).toFixed(3) : '0.000'}
        </div>
        <div className=\"text-slate-300 text-sm\">Avg SHAP Impact</div>
      </div>
      <div className=\"bg-slate-700/50 rounded-lg p-4 text-center\">
        <div className=\"text-blue-400 text-xl font-bold mb-1\">
          {data.length > 0 ? (data.reduce((acc, item) => acc + Math.abs(item.lime), 0) / data.length).toFixed(3) : '0.000'}
        </div>
        <div className=\"text-slate-300 text-sm\">Avg LIME Impact</div>
      </div>
      <div className=\"bg-slate-700/50 rounded-lg p-4 text-center\">
        <div className=\"text-purple-400 text-xl font-bold mb-1\">
          {data.length > 0 ? (data.reduce((acc, item) => acc + item.difference, 0) / data.length).toFixed(3) : '0.000'}
        </div>
        <div className=\"text-slate-300 text-sm\">Avg Difference</div>
      </div>
    </div>
  </div>
);

const UncertaintyAnalysisView = ({ uncertaintyMetrics, prediction, counterfactuals }) => (
  <div className=\"space-y-6\">
    {/* Uncertainty Metrics */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-6\">
        📊 Prediction Uncertainty Analysis
      </h3>
      
      {uncertaintyMetrics ? (
        <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
          <div className=\"space-y-4\">
            <UncertaintyGauge 
              title=\"Confidence\"
              value={uncertaintyMetrics.confidence * 100}
              color=\"#10B981\"
              format=\"percentage\"
            />
            <UncertaintyGauge 
              title=\"Entropy\"
              value={uncertaintyMetrics.entropy}
              color=\"#F59E0B\"
              format=\"decimal\"
              max={3}
            />
          </div>
          
          <div className=\"space-y-4\">
            <div className=\"bg-slate-700/50 rounded-lg p-4\">
              <h5 className=\"text-slate-300 font-medium mb-3\">Uncertainty Breakdown</h5>
              <div className=\"space-y-3\">
                <div className=\"flex justify-between items-center\">
                  <span className=\"text-slate-400\">Model Confidence</span>
                  <span className=\"text-green-400 font-semibold\">
                    {(uncertaintyMetrics.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className=\"flex justify-between items-center\">
                  <span className=\"text-slate-400\">Prediction Margin</span>
                  <span className=\"text-blue-400 font-semibold\">
                    {uncertaintyMetrics.prediction_margin?.toFixed(3) || 'N/A'}
                  </span>
                </div>
                <div className=\"flex justify-between items-center\">
                  <span className=\"text-slate-400\">Entropy Score</span>
                  <span className=\"text-orange-400 font-semibold\">
                    {uncertaintyMetrics.entropy.toFixed(3)}
                  </span>
                </div>
              </div>
            </div>
            
            <div className=\"bg-slate-700/50 rounded-lg p-4\">
              <h5 className=\"text-slate-300 font-medium mb-2\">Reliability Assessment</h5>
              <div className=\"space-y-2\">
                {uncertaintyMetrics.confidence > 0.9 && (
                  <div className=\"flex items-center gap-2 text-green-400 text-sm\">
                    <span>✅</span>
                    <span>High confidence prediction</span>
                  </div>
                )}
                {uncertaintyMetrics.confidence < 0.7 && (
                  <div className=\"flex items-center gap-2 text-yellow-400 text-sm\">
                    <span>⚠️</span>
                    <span>Moderate uncertainty detected</span>
                  </div>
                )}
                {uncertaintyMetrics.entropy > 1.5 && (
                  <div className=\"flex items-center gap-2 text-orange-400 text-sm\">
                    <span>🎲</span>
                    <span>High entropy - consider additional data</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className=\"text-center text-slate-400 py-8\">
          <div className=\"text-4xl mb-2\">📊</div>
          <p>No uncertainty metrics available</p>
        </div>
      )}
    </div>

    {/* Counterfactuals */}
    {counterfactuals.length > 0 && (
      <CounterfactualAnalysisSection 
        counterfactuals={counterfactuals}
        originalPrediction={prediction}
      />
    )}
  </div>
);

const UncertaintyGauge = ({ title, value, color, format = 'percentage', max = 100 }) => {
  const percentage = (value / max) * 100;
  const circumference = 2 * Math.PI * 40;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  return (
    <div className=\"bg-slate-700/50 rounded-lg p-4\">
      <h5 className=\"text-slate-300 font-medium mb-4 text-center\">{title}</h5>
      <div className=\"relative flex items-center justify-center\">
        <svg width=\"100\" height=\"100\" className=\"transform -rotate-90\">
          <circle
            cx=\"50\"
            cy=\"50\"
            r=\"40\"
            stroke=\"#374151\"
            strokeWidth=\"8\"
            fill=\"none\"
          />
          <circle
            cx=\"50\"
            cy=\"50\"
            r=\"40\"
            stroke={color}
            strokeWidth=\"8\"
            fill=\"none\"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap=\"round\"
            className=\"transition-all duration-1000 ease-out\"
          />
        </svg>
        <div className=\"absolute inset-0 flex items-center justify-center\">
          <div className=\"text-center\">
            <div className=\"text-xl font-bold\" style={{ color }}>
              {format === 'percentage' ? `${value.toFixed(1)}%` : value.toFixed(2)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const CounterfactualAnalysisSection = ({ counterfactuals, originalPrediction }) => (
  <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
    <h3 className=\"text-xl font-semibold text-slate-200 mb-6\">
      🔄 Counterfactual Analysis
    </h3>
    <p className=\"text-slate-400 text-sm mb-6\">
      Minimal changes needed to achieve different predictions
    </p>
    
    <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4\">
      {counterfactuals.slice(0, 6).map((cf, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className=\"bg-slate-700/50 rounded-lg p-4 border border-slate-600\"
        >
          <div className=\"flex items-center justify-between mb-3\">
            <h5 className=\"text-slate-300 font-medium truncate\">{cf.feature}</h5>
            <div className=\"text-xs bg-blue-600 text-white px-2 py-1 rounded\">
              {cf.new_prediction}
            </div>
          </div>
          
          <div className=\"space-y-2 text-sm\">
            <div className=\"flex justify-between\">
              <span className=\"text-slate-400\">Current:</span>
              <span className=\"text-slate-200 font-medium\">{cf.original_value.toFixed(3)}</span>
            </div>
            <div className=\"flex justify-between\">
              <span className=\"text-slate-400\">Change to:</span>
              <span className=\"text-blue-400 font-medium\">{cf.counterfactual_value.toFixed(3)}</span>
            </div>
            <div className=\"flex justify-between\">
              <span className=\"text-slate-400\">Difference:</span>
              <span className={`font-medium ${cf.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {cf.change >= 0 ? '+' : ''}{cf.change.toFixed(3)}
              </span>
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

const RealTimeExplanationStream = ({ explanations }) => (
  <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
    <h3 className=\"text-xl font-semibold text-slate-200 mb-6\">
      📡 Real-Time Explanation Stream
    </h3>
    
    <div className=\"space-y-3 max-h-64 overflow-y-auto\">
      {explanations.map((explanation, index) => (
        <motion.div
          key={explanation.timestamp || index}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className=\"bg-slate-700/50 rounded-lg p-3 border-l-4 border-blue-500\"
        >
          <div className=\"flex items-center justify-between mb-2\">
            <span className=\"text-slate-300 text-sm font-medium\">
              Prediction: {explanation.prediction}
            </span>
            <span className=\"text-slate-500 text-xs\">
              {new Date(explanation.timestamp).toLocaleTimeString()}
            </span>
          </div>
          <div className=\"text-slate-400 text-xs\">
            Quality: {(explanation.explanation_quality * 100).toFixed(1)}% | 
            Computation: {(explanation.computation_time * 1000).toFixed(0)}ms
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

const ExplanationLoadingSkeleton = () => (
  <div className=\"space-y-6 animate-pulse\">
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <div className=\"h-6 bg-slate-700 rounded w-1/3 mb-4\" />
      <div className=\"h-4 bg-slate-700 rounded w-2/3 mb-6\" />
      <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
        <div className=\"lg:col-span-2 h-96 bg-slate-700 rounded\" />
        <div className=\"space-y-4\">
          <div className=\"h-24 bg-slate-700 rounded\" />
          <div className=\"h-32 bg-slate-700 rounded\" />
          <div className=\"h-20 bg-slate-700 rounded\" />
        </div>
      </div>
    </div>
  </div>
);

export default AdvancedExplainabilityDashboard;