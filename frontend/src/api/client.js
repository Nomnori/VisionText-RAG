const API_BASE = import.meta.env.VITE_API_BASE || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.message || "请求失败");
  }
  return data;
}

export function fetchHealth() {
  return request("/api/health");
}

export function fetchKnowledgeFiles() {
  return request("/api/knowledge");
}

export function ingestKnowledge() {
  return request("/api/ingest", { method: "POST" });
}

export function sendChat(question, topK = 4) {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}
