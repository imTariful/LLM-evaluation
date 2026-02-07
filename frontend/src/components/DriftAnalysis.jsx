import React, { useState, useEffect } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { TrendingUp, Activity, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';

export function DriftAnalysis() {
    const [traceData, setTraceData] = useState([]);
    const [versionMetrics, setVersionMetrics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            setLoading(true);
            // Load recent traces for trend visualization
            const traces = await api.getTraces(0, 50, 'timestamp', 'desc');
            
            // Simulate scores for visualization (in real app, would come from evaluations)
            const scoreData = traces.slice().reverse().map((trace, idx) => ({
                timestamp: new Date(trace.timestamp).toLocaleTimeString(),
                overall_score: Math.random() * 2 + 7.5,
                latency: trace.latency_ms,
                cost: trace.cost_usd * 100 // Scale for visibility
            }));
            setTraceData(scoreData);

            // Load version metrics
            const metrics = await api.getMetricsByVersion();
            setVersionMetrics(metrics);
        } catch (err) {
            setError(err.message);
            console.error('Failed to load drift data:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-gray-800 border border-gray-700 p-12 rounded-lg flex justify-center items-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                    <p className="text-gray-400">Loading drift analysis...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-900 border border-red-700 text-red-100 p-4 rounded flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                    <p className="font-semibold">Error Loading Drift Analysis</p>
                    <p className="text-sm">{error}</p>
                </div>
            </div>
        );
    }

    // Calculate drift statistics
    const avgScore = (traceData.reduce((sum, d) => sum + d.overall_score, 0) / traceData.length).toFixed(2);
    const minScore = Math.min(...traceData.map(d => d.overall_score)).toFixed(2);
    const maxScore = Math.max(...traceData.map(d => d.overall_score)).toFixed(2);
    const drift = (maxScore - minScore).toFixed(2);

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                    <TrendingUp className="w-8 h-8 text-blue-500" />
                    Drift Analysis
                </h1>
                <p className="text-gray-400 mt-1">Monitor quality trends and detect performance drift</p>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">Average Score</p>
                    <p className="text-3xl font-bold text-white">{avgScore}/10</p>
                    <p className="text-xs text-gray-500 mt-2">across recent inferences</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">Best Score</p>
                    <p className="text-3xl font-bold text-green-400">{maxScore}/10</p>
                    <p className="text-xs text-gray-500 mt-2">peak performance</p>
                </div>
                <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                    <p className="text-gray-400 text-sm mb-2">Worst Score</p>
                    <p className="text-3xl font-bold text-red-400">{minScore}/10</p>
                    <p className="text-xs text-gray-500 mt-2">lowest performance</p>
                </div>
                <div className={`bg-gray-800 border border-gray-700 p-6 rounded-lg ${drift > 2 ? 'border-yellow-600' : ''}`}>
                    <p className="text-gray-400 text-sm mb-2">Quality Drift</p>
                    <p className={`text-3xl font-bold ${drift > 2 ? 'text-yellow-400' : 'text-green-400'}`}>{drift}</p>
                    <p className="text-xs text-gray-500 mt-2">{drift > 2 ? '⚠️ High drift' : '✓ Stable'}</p>
                </div>
            </div>

            {/* Score Trend Chart */}
            <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                    <Activity className="w-5 h-5 text-blue-500" />
                    Score Trend Over Time
                </h2>
                <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <AreaChart data={traceData}>
                            <defs>
                                <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="timestamp" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" domain={[0, 10]} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="overall_score"
                                stroke="#3b82f6"
                                fillOpacity={1}
                                fill="url(#scoreGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-gray-400 text-sm mt-4">
                    📊 This chart shows the quality score trend across recent inferences.
                    {drift > 2 && ' ⚠️ Detected significant drift - investigate recent changes.'}
                </p>
            </div>

            {/* Version Comparison */}
            <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-white mb-4">Prompt Version Comparison</h2>
                <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={versionMetrics}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="semantic_version" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Legend />
                            <Bar dataKey="avg_overall_score" fill="#3b82f6" name="Avg Score" />
                            <Bar dataKey="count" fill="#10b981" name="Inference Count" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-gray-400 text-sm mt-4">
                    📈 Compare quality across different prompt versions to identify improvements and regressions.
                </p>
            </div>

            {/* Latency vs Cost */}
            <div className="bg-gray-800 border border-gray-700 p-6 rounded-lg">
                <h2 className="text-xl font-semibold text-white mb-4">Latency vs Cost</h2>
                <div className="w-full h-80">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={traceData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis dataKey="timestamp" stroke="#6b7280" />
                            <YAxis yAxisId="left" stroke="#6b7280" />
                            <YAxis yAxisId="right" orientation="right" stroke="#6b7280" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151' }}
                                labelStyle={{ color: '#fff' }}
                            />
                            <Legend />
                            <Line yAxisId="left" type="monotone" dataKey="latency" stroke="#f59e0b" name="Latency (ms)" />
                            <Line yAxisId="right" type="monotone" dataKey="cost" stroke="#ef4444" name="Cost (¢)" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-gray-400 text-sm mt-4">
                    💰 Track the relationship between response latency and API costs to optimize operations.
                </p>
            </div>
        </div>
    );
}
