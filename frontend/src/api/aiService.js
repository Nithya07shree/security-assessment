const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.error ?? data?.detail ?? `Request failed (${response.status})`;
    throw new Error(message);
  }

  return data;
}

export function getHealth() {
  return request("/health");
}

export function describeControl(rule) {
  return request("/describe", {
    method: "POST",
    body: JSON.stringify({ rule }),
  });
}

export function recommendControl(rule) {
  return request("/recommend", {
    method: "POST",
    body: JSON.stringify({ rule }),
  });
}

export function categoriseControl(rule) {
  return request("/categorise", {
    method: "POST",
    body: JSON.stringify({ rule }),
  });
}

export function queryKnowledge(question) {
  return request("/query", {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

export function analyseDocument(text) {
  return request("/analyse-document", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function generateReport(input) {
  return request("/generate-report", {
    method: "POST",
    body: JSON.stringify({ input }),
  });
}

export const ENDPOINT_ACTIONS = {
  describe: describeControl,
  recommend: recommendControl,
  categorise: categoriseControl,
  query: queryKnowledge,
  analyse: analyseDocument,
  report: generateReport,
};
