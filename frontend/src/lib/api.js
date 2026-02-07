const API_URL = "http://localhost:8000/api/v1";

// Helper to format dates
const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleString();
};

export const api = {
    // Prompts
    getPrompts: async () => {
        const res = await fetch(`${API_URL}/prompts/`);
        return res.json();
    },
    createPrompt: async (data) => {
        const res = await fetch(`${API_URL}/prompts/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    // Inference
    runInference: async (payload) => {
        const res = await fetch(`${API_URL}/inference/run`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || "Inference failed");
        }
        return res.json();
    },

    // Traces (Phase 4)
    getTraces: async (skip = 0, limit = 100, sortBy = 'timestamp', order = 'desc') => {
        const params = new URLSearchParams({
            skip,
            limit,
            sort_by: sortBy,
            order
        });
        const res = await fetch(`${API_URL}/traces?${params}`);
        if (!res.ok) throw new Error(`Failed to fetch traces: ${res.statusText}`);
        return res.json();
    },

    getTrace: async (traceId) => {
        const res = await fetch(`${API_URL}/traces/${traceId}`);
        if (!res.ok) throw new Error(`Failed to fetch trace: ${res.statusText}`);
        return res.json();
    },

    getTraceEvaluations: async (traceId) => {
        const res = await fetch(`${API_URL}/traces/${traceId}/evaluations`);
        if (!res.ok) throw new Error(`Failed to fetch evaluations: ${res.statusText}`);
        return res.json();
    },

    // Models
    getModels: async () => {
        // This could be an endpoint, but for now we'll define supported ones
        return [
            { id: 'gpt-4-turbo', name: 'OpenAI GPT-4 Turbo', provider: 'openai' },
            { id: 'gpt-3.5-turbo', name: 'OpenAI GPT-3.5 Turbo', provider: 'openai' },
            { id: 'llama2', name: 'Ollama Llama 2 (Local)', provider: 'ollama' },
            { id: 'mistral', name: 'Ollama Mistral (Local)', provider: 'ollama' },
            { id: 'mock-model', name: 'Mock Development Model', provider: 'mock' }
        ];
    },

    // Metrics (Phase 4)
    getMetrics: async () => {
        try {
            const res = await fetch(`${API_URL}/metrics/stats`);
            if (res.ok) return res.json();
        } catch (e) {
            // Fallback to mock data
        }
        // Fallback mock data
        return {
            total_inferences: 1234,
            total_cost_usd: 45.67,
            avg_latency_ms: 523,
            avg_judge_score: 8.2,
            hallucination_rate: 0.03
        };
    },

    getMetricsByVersion: async () => {
        try {
            const res = await fetch(`${API_URL}/metrics/by-version`);
            if (res.ok) return res.json();
        } catch (e) {
            // Fallback to mock data
        }
        return [
            { prompt_version_id: '1', semantic_version: '1.0.0', count: 500, avg_overall_score: 8.5 },
            { prompt_version_id: '2', semantic_version: '1.1.0', count: 400, avg_overall_score: 8.3 },
            { prompt_version_id: '3', semantic_version: '1.2.0', count: 334, avg_overall_score: 8.1 }
        ];
    }
};
