import React, { useState, useEffect } from 'react';
import { Play, Copy, CheckCircle, AlertCircle, Loader, Shield, Brain, Zap, DollarSign, List } from 'lucide-react';
import { api } from '../lib/api';

export function TestRunner() {
    const [testState, setTestState] = useState('idle'); // idle, running, success, error
    const [formData, setFormData] = useState({
        promptName: 'greeting',
        variables: '{"name": "User", "topic": "AI"}',
        model: 'gpt-3.5-turbo',
        temperature: 0.7,
        provider: 'openai'
    });
    const [models, setModels] = useState([]);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        api.getModels().then(setModels);
    }, []);

    const handleInputChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
    };

    const runTest = async () => {
        setTestState('running');
        setError(null);
        setResult(null);

        try {
            // Parse variables
            let variables;
            try {
                variables = JSON.parse(formData.variables);
            } catch (e) {
                throw new Error('Invalid JSON in variables field: ' + e.message);
            }

            // Call backend inference endpoint
            const data = await api.runInference({
                prompt_name: formData.promptName,
                variables: variables,
                model: formData.model,
                temperature: parseFloat(formData.temperature),
                session_id: 'test-session-' + Date.now(),
                user_id: 'test-user',
            });

            if (data.error) throw new Error(data.error);

            // Poll for evaluation results (simplified for now, ideally we'd have a status)
            // Wait a bit for background tasks
            await new Promise(r => setTimeout(r, 2000));
            const evaluations = await api.getTraceEvaluations(data.trace_id);

            setResult({
                ...data,
                evaluations: evaluations || []
            });

            setTestState('success');
        } catch (err) {
            setError(err.message || 'An error occurred during testing.');
            setTestState('error');
        }
    };

    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="space-y-6">
            <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
                <h2 className="text-2xl font-bold text-white mb-6">Create & Run Test</h2>

                <div className="space-y-4">
                    {/* Prompt Name */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Prompt Name</label>
                            <input
                                type="text"
                                value={formData.promptName}
                                onChange={(e) => handleInputChange('promptName', e.target.value)}
                                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Model</label>
                            <select
                                value={formData.model}
                                onChange={(e) => handleInputChange('model', e.target.value)}
                                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500"
                            >
                                {models.map(m => (
                                    <option key={m.id} value={m.id}>{m.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">Temperature ({formData.temperature})</label>
                            <input
                                type="range"
                                min="0"
                                max="2"
                                step="0.1"
                                value={formData.temperature}
                                onChange={(e) => handleInputChange('temperature', e.target.value)}
                                className="w-full"
                            />
                        </div>
                    </div>

                    {/* Variables JSON */}
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Input Variables (JSON)</label>
                        <textarea
                            value={formData.variables}
                            onChange={(e) => handleInputChange('variables', e.target.value)}
                            rows="4"
                            placeholder='{"name": "User", "topic": "AI"}'
                            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded text-white focus:outline-none focus:border-blue-500 font-mono text-sm"
                        />
                        <p className="text-xs text-gray-400 mt-1">Must be valid JSON format</p>
                    </div>

                    {/* Evaluation Criteria */}
                    {/* Removed manually since it is handled by the Intelligence Plane Judges */}

                    {/* Run Button */}
                    <button
                        onClick={runTest}
                        disabled={testState === 'running'}
                        className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white font-bold py-3 px-4 rounded transition flex items-center justify-center gap-2"
                    >
                        {testState === 'running' ? (
                            <>
                                <Loader className="w-5 h-5 animate-spin" />
                                Running Test...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5" />
                                Run Test
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div className="bg-red-900 border border-red-700 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                        <h3 className="font-semibold text-white mb-1">Test Failed</h3>
                        <p className="text-red-100 text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* Results */}
            {result && testState === 'success' && (
                <div className="bg-green-900 border border-green-700 rounded-lg p-6 space-y-4">
                    <div className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                            <h3 className="font-semibold text-white mb-1">Test Passed!</h3>
                            <p className="text-green-100 text-sm">Inference completed successfully and logged to database.</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div className="bg-black/20 p-3 rounded flex items-center gap-2">
                            <Zap className="w-4 h-4 text-yellow-400" />
                            <div>
                                <p className="text-gray-300 text-xs font-medium">Latency</p>
                                <p className="text-white font-mono">{result.latency_ms}ms</p>
                            </div>
                        </div>
                        <div className="bg-black/20 p-3 rounded flex items-center gap-2">
                            <Brain className="w-4 h-4 text-blue-400" />
                            <div>
                                <p className="text-gray-300 text-xs font-medium">Tokens</p>
                                <p className="text-white font-mono">{result.tokens_in + result.tokens_out}</p>
                            </div>
                        </div>
                        <div className="bg-black/20 p-3 rounded flex items-center gap-2">
                            <DollarSign className="w-4 h-4 text-green-400" />
                            <div>
                                <p className="text-gray-300 text-xs font-medium">Cost</p>
                                <p className="text-white font-mono">${result.cost_usd.toFixed(5)}</p>
                            </div>
                        </div>
                        <div className="bg-black/20 p-3 rounded flex items-center gap-2">
                            <List className="w-4 h-4 text-purple-400" />
                            <div>
                                <p className="text-gray-300 text-xs font-medium">Model</p>
                                <p className="text-white font-mono truncate max-w-[80px]">{result.model}</p>
                            </div>
                        </div>
                    </div>

                    {/* Evaluation Intelligence */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                            <Shield className="w-4 h-4 text-blue-500" />
                            Intelligence Plane Evaluations
                        </h4>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {result.evaluations.map((eval_item, idx) => (
                                <div key={idx} className="bg-black/30 p-4 rounded-lg border border-white/5">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{eval_item.evaluator_id}</span>
                                        <span className={`px-2 py-0.5 rounded text-xs font-bold ${eval_item.overall_score > 7 ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                                            SCORE: {eval_item.overall_score}/10
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-300 italic">"{eval_item.reasoning}"</p>
                                    
                                    {eval_item.scores && (
                                        <div className="mt-3 grid grid-cols-2 gap-2 text-[10px]">
                                            {Object.entries(eval_item.scores).filter(([k]) => k !== 'reasoning').map(([key, val]) => (
                                                <div key={key} className="flex justify-between border-b border-white/5 pb-1">
                                                    <span className="text-gray-500 capitalize">{key}</span>
                                                    <span className="text-white">{val}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-black/20 p-4 rounded">
                        <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-white text-sm">Output</h4>
                            <button
                                onClick={() => copyToClipboard(result.output)}
                                className="text-green-300 hover:text-green-200 flex items-center gap-1"
                            >
                                <Copy className="w-4 h-4" />
                                Copy
                            </button>
                        </div>
                        <p className="text-green-100 text-sm whitespace-pre-wrap">{result.output}</p>
                    </div>

                    <div className="bg-black/20 p-4 rounded">
                        <p className="text-gray-300 text-xs font-medium mb-1">Trace ID</p>
                        <div className="flex items-center gap-2">
                            <p className="text-white font-mono text-xs break-all">{result.trace_id}</p>
                            <button
                                onClick={() => copyToClipboard(result.trace_id)}
                                className="text-green-300 hover:text-green-200"
                            >
                                <Copy className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
