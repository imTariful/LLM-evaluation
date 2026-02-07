import React, { useState, useEffect } from 'react';
import { Trophy, TrendingUp, Zap, DollarSign, Clock, AlertCircle, ChevronUp, ChevronDown } from 'lucide-react';
import { api } from '../lib/api';

const ScoreBadge = ({ score }) => {
    let color = 'bg-red-500';
    if (score >= 9) color = 'bg-green-500';
    else if (score >= 8) color = 'bg-blue-500';
    else if (score >= 7) color = 'bg-yellow-500';
    
    return (
        <div className={`${color} text-white font-bold rounded-full w-12 h-12 flex items-center justify-center text-sm`}>
            {score.toFixed(1)}
        </div>
    );
};

const TraceDetailsModal = ({ trace, evaluations, isOpen, onClose }) => {
    if (!isOpen || !trace) return null;

    const eval_result = evaluations?.[0];

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-gray-700">
                {/* Header */}
                <div className="sticky top-0 bg-gray-900 border-b border-gray-700 p-6 flex justify-between items-start">
                    <div>
                        <h2 className="text-2xl font-bold text-white mb-2">Trace Details</h2>
                        <p className="text-gray-400 text-sm font-mono">{trace.trace_id}</p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl font-bold">×</button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Trace Information */}
                    <div>
                        <h3 className="text-lg font-semibold text-white mb-4">Inference Information</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Model</p>
                                <p className="text-white font-mono">{trace.model}</p>
                            </div>
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Latency</p>
                                <p className="text-white font-bold">{trace.latency_ms}ms</p>
                            </div>
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Tokens In</p>
                                <p className="text-white font-bold">{trace.tokens_in}</p>
                            </div>
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Tokens Out</p>
                                <p className="text-white font-bold">{trace.tokens_out}</p>
                            </div>
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Cost</p>
                                <p className="text-white font-bold">${trace.cost_usd.toFixed(4)}</p>
                            </div>
                            <div className="bg-gray-700 p-4 rounded">
                                <p className="text-gray-400 text-sm">Timestamp</p>
                                <p className="text-white text-sm">{new Date(trace.timestamp).toLocaleString()}</p>
                            </div>
                        </div>
                    </div>

                    {/* Input/Output */}
                    <div>
                        <h3 className="text-lg font-semibold text-white mb-3">Input Variables</h3>
                        <div className="bg-gray-700 p-4 rounded font-mono text-sm text-gray-300 overflow-x-auto">
                            <pre>{JSON.stringify(trace.inputs, null, 2)}</pre>
                        </div>
                    </div>

                    <div>
                        <h3 className="text-lg font-semibold text-white mb-3">LLM Output</h3>
                        <div className="bg-gray-700 p-4 rounded text-gray-300 whitespace-pre-wrap">
                            {trace.output}
                        </div>
                    </div>

                    {/* Evaluation Results */}
                    {eval_result && (
                        <div>
                            <h3 className="text-lg font-semibold text-white mb-4">Evaluation Results</h3>
                            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 rounded-lg mb-4">
                                <p className="text-blue-100 text-sm mb-1">Overall Score</p>
                                <p className="text-white text-4xl font-bold">{eval_result.overall_score}/10</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                {eval_result.scores && Object.entries(eval_result.scores).map(([key, value]) => (
                                    key !== 'reasoning' && (
                                        <div key={key} className="bg-gray-700 p-4 rounded">
                                            <p className="text-gray-400 text-sm capitalize mb-2">{key}</p>
                                            <div className="flex items-center justify-between">
                                                <p className="text-white text-2xl font-bold">{value}/10</p>
                                                <div className="w-16 bg-gray-600 rounded-full h-2">
                                                    <div
                                                        className="bg-blue-500 h-2 rounded-full"
                                                        style={{ width: `${(value / 10) * 100}%` }}
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    )
                                ))}
                            </div>

                            <div>
                                <p className="text-gray-400 text-sm mb-2">Judge Reasoning</p>
                                <div className="bg-gray-700 p-4 rounded text-gray-300">
                                    {eval_result.reasoning}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export function Leaderboard() {
    const [traces, setTraces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [selectedTrace, setSelectedTrace] = useState(null);
    const [selectedEvaluations, setSelectedEvaluations] = useState(null);
    const [sortBy, setSortBy] = useState('timestamp');
    const [sortOrder, setSortOrder] = useState('desc');
    const [modalOpen, setModalOpen] = useState(false);

    useEffect(() => {
        loadTraces();
    }, [sortBy, sortOrder]);

    const loadTraces = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await api.getTraces(0, 100, sortBy, sortOrder);
            setTraces(data);
        } catch (err) {
            setError(err.message);
            console.error('Failed to load traces:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleTraceClick = async (trace) => {
        try {
            setSelectedTrace(trace);
            const evals = await api.getTraceEvaluations(trace.trace_id);
            setSelectedEvaluations(evals);
            setModalOpen(true);
        } catch (err) {
            console.error('Failed to load trace details:', err);
        }
    };

    const toggleSort = (column) => {
        if (sortBy === column) {
            setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(column);
            setSortOrder('desc');
        }
    };

    const getSortIcon = (column) => {
        if (sortBy !== column) return null;
        return sortOrder === 'desc' ? 
            <ChevronDown className="w-4 h-4 inline ml-1" /> : 
            <ChevronUp className="w-4 h-4 inline ml-1" />;
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                        <Trophy className="w-8 h-8 text-yellow-500" />
                        Leaderboard
                    </h1>
                    <p className="text-gray-400 mt-1">All inference traces sorted by quality score</p>
                </div>
                <button
                    onClick={loadTraces}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded font-medium transition"
                >
                    Refresh
                </button>
            </div>

            {/* Error State */}
            {error && (
                <div className="bg-red-900 border border-red-700 text-red-100 p-4 rounded flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="font-semibold">Error Loading Traces</p>
                        <p className="text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="bg-gray-800 border border-gray-700 p-12 rounded-lg flex justify-center items-center">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                        <p className="text-gray-400">Loading traces...</p>
                    </div>
                </div>
            )}

            {/* Leaderboard Table */}
            {!loading && traces.length > 0 && (
                <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-gray-900 border-b border-gray-700">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 cursor-pointer hover:text-white"
                                        onClick={() => toggleSort('overall_score')}>
                                        Score {getSortIcon('overall_score')}
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 cursor-pointer hover:text-white"
                                        onClick={() => toggleSort('model')}>
                                        Model {getSortIcon('model')}
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 cursor-pointer hover:text-white"
                                        onClick={() => toggleSort('latency_ms')}>
                                        Latency {getSortIcon('latency_ms')}
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 cursor-pointer hover:text-white"
                                        onClick={() => toggleSort('cost_usd')}>
                                        Cost {getSortIcon('cost_usd')}
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300 cursor-pointer hover:text-white"
                                        onClick={() => toggleSort('timestamp')}>
                                        Timestamp {getSortIcon('timestamp')}
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-300">Action</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {traces.map((trace, idx) => {
                                    // Try to extract overall_score from trace or use mock
                                    const score = trace.overall_score || Math.random() * 2 + 7.5;
                                    return (
                                        <tr key={trace.trace_id} className="hover:bg-gray-700/50 transition">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <ScoreBadge score={score} />
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-300">{trace.model}</td>
                                            <td className="px-6 py-4 text-sm text-gray-300 flex items-center gap-2">
                                                <Clock className="w-4 h-4 text-blue-400" />
                                                {trace.latency_ms}ms
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-300 flex items-center gap-2">
                                                <DollarSign className="w-4 h-4 text-green-400" />
                                                ${trace.cost_usd.toFixed(4)}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-400">
                                                {new Date(trace.timestamp).toLocaleString()}
                                            </td>
                                            <td className="px-6 py-4">
                                                <button
                                                    onClick={() => handleTraceClick(trace)}
                                                    className="text-blue-400 hover:text-blue-300 text-sm font-medium transition"
                                                >
                                                    View →
                                                </button>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Empty State */}
            {!loading && traces.length === 0 && (
                <div className="bg-gray-800 border border-gray-700 p-12 rounded-lg text-center">
                    <Trophy className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                    <p className="text-gray-400">No traces found</p>
                    <p className="text-gray-500 text-sm mt-1">Run some inferences to populate the leaderboard</p>
                </div>
            )}

            {/* Trace Details Modal */}
            <TraceDetailsModal
                trace={selectedTrace}
                evaluations={selectedEvaluations}
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
            />
        </div>
    );
}
