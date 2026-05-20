import { useCallback, useEffect, useRef, useState } from "react";
import {
  categoriseControl,
  describeControl,
  ENDPOINT_ACTIONS,
  getHealth,
  recommendControl,
} from "./api/aiService";
import ResultViewer from "./components/ResultViewer";

const SERVICES = [
  {
    id: "describe",
    title: "Control Description",
    category: "Analysis",
    description:
      "Produce a formal control statement and scope summary from auditor notes or raw findings.",
    placeholder:
      "Describe the control gap, affected systems, and evidence observed during review…",
    inputLabel: "Finding or control narrative",
  },
  {
    id: "recommend",
    title: "Remediation Advisory",
    category: "Remediation",
    description:
      "Generate prioritised corrective actions aligned to risk and implementation effort.",
    placeholder:
      "Summarise the deficiency and any constraints (timeline, budget, tooling)…",
    inputLabel: "Deficiency summary",
  },
  {
    id: "categorise",
    title: "Risk Classification",
    category: "Governance",
    description:
      "Map findings to standard security domains for reporting and trend analysis.",
    placeholder:
      "State the observation in plain language; classification follows policy taxonomy…",
    inputLabel: "Observation text",
  },
  {
    id: "query",
    title: "Policy & Controls Search",
    category: "Knowledge",
    description:
      "Query the organisational controls library and seeded reference materials.",
    placeholder:
      "Ask about a control requirement, framework mapping, or implementation guidance…",
    inputLabel: "Search query",
  },
  {
    id: "analyse",
    title: "Document Review",
    category: "Review",
    description:
      "Extract findings, risk themes, and actionable items from assessment artefacts.",
    placeholder:
      "Paste audit notes, interview transcripts, or policy excerpts for structured review…",
    inputLabel: "Source material",
  },
  {
    id: "report",
    title: "Executive Summary",
    category: "Reporting",
    description:
      "Draft board-ready narrative covering scope, material findings, and recommendations.",
    placeholder:
      "Provide engagement context, scope boundaries, and headline outcomes to include…",
    inputLabel: "Engagement summary",
  },
];

function formatTimestamp() {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date());
}

export default function Tool53Dashboard() {
  const workspaceRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedService, setSelectedService] = useState(null);
  const [inputText, setInputText] = useState("");
  const [health, setHealth] = useState({ status: "checking" });
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeAction, setActiveAction] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [completedAt, setCompletedAt] = useState(null);

  const activeService = SERVICES.find((s) => s.id === selectedService);

  const refreshHealth = useCallback(async () => {
    setHealth({ status: "checking" });
    try {
      const data = await getHealth();
      setHealthData(data);
      setHealth({ status: "healthy" });
    } catch (err) {
      setHealthData(null);
      setHealth({ status: "unhealthy", message: err.message });
    }
  }, []);

  useEffect(() => {
    refreshHealth();
  }, [refreshHealth]);

  const handleSelectService = (serviceId) => {
    setSelectedService(serviceId);
    setError(null);
    setResult(null);
    setCompletedAt(null);
    workspaceRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleSendRequest = async () => {
    if (!activeService) {
      setError("Select an analysis service from the catalog below.");
      return;
    }

    const trimmed = inputText.trim();
    if (!trimmed) {
      setError(`Provide ${activeService.inputLabel.toLowerCase()} before submitting.`);
      setResult(null);
      return;
    }

    const runner = ENDPOINT_ACTIONS[selectedService];
    if (!runner) return;

    setLoading(true);
    setActiveAction(selectedService);
    setError(null);
    setResult(null);
    setCompletedAt(null);

    try {
      const data = await runner(trimmed);
      setResult({ actionId: selectedService, data });
      setCompletedAt(formatTimestamp());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setActiveAction(null);
    }
  };

  const handleComprehensiveReview = async () => {
    if (!inputText.trim()) {
      setError("Provide a finding narrative before running a comprehensive review.");
      return;
    }

    const trimmed = inputText.trim();
    setLoading(true);
    setActiveAction("assessment");
    setError(null);
    setResult(null);
    setCompletedAt(null);

    try {
      const [description, recommendations, category] = await Promise.all([
        describeControl(trimmed),
        recommendControl(trimmed),
        categoriseControl(trimmed),
      ]);
      setResult({
        actionId: "assessment",
        data: { description, recommendations, category },
      });
      setCompletedAt(formatTimestamp());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      setActiveAction(null);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setInputText(String(reader.result ?? ""));
      handleSelectService("analyse");
      event.target.value = "";
    };
    reader.readAsText(file);
  };

  const isHealthy = health.status === "healthy";
  const isChecking = health.status === "checking";
  const isSending = activeAction === selectedService;
  const isComprehensive = activeAction === "assessment";

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <header className="bg-slate-900 text-white border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-6 py-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="h-10 w-10 rounded-lg bg-white/10 flex items-center justify-center text-sm font-bold tracking-wide">
              T53
            </div>
            <div>
              <p className="text-[11px] uppercase tracking-widest text-slate-400 font-medium">
                Security Controls Program
              </p>
              <h1 className="text-xl font-semibold tracking-tight">
                Tool-53 Assessment Console
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span className="hidden sm:inline text-slate-400">Analysis engine</span>
            <span
              className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-md border text-xs font-medium ${
                isHealthy
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : isChecking
                    ? "bg-slate-800 border-slate-700 text-slate-300"
                    : "bg-red-500/10 border-red-500/30 text-red-300"
              }`}
            >
              <span
                className={`h-1.5 w-1.5 rounded-full ${
                  isHealthy
                    ? "bg-emerald-400"
                    : isChecking
                      ? "bg-slate-400 animate-pulse"
                      : "bg-red-400"
                }`}
              />
              {isChecking
                ? "Checking availability"
                : isHealthy
                  ? "Operational"
                  : "Unavailable"}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        <section
          ref={workspaceRef}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6 scroll-mt-6"
        >
          <div className="lg:col-span-2 bg-white rounded-lg border border-slate-200 shadow-sm">
            <div className="px-6 py-4 border-b border-slate-200 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Assessment workspace
                </h2>
                <p className="text-sm text-slate-500 mt-0.5">
                  Select an analysis service below, then submit material for
                  processing.
                </p>
              </div>

              {activeService ? (
                <div className="flex flex-col items-start sm:items-end gap-1">
                  <span className="text-[11px] uppercase tracking-wide text-slate-400 font-medium">
                    Active service
                  </span>
                  <span className="inline-flex items-center gap-2 px-3 py-1 rounded-md bg-slate-900 text-white text-sm font-medium">
                    {activeService.title}
                  </span>
                  <span className="text-xs text-slate-500">
                    {activeService.category}
                  </span>
                </div>
              ) : (
                <span className="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-md">
                  No service selected
                </span>
              )}
            </div>

            <div className="p-6 space-y-5">
              {!activeService && (
                <p className="text-sm text-slate-600 bg-slate-50 border border-slate-200 rounded-md px-4 py-3">
                  Choose an analysis service from the catalog at the bottom of
                  this page. Each service performs a distinct step in the
                  assessment workflow—descriptions, remediation guidance,
                  classification, and reporting are handled separately.
                </p>
              )}

              {activeService && (
                <p className="text-sm text-slate-600 leading-relaxed">
                  {activeService.description}
                </p>
              )}

              <div>
                <label
                  htmlFor="assessment-input"
                  className="block text-sm font-medium text-slate-700 mb-1.5"
                >
                  {activeService?.inputLabel ?? "Submission content"}
                </label>
                <textarea
                  id="assessment-input"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  placeholder={
                    activeService?.placeholder ??
                    "Select a service below to enable input…"
                  }
                  disabled={!activeService}
                  className="w-full h-48 rounded-md border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-slate-400 focus:border-slate-400 resize-none disabled:opacity-60 disabled:cursor-not-allowed"
                />
              </div>

              <div className="flex flex-wrap items-center gap-3 pt-1">
                <button
                  type="button"
                  onClick={handleSendRequest}
                  disabled={loading || !isHealthy || !activeService}
                  className="px-5 py-2.5 rounded-md bg-slate-900 text-white text-sm font-medium hover:bg-slate-800 transition disabled:opacity-50"
                >
                  {isSending ? "Processing…" : "Submit for analysis"}
                </button>

                <button
                  type="button"
                  onClick={handleComprehensiveReview}
                  disabled={loading || !isHealthy}
                  className="px-4 py-2.5 rounded-md border border-slate-300 bg-white text-sm font-medium text-slate-700 hover:bg-slate-50 transition disabled:opacity-50"
                  title="Runs description, remediation, and classification together"
                >
                  {isComprehensive
                    ? "Processing…"
                    : "Comprehensive review"}
                </button>

                {selectedService === "analyse" && (
                  <>
                    <button
                      type="button"
                      onClick={() => fileInputRef.current?.click()}
                      disabled={loading || !isHealthy}
                      className="px-4 py-2.5 rounded-md border border-slate-300 bg-white text-sm text-slate-700 hover:bg-slate-50 transition disabled:opacity-50"
                    >
                      Import document
                    </button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".txt,.md,.csv,.json"
                      className="hidden"
                      onChange={handleFileUpload}
                    />
                  </>
                )}
              </div>

              {(result || error) && (
                <div className="rounded-md border border-slate-200 overflow-hidden">
                  <div className="px-4 py-3 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-2">
                    <p className="text-sm font-medium text-slate-800">
                      {error
                        ? "Submission could not be completed"
                        : result?.actionId === "assessment"
                          ? "Comprehensive review output"
                          : `${activeService?.title ?? "Analysis"} — results`}
                    </p>
                    {completedAt && !error && (
                      <span className="text-xs text-slate-500">
                        Completed {completedAt}
                      </span>
                    )}
                  </div>
                  <div className="p-4">
                    {error ? (
                      <p className="text-sm text-red-700 px-4 py-3">{error}</p>
                    ) : (
                      <div className="max-h-[32rem] overflow-y-auto">
                        <ResultViewer
                          actionId={result.actionId}
                          data={result.data}
                        />
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>

          <aside className="bg-white rounded-lg border border-slate-200 shadow-sm h-fit">
            <div className="px-5 py-4 border-b border-slate-200 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
                Platform status
              </h3>
              <button
                type="button"
                onClick={refreshHealth}
                className="text-xs text-slate-500 hover:text-slate-800 font-medium"
              >
                Refresh
              </button>
            </div>

            <dl className="px-5 py-4 space-y-4 text-sm">
              <div>
                <dt className="text-slate-500">Analysis engine</dt>
                <dd className="font-medium text-slate-900 mt-0.5">
                  {healthData?.model_name ?? "—"}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Policy library</dt>
                <dd className="font-medium text-slate-900 mt-0.5">
                  {healthData
                    ? `${healthData.chroma_doc_count} reference documents`
                    : "—"}
                </dd>
              </div>
              {health.status === "unhealthy" && (
                <p className="text-xs text-red-600 pt-1 border-t border-slate-100">
                  {health.message}
                </p>
              )}
            </dl>
          </aside>
        </section>

        <section>
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-900">
              Analysis services
            </h2>
            <p className="text-sm text-slate-500 mt-1 max-w-3xl">
              Each card represents a dedicated capability within the assessment
              platform. Select one to configure the workspace above—services are
              composable and may be run independently or as part of a
              comprehensive review.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {SERVICES.map((service) => {
              const isSelected = selectedService === service.id;
              return (
                <button
                  key={service.id}
                  type="button"
                  onClick={() => handleSelectService(service.id)}
                  className={`text-left bg-white rounded-lg border p-5 transition ${
                    isSelected
                      ? "border-slate-900 shadow-md ring-1 ring-slate-900"
                      : "border-slate-200 shadow-sm hover:border-slate-400 hover:shadow"
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="text-[10px] uppercase tracking-wider font-semibold text-slate-400">
                        {service.category}
                      </span>
                      <h3 className="font-semibold text-slate-900 mt-1">
                        {service.title}
                      </h3>
                    </div>
                    {isSelected && (
                      <span className="shrink-0 text-[10px] uppercase tracking-wide font-semibold text-white bg-slate-900 px-2 py-1 rounded">
                        Active
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-slate-600 mt-3 leading-relaxed">
                    {service.description}
                  </p>
                </button>
              );
            })}
          </div>
        </section>
      </main>

      <footer className="border-t border-slate-200 bg-white mt-4">
        <div className="max-w-7xl mx-auto px-6 py-4 text-xs text-slate-500 flex flex-wrap justify-between gap-2">
          <span>Tool-53 · Internal use · Security Controls Assessment</span>
          <span>AI-assisted analysis · Results require human validation</span>
        </div>
      </footer>
    </div>
  );
}
