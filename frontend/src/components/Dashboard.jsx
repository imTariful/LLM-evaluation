import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { api } from '../lib/api';
import { Activity, DollarSign, Zap, AlertTriangle, Plus } from 'lucide-react';

const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-medium">{title}</h3>
            <Icon className={`w-5 h-5 ${color}`} />
        </div>
        <div className="text-2xl font-bold text-white">{value}</div>
    </div>
);

export function Dashboard() {
    const [data, setData] = useState([]);
    const [stats, setStats] = useState({
        avg_latency_ms: 0,
        total_cost_usd: 0,
        avg_judge_score: 0,
        hallucination_rate: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const [metrics, trendData] = await Promise.all([
                    api.getMetrics(),
                    api.getMetricsByVersion()
                ]);
                setStats(metrics);
                setData(trendData.map(d => ({
                    timestamp: d.semantic_version,
                    score: d.avg_overall_score,
                    latency: d.avg_latency_ms || 450,
                    cost: d.avg_cost_usd || 0.002
                })));
            } catch (err) {
                console.error("Failed to fetch dashboard metrics:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, []);

    if (loading) return <div className="text-white p-10">Loading Intelligence Telemetry...</div>;

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <StatCard 
                    title="Avg Latency" 
                    value={`${stats.avg_latency_ms}ms`} 
                    icon={Zap} 
                    color="text-yellow-400" 
                />
                <StatCard 
                    title="Total Cost" 
                    value={`$${stats.total_cost_usd?.toFixed(2)}`} 
                    icon={DollarSign} 
                    color="text-green-400" 
                />
                <StatCard 
                    title="Avg Quality Score" 
                    value={`${stats.avg_judge_score?.toFixed(1)}/10`} 
                    icon={Activity} 
                    color="text-blue-400" 
                />
                <StatCard 
                    title="Hallucination Rate" 
                    value={`${(stats.hallucination_rate * 100).toFixed(1)}%`} 
                    icon={AlertTriangle} 
                    color="text-red-400" 
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-lg font-semibold text-white mb-6">Quality Trend (Last 24h)</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                                <YAxis domain={[0, 10]} stroke="#9CA3AF" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }}
                                />
                                <Area type="monotone" dataKey="score" stroke="#60A5FA" fill="#3B82F6" fillOpacity={0.2} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                    <h3 className="text-lg font-semibold text-white mb-6">Latency vs Cost</h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis dataKey="timestamp" stroke="#9CA3AF" />
                                <YAxis yAxisId="left" stroke="#FBBF24" />
                                <YAxis yAxisId="right" orientation="right" stroke="#34D399" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: '#fff' }}
                                />
                                <Legend />
                                <Line yAxisId="left" type="monotone" dataKey="latency" stroke="#FBBF24" name="Latency (ms)" />
                                <Line yAxisId="right" type="monotone" dataKey="cost" stroke="#34D399" name="Cost ($)" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
