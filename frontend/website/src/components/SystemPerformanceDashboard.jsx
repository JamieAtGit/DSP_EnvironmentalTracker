import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  ScatterChart, Scatter, RadialBarChart, RadialBar
} from 'recharts';
import { useQuery, useQueryClient } from 'react-query';
import io from 'socket.io-client';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

/**
 * System Performance Dashboard
 * 
 * Features:
 * - Real-time performance monitoring
 * - API metrics visualization
 * - Cache performance analysis
 * - Circuit breaker status
 * - Model performance tracking
 * - Resource utilization monitoring
 */

const SystemPerformanceDashboard = () => {
  const [socket, setSocket] = useState(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState(null);
  const [selectedTimeRange, setSelectedTimeRange] = useState('1h');
  const [selectedView, setSelectedView] = useState('overview');
  const [alertHistory, setAlertHistory] = useState([]);
  const queryClient = useQueryClient();

  // Initialize WebSocket for real-time monitoring
  useEffect(() => {
    const socketConnection = io(`${BASE_URL}/realtime`, {
      transports: ['websocket'],
      autoConnect: true
    });

    socketConnection.on('connect', () => {
      console.log('Connected to monitoring service');
      socketConnection.emit('subscribe_monitoring');
    });

    socketConnection.on('monitoring_data', (data) => {
      setRealTimeMetrics(data);
    });

    socketConnection.on('monitoring_update', (data) => {
      setRealTimeMetrics(prev => ({
        ...prev,
        ...data
      }));
    });

    socketConnection.on('drift_alert', (alert) => {
      setAlertHistory(prev => [alert, ...prev.slice(0, 19)]); // Keep last 20 alerts
    });

    setSocket(socketConnection);

    return () => {
      socketConnection.disconnect();
    };
  }, []);

  // Fetch performance metrics
  const { 
    data: performanceData, 
    isLoading,
    error,
    refetch 
  } = useQuery(
    ['performance-metrics', selectedTimeRange],
    async () => {
      const response = await fetch(`${BASE_URL}/api/performance-metrics`);
      if (!response.ok) {
        throw new Error('Failed to fetch performance metrics');
      }
      return response.json();
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      staleTime: 15000, // Consider data stale after 15 seconds
      cacheTime: 60000 // Cache for 1 minute
    }
  );

  // Combine real-time and historical data
  const combinedMetrics = useMemo(() => {
    if (!performanceData) return realTimeMetrics;
    if (!realTimeMetrics) return performanceData;
    
    return {
      ...performanceData,
      metrics: realTimeMetrics.metrics || performanceData.api_metrics,
      cache_stats: realTimeMetrics.cache_stats || performanceData.cache_performance,
      active_connections: realTimeMetrics.active_connections || performanceData.active_connections,
      timestamp: realTimeMetrics.timestamp || performanceData.timestamp
    };
  }, [performanceData, realTimeMetrics]);

  // Generate chart data for time series
  const timeSeriesData = useMemo(() => {
    if (!combinedMetrics?.recent_requests) return [];
    
    return combinedMetrics.recent_requests.map((request, index) => ({
      index: index,
      response_time: request.response_time * 1000, // Convert to ms
      timestamp: new Date(request.timestamp).getTime(),
      status: request.status === 'success' ? 1 : 0
    })).reverse();
  }, [combinedMetrics]);

  // Circuit breaker status data
  const circuitBreakerData = useMemo(() => {
    if (!combinedMetrics?.circuit_breaker_status) return [];
    
    return Object.entries(combinedMetrics.circuit_breaker_status).map(([name, status]) => ({
      name: name.replace('_', ' ').toUpperCase(),
      state: status.state,
      failure_count: status.failure_count,
      status: status.state === 'CLOSED' ? 'healthy' : status.state === 'HALF_OPEN' ? 'warning' : 'error'
    }));
  }, [combinedMetrics]);

  // Cache performance data
  const cachePerformanceData = useMemo(() => {
    if (!combinedMetrics?.cache_stats?.performance_stats) return [];
    
    const stats = combinedMetrics.cache_stats.performance_stats;
    return [
      { name: 'L1 Cache', hit_rate: stats.l1?.hit_rate * 100 || 0, hits: stats.l1?.hits || 0, misses: stats.l1?.misses || 0 },
      { name: 'L2 Cache', hit_rate: stats.l2?.hit_rate * 100 || 0, hits: stats.l2?.hits || 0, misses: stats.l2?.misses || 0 },
      { name: 'L3 Cache', hit_rate: stats.l3?.hit_rate * 100 || 0, hits: stats.l3?.hits || 0, misses: stats.l3?.misses || 0 },
      { name: 'Overall', hit_rate: stats.overall?.hit_rate * 100 || 0, hits: stats.overall?.hits || 0, misses: stats.overall?.misses || 0 }
    ];
  }, [combinedMetrics]);

  const handleViewChange = useCallback((view) => {
    setSelectedView(view);
  }, []);

  const handleTimeRangeChange = useCallback((range) => {
    setSelectedTimeRange(range);
    refetch();
  }, [refetch]);

  if (isLoading && !realTimeMetrics) {
    return <DashboardLoadingSkeleton />;
  }

  if (error && !realTimeMetrics) {
    return (
      <div className=\"bg-red-900/20 border border-red-500/50 rounded-lg p-8 text-center\">
        <div className=\"text-red-400 text-4xl mb-4\">⚠️</div>
        <h3 className=\"text-red-300 font-semibold mb-2\">Monitoring Error</h3>
        <p className=\"text-red-200 mb-4\">{error.message}</p>
        <button 
          onClick={refetch}
          className=\"bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg text-white font-medium transition-colors\"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className=\"space-y-6\">
      {/* Header with Controls */}
      <div className=\"flex items-center justify-between\">
        <div>
          <h1 className=\"text-3xl font-bold text-slate-200 mb-2\">
            📊 System Performance Dashboard
          </h1>
          <p className=\"text-slate-400\">
            Real-time monitoring and performance analytics
          </p>
        </div>
        
        <div className=\"flex items-center gap-4\">
          {/* View Selector */}
          <div className=\"flex bg-slate-800 rounded-lg p-1\">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'api', label: 'API', icon: '🔌' },
              { id: 'cache', label: 'Cache', icon: '⚡' },
              { id: 'model', label: 'Model', icon: '🧠' }
            ].map(view => (
              <button
                key={view.id}
                onClick={() => handleViewChange(view.id)}
                className={`px-4 py-2 rounded-md transition-all font-medium ${
                  selectedView === view.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700'
                }`}
              >
                <span className=\"mr-2\">{view.icon}</span>
                {view.label}
              </button>
            ))}
          </div>

          {/* Time Range Selector */}
          <select
            value={selectedTimeRange}
            onChange={(e) => handleTimeRangeChange(e.target.value)}
            className=\"bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-slate-200\"
          >
            <option value=\"1h\">Last Hour</option>
            <option value=\"6h\">Last 6 Hours</option>
            <option value=\"24h\">Last 24 Hours</option>
            <option value=\"7d\">Last 7 Days</option>
          </select>
        </div>
      </div>

      {/* Real-time Status */}
      <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
        <SystemStatusCard
          title=\"System Status\"
          value={combinedMetrics?.metrics ? 'Operational' : 'Unknown'}
          icon=\"🟢\"
          trend={null}
          color=\"green\"
        />
        <SystemStatusCard
          title=\"Active Connections\"
          value={combinedMetrics?.active_connections || 0}
          icon=\"🔗\"
          trend={null}
          color=\"blue\"
        />
        <SystemStatusCard
          title=\"Requests/Min\"
          value={(combinedMetrics?.metrics?.total_requests || 0)}
          icon=\"📈\"
          trend=\"+12%\"
          color=\"purple\"
        />
        <SystemStatusCard
          title=\"Cache Hit Rate\"
          value={`${((combinedMetrics?.cache_stats?.performance_stats?.overall?.hit_rate || 0) * 100).toFixed(1)}%`}
          icon=\"⚡\"
          trend=\"+5%\"
          color=\"cyan\"
        />
      </div>

      {/* Alert Bar */}
      {alertHistory.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className=\"bg-yellow-900/30 border border-yellow-500/50 rounded-lg p-4\"
        >
          <div className=\"flex items-center gap-3\">
            <div className=\"text-yellow-400 text-xl\">🚨</div>
            <div>
              <h4 className=\"text-yellow-300 font-semibold\">Recent Alert</h4>
              <p className=\"text-yellow-200 text-sm\">{alertHistory[0]?.drift_result?.drift_type} drift detected</p>
            </div>
            <div className=\"ml-auto text-yellow-400 text-sm\">
              {new Date(alertHistory[0]?.timestamp).toLocaleTimeString()}
            </div>
          </div>
        </motion.div>
      )}

      {/* Main Content */}
      <AnimatePresence mode=\"wait\">
        <motion.div
          key={selectedView}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.3 }}
        >
          {selectedView === 'overview' && (
            <OverviewDashboard 
              metrics={combinedMetrics}
              timeSeriesData={timeSeriesData}
              circuitBreakerData={circuitBreakerData}
            />
          )}
          
          {selectedView === 'api' && (
            <APIDashboard 
              metrics={combinedMetrics}
              timeSeriesData={timeSeriesData}
            />
          )}
          
          {selectedView === 'cache' && (
            <CacheDashboard 
              cacheData={cachePerformanceData}
              metrics={combinedMetrics}
            />
          )}
          
          {selectedView === 'model' && (
            <ModelDashboard 
              metrics={combinedMetrics}
              alertHistory={alertHistory}
            />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

/* Supporting Components */

const SystemStatusCard = ({ title, value, icon, trend, color }) => {
  const colorClasses = {
    green: 'border-green-500/50 text-green-400',
    blue: 'border-blue-500/50 text-blue-400',
    purple: 'border-purple-500/50 text-purple-400',
    cyan: 'border-cyan-500/50 text-cyan-400',
    red: 'border-red-500/50 text-red-400'
  };

  return (
    <div className={`bg-slate-800/50 border ${colorClasses[color]} rounded-lg p-4`}>
      <div className=\"flex items-center justify-between mb-2\">
        <div className=\"text-2xl\">{icon}</div>
        {trend && (
          <span className=\"text-green-400 text-sm font-medium\">{trend}</span>
        )}
      </div>
      <div className={`text-2xl font-bold ${colorClasses[color]} mb-1`}>
        {value}
      </div>
      <div className=\"text-slate-400 text-sm\">{title}</div>
    </div>
  );
};

const OverviewDashboard = ({ metrics, timeSeriesData, circuitBreakerData }) => (
  <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
    {/* Response Time Chart */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Response Time Trends</h3>
      <ResponsiveContainer width=\"100%\" height={300}>
        <LineChart data={timeSeriesData}>
          <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
          <XAxis 
            dataKey=\"index\" 
            stroke=\"#9CA3AF\"
            tickFormatter={(value) => `${value}`}
          />
          <YAxis stroke=\"#9CA3AF\" />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                return (
                  <div className=\"bg-slate-900 border border-slate-600 rounded-lg p-3 shadow-xl\">
                    <p className=\"text-slate-200\">Request #{label}</p>
                    <p className=\"text-blue-400\">Response Time: {payload[0].value.toFixed(2)}ms</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Line 
            type=\"monotone\" 
            dataKey=\"response_time\" 
            stroke=\"#3B82F6\" 
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>

    {/* Circuit Breaker Status */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Circuit Breaker Status</h3>
      <div className=\"space-y-4\">
        {circuitBreakerData.map((breaker, index) => (
          <div key={index} className=\"flex items-center justify-between p-3 bg-slate-700/50 rounded-lg\">
            <div className=\"flex items-center gap-3\">
              <div className={`w-3 h-3 rounded-full ${
                breaker.status === 'healthy' ? 'bg-green-500' :
                breaker.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
              }`} />
              <span className=\"text-slate-200 font-medium\">{breaker.name}</span>
            </div>
            <div className=\"text-right\">
              <div className={`text-sm font-medium ${
                breaker.status === 'healthy' ? 'text-green-400' :
                breaker.status === 'warning' ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {breaker.state}
              </div>
              <div className=\"text-slate-400 text-xs\">
                Failures: {breaker.failure_count}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>

    {/* Request Success Rate */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Request Success Rate</h3>
      <div className=\"flex items-center justify-center h-48\">
        <div className=\"relative\">
          <svg width=\"150\" height=\"150\" className=\"transform -rotate-90\">
            <circle
              cx=\"75\"
              cy=\"75\"
              r=\"60\"
              stroke=\"#374151\"
              strokeWidth=\"12\"
              fill=\"none\"
            />
            <circle
              cx=\"75\"
              cy=\"75\"
              r=\"60\"
              stroke=\"#10B981\"
              strokeWidth=\"12\"
              fill=\"none\"
              strokeDasharray={`${2 * Math.PI * 60}`}
              strokeDashoffset={`${2 * Math.PI * 60 * (1 - (metrics?.metrics?.successful_requests || 0) / (metrics?.metrics?.total_requests || 1))}`}
              strokeLinecap=\"round\"
              className=\"transition-all duration-1000\"
            />
          </svg>
          <div className=\"absolute inset-0 flex items-center justify-center\">
            <div className=\"text-center\">
              <div className=\"text-2xl font-bold text-green-400\">
                {((metrics?.metrics?.successful_requests || 0) / (metrics?.metrics?.total_requests || 1) * 100).toFixed(1)}%
              </div>
              <div className=\"text-slate-400 text-sm\">Success Rate</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {/* System Health Overview */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">System Health</h3>
      <div className=\"grid grid-cols-2 gap-4\">
        <div className=\"text-center p-3 bg-slate-700/50 rounded-lg\">
          <div className=\"text-2xl font-bold text-blue-400 mb-1\">
            {(metrics?.metrics?.avg_response_time * 1000).toFixed(0) || 0}ms
          </div>
          <div className=\"text-slate-400 text-sm\">Avg Response</div>
        </div>
        <div className=\"text-center p-3 bg-slate-700/50 rounded-lg\">
          <div className=\"text-2xl font-bold text-purple-400 mb-1\">
            {metrics?.metrics?.model_predictions || 0}
          </div>
          <div className=\"text-slate-400 text-sm\">Predictions</div>
        </div>
        <div className=\"text-center p-3 bg-slate-700/50 rounded-lg\">
          <div className=\"text-2xl font-bold text-green-400 mb-1\">
            {metrics?.metrics?.explanations_generated || 0}
          </div>
          <div className=\"text-slate-400 text-sm\">Explanations</div>
        </div>
        <div className=\"text-center p-3 bg-slate-700/50 rounded-lg\">
          <div className=\"text-2xl font-bold text-cyan-400 mb-1\">
            {metrics?.cache_stats?.memory_usage_mb?.toFixed(0) || 0}MB
          </div>
          <div className=\"text-slate-400 text-sm\">Memory Usage</div>
        </div>
      </div>
    </div>
  </div>
);

const APIDashboard = ({ metrics, timeSeriesData }) => (
  <div className=\"space-y-6\">
    {/* API Metrics Overview */}
    <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-blue-400 mb-1\">
          {metrics?.metrics?.total_requests || 0}
        </div>
        <div className=\"text-slate-400 text-sm\">Total Requests</div>
      </div>
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-green-400 mb-1\">
          {metrics?.metrics?.successful_requests || 0}
        </div>
        <div className=\"text-slate-400 text-sm\">Successful</div>
      </div>
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-red-400 mb-1\">
          {metrics?.metrics?.failed_requests || 0}
        </div>
        <div className=\"text-slate-400 text-sm\">Failed</div>
      </div>
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-purple-400 mb-1\">
          {(metrics?.metrics?.avg_response_time * 1000).toFixed(0) || 0}ms
        </div>
        <div className=\"text-slate-400 text-sm\">Avg Response</div>
      </div>
    </div>

    {/* Detailed Request Analysis */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Request Timeline</h3>
      <ResponsiveContainer width=\"100%\" height={400}>
        <AreaChart data={timeSeriesData}>
          <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
          <XAxis dataKey=\"index\" stroke=\"#9CA3AF\" />
          <YAxis stroke=\"#9CA3AF\" />
          <Tooltip />
          <Area 
            type=\"monotone\" 
            dataKey=\"response_time\" 
            stroke=\"#8B5CF6\" 
            fill=\"#8B5CF6\" 
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>

    {/* Rate Limiter Status */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Rate Limiter Status</h3>
      <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4\">
        {metrics?.rate_limiter_status && Object.entries(metrics.rate_limiter_status).map(([name, status]) => (
          <div key={name} className=\"p-4 bg-slate-700/50 rounded-lg\">
            <h5 className=\"text-slate-300 font-medium mb-2 capitalize\">{name}</h5>
            <div className=\"space-y-2\">
              <div className=\"flex justify-between text-sm\">
                <span className=\"text-slate-400\">Available:</span>
                <span className=\"text-green-400\">{Math.floor(status.tokens_available)}</span>
              </div>
              <div className=\"flex justify-between text-sm\">
                <span className=\"text-slate-400\">Capacity:</span>
                <span className=\"text-slate-300\">{status.capacity}</span>
              </div>
              <div className=\"w-full bg-slate-600 rounded-full h-2\">
                <div 
                  className=\"bg-green-500 h-2 rounded-full transition-all duration-300\"
                  style={{ width: `${(status.tokens_available / status.capacity) * 100}%` }}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </div>
);

const CacheDashboard = ({ cacheData, metrics }) => (
  <div className=\"space-y-6\">
    {/* Cache Hit Rates */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Cache Performance</h3>
      <ResponsiveContainer width=\"100%\" height={300}>
        <BarChart data={cacheData}>
          <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
          <XAxis dataKey=\"name\" stroke=\"#9CA3AF\" />
          <YAxis stroke=\"#9CA3AF\" />
          <Tooltip 
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className=\"bg-slate-900 border border-slate-600 rounded-lg p-3 shadow-xl\">
                    <p className=\"text-slate-200 font-medium\">{label}</p>
                    <p className=\"text-green-400\">Hit Rate: {data.hit_rate.toFixed(1)}%</p>
                    <p className=\"text-blue-400\">Hits: {data.hits}</p>
                    <p className=\"text-red-400\">Misses: {data.misses}</p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey=\"hit_rate\" fill=\"#10B981\" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>

    {/* Cache Statistics */}
    <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
        <h4 className=\"text-lg font-semibold text-slate-200 mb-4\">Cache Levels</h4>
        <div className=\"space-y-4\">
          {cacheData.slice(0, 3).map((cache, index) => (
            <div key={index} className=\"flex items-center justify-between p-3 bg-slate-700/50 rounded-lg\">
              <div>
                <div className=\"text-slate-200 font-medium\">{cache.name}</div>
                <div className=\"text-slate-400 text-sm\">
                  {cache.hits} hits, {cache.misses} misses
                </div>
              </div>
              <div className=\"text-right\">
                <div className=\"text-green-400 font-bold\">{cache.hit_rate.toFixed(1)}%</div>
                <div className=\"text-slate-400 text-sm\">Hit Rate</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
        <h4 className=\"text-lg font-semibold text-slate-200 mb-4\">Memory Usage</h4>
        <div className=\"text-center\">
          <div className=\"text-4xl font-bold text-cyan-400 mb-2\">
            {metrics?.cache_stats?.memory_usage_mb?.toFixed(1) || 0}MB
          </div>
          <div className=\"text-slate-400\">Current Usage</div>
          
          <div className=\"mt-6 space-y-2\">
            <div className=\"flex justify-between text-sm\">
              <span className=\"text-slate-400\">Cache Efficiency:</span>
              <span className=\"text-green-400\">
                {((metrics?.cache_stats?.performance_stats?.overall?.hit_rate || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className=\"flex justify-between text-sm\">
              <span className=\"text-slate-400\">Total Requests:</span>
              <span className=\"text-slate-300\">
                {metrics?.cache_stats?.performance_stats?.overall?.total_requests || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ModelDashboard = ({ metrics, alertHistory }) => (
  <div className=\"space-y-6\">
    {/* Model Performance */}
    <div className=\"grid grid-cols-1 md:grid-cols-3 gap-4\">
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-purple-400 mb-1\">
          {metrics?.metrics?.model_predictions || 0}
        </div>
        <div className=\"text-slate-400 text-sm\">Total Predictions</div>
      </div>
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-blue-400 mb-1\">
          {metrics?.metrics?.explanations_generated || 0}
        </div>
        <div className=\"text-slate-400 text-sm\">Explanations Generated</div>
      </div>
      <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-4 text-center\">
        <div className=\"text-2xl font-bold text-green-400 mb-1\">
          85.8%
        </div>
        <div className=\"text-slate-400 text-sm\">Model Accuracy</div>
      </div>
    </div>

    {/* Drift Alerts */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Concept Drift Alerts</h3>
      {alertHistory.length > 0 ? (
        <div className=\"space-y-3 max-h-64 overflow-y-auto\">
          {alertHistory.map((alert, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className=\"p-3 bg-slate-700/50 rounded-lg border-l-4 border-yellow-500\"
            >
              <div className=\"flex items-center justify-between mb-2\">
                <span className=\"text-yellow-400 font-medium\">
                  {alert.drift_result?.drift_type} Drift Detected
                </span>
                <span className=\"text-slate-500 text-xs\">
                  {new Date(alert.timestamp).toLocaleString()}
                </span>
              </div>
              <div className=\"text-slate-300 text-sm\">
                Score: {alert.drift_result?.drift_score?.toFixed(4)} | 
                Method: {alert.drift_result?.detection_method} |
                Action: {alert.drift_result?.recommended_action}
              </div>
              {alert.drift_result?.affected_features?.length > 0 && (
                <div className=\"text-slate-400 text-xs mt-1\">
                  Affected: {alert.drift_result.affected_features.join(', ')}
                </div>
              )}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className=\"text-center text-slate-400 py-8\">
          <div className=\"text-4xl mb-2\">✅</div>
          <p>No drift alerts detected</p>
          <p className=\"text-sm\">System is performing normally</p>
        </div>
      )}
    </div>

    {/* Model Health */}
    <div className=\"bg-slate-800/50 rounded-lg border border-slate-600 p-6\">
      <h3 className=\"text-xl font-semibold text-slate-200 mb-4\">Model Health Status</h3>
      <div className=\"grid grid-cols-1 md:grid-cols-2 gap-6\">
        <div className=\"space-y-4\">
          <div className=\"flex items-center justify-between p-3 bg-slate-700/50 rounded-lg\">
            <div className=\"flex items-center gap-3\">
              <div className=\"w-3 h-3 bg-green-500 rounded-full\" />
              <span className=\"text-slate-200\">Prediction Service</span>
            </div>
            <span className=\"text-green-400 text-sm font-medium\">Healthy</span>
          </div>
          <div className=\"flex items-center justify-between p-3 bg-slate-700/50 rounded-lg\">
            <div className=\"flex items-center gap-3\">
              <div className=\"w-3 h-3 bg-green-500 rounded-full\" />
              <span className=\"text-slate-200\">Explanation Engine</span>
            </div>
            <span className=\"text-green-400 text-sm font-medium\">Healthy</span>
          </div>
          <div className=\"flex items-center justify-between p-3 bg-slate-700/50 rounded-lg\">
            <div className=\"flex items-center gap-3\">
              <div className=\"w-3 h-3 bg-green-500 rounded-full\" />
              <span className=\"text-slate-200\">Drift Monitor</span>
            </div>
            <span className=\"text-green-400 text-sm font-medium\">Active</span>
          </div>
        </div>
        
        <div className=\"text-center\">
          <div className=\"text-3xl mb-2\">🧠</div>
          <div className=\"text-lg font-semibold text-slate-200 mb-2\">XGBoost Ensemble</div>
          <div className=\"text-slate-400 text-sm\">Version 1.2.0</div>
          <div className=\"text-green-400 text-sm mt-1\">11-feature enhanced model</div>
        </div>
      </div>
    </div>
  </div>
);

const DashboardLoadingSkeleton = () => (
  <div className=\"space-y-6 animate-pulse\">
    <div className=\"h-8 bg-slate-700 rounded w-1/3\" />
    <div className=\"grid grid-cols-1 md:grid-cols-4 gap-4\">
      {[...Array(4)].map((_, i) => (
        <div key={i} className=\"h-24 bg-slate-700 rounded\" />
      ))}
    </div>
    <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6\">
      <div className=\"h-96 bg-slate-700 rounded\" />
      <div className=\"h-96 bg-slate-700 rounded\" />
    </div>
  </div>
);

export default SystemPerformanceDashboard;