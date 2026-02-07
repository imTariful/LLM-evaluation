import React, { useState } from 'react';
import { Eye, CheckCircle, XCircle, AlertOctagon } from 'lucide-react';

// MOCK TRACE DATA
const MOCK_TRACES = [
    { id: '1', prompt: 'Summarize strict versioning', output: 'Semantic versioning uses MAJOR.MINOR.PATCH...', score: 9.5, latency: 400, model: 'gpt-4', hallucination: false, reasoning: 'Perfectly accurate.' },
    { id: '2', prompt: 'Who is CEO of Deepmind?', output: 'As of 2024, Demis Hassabis...', score: 10, latency: 320, model: 'gpt-4', hallucination: false, reasoning: 'Correct.' },
    { id: '3', prompt: 'Explain quantum gravity', output: 'Quantum gravity is a cheese found on the moon...', score: 2.0, latency: 800, model: 'llama-2-7b', hallucination: true, reasoning: 'Complete hallucination. Mentions cheese.' },
];

export function TraceViewer() {
    const [selectedTrace, setSelectedTrace] = useState(null);

    return (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
            <div className="p-6 border-b border-gray-700">
                <h2 className="text-xl font-bold text-white">Inference Traces</h2>
            </div>

            {/* TABLE */}
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-gray-400">
                    <thead className="bg-gray-900 text-gray-200 uppercase font-medium">
                        <tr>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Prompt</th>
                            <th className="px-6 py-4">Model</th>
                            <th className="px-6 py-4">Score</th>
                            <th className="px-6 py-4">Latency</th>
                            <th className="px-6 py-4" />
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                        {MOCK_TRACES.map((trace) => (
                            <tr key={trace.id} className="hover:bg-gray-700/50 transition-colors">
                                <td className="px-6 py-4">
                                    {trace.hallucination ? (
                                        <span className="inline-flex items-center px-2 py-1 rounded bg-red-500/10 text-red-500 text-xs font-bold ring-1 ring-red-500/20">
                                            HALLUCINATION
                                        </span>
                                    ) : (
                                        <span className="inline-flex items-center px-2 py-1 rounded bg-green-500/10 text-green-500 text-xs font-bold ring-1 ring-green-500/20">
                                            PASS
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4 max-w-xs truncate font-mono text-white">{trace.prompt}</td>
                                <td className="px-6 py-4">{trace.model}</td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        <span className={`text-sm font-bold ${trace.score < 5 ? 'text-red-400' : 'text-blue-400'}`}>
                                            {trace.score}
                                        </span>
                                        <span className="text-gray-600">/ 10</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-gray-500">{trace.latency}ms</td>
                                <td className="px-6 py-4 text-right">
                                    <button
                                        onClick={() => setSelectedTrace(trace)}
                                        className="p-2 hover:bg-gray-600 rounded-lg text-gray-300 transition-colors"
                                    >
                                        <Eye size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* MODAL - KILLER FEATURE */}
            {selectedTrace && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
                    <div className="bg-gray-900 border border-gray-700 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl">
                        <div className="p-6 border-b border-gray-700 flex justify-between items-center">
                            <h3 className="text-xl font-bold text-white">Trace Details {selectedTrace.id}</h3>
                            <button onClick={() => setSelectedTrace(null)} className="text-gray-400 hover:text-white">
                                <XCircle />
                            </button>
                        </div>

                        <div className="p-6 space-y-6">
                            {/* Input / Output */}
                            <div className="grid grid-cols-1 gap-6">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase">Input Prompt</label>
                                    <div className="bg-gray-800 p-4 rounded-lg font-mono text-sm text-gray-300 border border-gray-700">
                                        {selectedTrace.prompt}
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase">Model Output</label>
                                    <div className="bg-gray-800 p-4 rounded-lg font-mono text-sm text-blue-100 border border-gray-700">
                                        {selectedTrace.output}
                                    </div>
                                </div>
                            </div>

                            {/* Evaluation Section */}
                            <div className="bg-gray-800/50 p-6 rounded-xl border border-blue-500/20">
                                <div className="flex items-center gap-3 mb-4">
                                    <Activity className="text-blue-400" size={20} />
                                    <h4 className="font-bold text-blue-400">Judge Evaluation</h4>
                                </div>

                                <div className="space-y-4">
                                    <div className="flex justify-between items-center bg-gray-900 p-3 rounded-lg border border-gray-700">
                                        <span className="text-gray-400">Overall Score</span>
                                        <span className="text-xl font-bold text-white">{selectedTrace.score} / 10</span>
                                    </div>

                                    <div>
                                        <label className="text-xs font-bold text-gray-500 uppercase">Reasoning</label>
                                        <p className="mt-2 text-gray-300 leading-relaxed">
                                            {selectedTrace.reasoning}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Helper icon
function Activity({ className, ...props }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24" height="24" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
            className={className} {...props}>
            <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
        </svg>
    )
}
