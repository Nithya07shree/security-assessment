const PRIORITY_STYLES = {
  high: "bg-red-50 text-red-800 border-red-200",
  medium: "bg-amber-50 text-amber-800 border-amber-200",
  low: "bg-slate-100 text-slate-700 border-slate-200",
};

/** Internal / technical fields hidden from assessors */
const HIDDEN_FIELDS = new Set([
  "meta",
  "generated_at",
  "sources",
  "confidence",
]);

function shouldShowField(key, value) {
  if (HIDDEN_FIELDS.has(key)) return false;
  if (value === null || value === undefined) return false;
  if (isObject(value) && Object.keys(value).length === 0) return false;
  return true;
}

function filterEntries(obj) {
  return Object.entries(obj).filter(([key, value]) => shouldShowField(key, value));
}

function filterRow(row) {
  return Object.fromEntries(filterEntries(row));
}

function labelize(key) {
  return key
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function isRowArray(value) {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    value.every((item) => isObject(item))
  );
}

function formatCell(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return String(value);
  if (Array.isArray(value)) return value.join(", ");
  if (isObject(value)) return JSON.stringify(value);
  return String(value);
}

function PriorityBadge({ value }) {
  const level = String(value ?? "").toLowerCase();
  const style = PRIORITY_STYLES[level] ?? PRIORITY_STYLES.low;
  return (
    <span
      className={`inline-flex px-2 py-0.5 rounded text-xs font-medium border ${style}`}
    >
      {formatCell(value)}
    </span>
  );
}

function ProseBlock({ children }) {
  return (
    <div className="px-4 py-4">
      <p className="text-sm text-slate-800 leading-relaxed whitespace-pre-wrap">
        {children}
      </p>
    </div>
  );
}

function DataTable({ rows, columns }) {
  const filteredRows = rows.map(filterRow);
  const cols =
    columns ??
    Array.from(
      filteredRows.reduce((set, row) => {
        Object.keys(row).forEach((k) => {
          if (shouldShowField(k, row[k])) set.add(k);
        });
        return set;
      }, new Set())
    );

  if (!filteredRows.length || !cols.length) {
    return (
      <p className="text-sm text-slate-500 px-4 py-3">No records returned.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-slate-100 border-b border-slate-200">
            {cols.map((col) => (
              <th
                key={col}
                className="text-left px-4 py-2.5 font-semibold text-slate-700 whitespace-nowrap"
              >
                {labelize(col)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {filteredRows.map((row, i) => (
            <tr
              key={i}
              className={`border-b border-slate-100 ${
                i % 2 === 0 ? "bg-white" : "bg-slate-50/60"
              }`}
            >
              {cols.map((col) => (
                <td
                  key={col}
                  className="px-4 py-3 text-slate-700 align-top max-w-md"
                >
                  {col === "priority" && row[col] ? (
                    <PriorityBadge value={row[col]} />
                  ) : (
                    <span className="leading-relaxed">{formatCell(row[col])}</span>
                  )}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function KeyValueTable({ entries }) {
  if (!entries.length) {
    return (
      <p className="text-sm text-slate-500 px-4 py-3">No fields returned.</p>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-slate-100 border-b border-slate-200">
            <th className="text-left px-4 py-2.5 font-semibold text-slate-700 w-48">
              Field
            </th>
            <th className="text-left px-4 py-2.5 font-semibold text-slate-700">
              Value
            </th>
          </tr>
        </thead>
        <tbody>
          {entries.map(([key, value], i) => (
            <tr
              key={key}
              className={`border-b border-slate-100 ${
                i % 2 === 0 ? "bg-white" : "bg-slate-50/60"
              }`}
            >
              <td className="px-4 py-3 font-medium text-slate-600 align-top whitespace-nowrap">
                {labelize(key)}
              </td>
              <td className="px-4 py-3 text-slate-800 align-top">
                {key === "priority" ? (
                  <PriorityBadge value={value} />
                ) : isRowArray(value) ? (
                  <NestedTable rows={value} />
                ) : Array.isArray(value) && value.every((v) => typeof v === "string") ? (
                  <ul className="list-disc pl-4 space-y-1">
                    {value.map((item, idx) => (
                      <li key={idx}>{item}</li>
                    ))}
                  </ul>
                ) : (
                  <span className="leading-relaxed whitespace-pre-wrap">
                    {formatCell(value)}
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function NestedTable({ rows }) {
  return (
    <div className="mt-1 rounded border border-slate-200 overflow-hidden">
      <DataTable rows={rows} />
    </div>
  );
}

function ResultSection({ title, children }) {
  return (
    <div className="border-b border-slate-200 last:border-b-0">
      <div className="px-4 py-2 bg-slate-50 border-b border-slate-100">
        <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          {title}
        </h4>
      </div>
      {children}
    </div>
  );
}

function renderPayload(data) {
  if (data === null || data === undefined) {
    return <p className="text-sm text-slate-500 px-4 py-3">Empty response.</p>;
  }

  if (typeof data === "string") {
    return <ProseBlock>{data}</ProseBlock>;
  }

  if (isRowArray(data)) {
    return <DataTable rows={data} />;
  }

  if (Array.isArray(data)) {
    return (
      <KeyValueTable
        entries={data.map((item, i) => [`Item ${i + 1}`, item])}
      />
    );
  }

  if (!isObject(data)) {
    return (
      <div className="px-4 py-3 text-sm text-slate-700">{formatCell(data)}</div>
    );
  }

  const arrayFields = [];
  const scalarFields = [];

  for (const [key, value] of filterEntries(data)) {
    if (isRowArray(value)) {
      arrayFields.push([key, value]);
    } else if (
      Array.isArray(value) &&
      value.length > 0 &&
      typeof value[0] === "string"
    ) {
      arrayFields.push([key, value]);
    } else {
      scalarFields.push([key, value]);
    }
  }

  if (
    scalarFields.length === 1 &&
    typeof scalarFields[0][1] === "string" &&
    arrayFields.length === 0
  ) {
    return <ProseBlock>{scalarFields[0][1]}</ProseBlock>;
  }

  return (
    <>
      {scalarFields.length > 0 && <KeyValueTable entries={scalarFields} />}
      {arrayFields.map(([key, value]) =>
        isRowArray(value) ? (
          <ResultSection key={key} title={labelize(key)}>
            <DataTable rows={value} />
          </ResultSection>
        ) : (
          <ResultSection key={key} title={labelize(key)}>
            <KeyValueTable
              entries={value.map((item, i) => [`${i + 1}`, item])}
            />
          </ResultSection>
        )
      )}
    </>
  );
}

function renderAssessment(data) {
  const sections = [
    { title: "Control description", payload: data.description },
    { title: "Risk classification", payload: data.category },
    { title: "Remediation advisory", payload: data.recommendations },
  ];

  return (
    <div>
      {sections.map(({ title, payload }) => (
        <ResultSection key={title} title={title}>
          {renderPayload(payload)}
        </ResultSection>
      ))}
    </div>
  );
}

export default function ResultViewer({ actionId, data }) {
  const content =
    actionId === "assessment" ? renderAssessment(data) : renderPayload(data);

  return <div className="divide-y divide-slate-200">{content}</div>;
}
