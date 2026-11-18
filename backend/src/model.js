'use strict';

// Provider adapter keeps the course drafting contract and defaults to local Ollama.
const groq = require('./groq');
const MODEL = process.env.OLLAMA_MODEL || 'qwen2.5:3b';
const provider = () => process.env.GRANT_LLM === 'groq' ? 'Groq Cloud' : 'Ollama';
const stats = { calls: 0, errors: 0, promptTokens: 0, completionTokens: 0, lastError: null };

function isConfigured() {
  return process.env.AURA_LLM !== 'off' && process.env.GRANT_LLM !== 'template' &&
    (provider() === 'Ollama' || groq.isGroqConfigured());
}

async function status() {
  if (provider() !== 'Ollama') return { ...groq.getStats(), provider: provider(), model: groq.GROQ_MODEL };
  try {
    const res = await fetch('http://127.0.0.1:11434/api/tags', { signal: AbortSignal.timeout(2000) });
    if (!res.ok) throw new Error('Ollama returned an error');
    const models = (await res.json()).models?.map((entry) => entry.name) || [];
    const ready = models.includes(MODEL) || models.includes(MODEL + ':latest');
    return { ...stats, configured: ready, ready, model: MODEL, provider: 'Ollama', installedModels: models,
      notice: ready ? 'Local model available' : 'Install the selected model in Ollama' };
  } catch {
    return { ...stats, configured: false, ready: false, model: MODEL, provider: 'Ollama', installedModels: [], notice: 'Start Ollama to use local drafting' };
  }
}

async function generate(options = {}) {
  if (provider() === 'Groq Cloud') return groq.callGroq(options);
  if (!isConfigured()) return { success: false, error: 'Template mode selected', model: MODEL };
  stats.calls += 1;
  const started = Date.now();
  try {
    const messages = options.messages || [
      { role: 'system', content: options.systemPrompt || 'Use the provided evidence. Label proposed work clearly.' },
      { role: 'user', content: options.prompt || '' },
    ];
    const response = await fetch('http://127.0.0.1:11434/api/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL, stream: false, messages,
        ...(options.json ? { format: 'json' } : {}),
        options: { temperature: options.temperature ?? 0.1, num_predict: Math.min(options.maxTokens || 900, 1800), num_ctx: 8192 } }),
      signal: AbortSignal.timeout(Math.min(options.timeoutMs || 60000, 90000)),
    });
    if (!response.ok) throw new Error(`Local model HTTP ${response.status}`);
    const data = await response.json();
    if (typeof data.message?.content !== 'string') throw new Error('Invalid local model response');
    const usage = { promptTokens: data.prompt_eval_count || 0, completionTokens: data.eval_count || 0, totalTokens: (data.prompt_eval_count || 0) + (data.eval_count || 0) };
    stats.promptTokens += usage.promptTokens;
    stats.completionTokens += usage.completionTokens;
    stats.lastError = null;
    return { success: true, content: data.message.content, model: MODEL, usage, latencyMs: Date.now() - started };
  } catch (error) {
    stats.errors += 1;
    stats.lastError = error.name === 'TimeoutError' ? 'Local model timed out' : error.message;
    return { success: false, error: stats.lastError, model: MODEL };
  }
}

module.exports = { callGroq: generate, isGroqConfigured: isConfigured,
  GROQ_MODEL: provider() === 'Ollama' ? MODEL : groq.GROQ_MODEL, provider, status,
  getStats: () => ({ ...stats, configured: isConfigured(), provider: provider(), model: MODEL }) };
