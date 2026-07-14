"use client";

// プリセットプロンプト実行画面。
// ①テンプレート一覧を取得 → ②選ぶと variables から入力フォームを動的生成
// → ③実行で POST /api/generate → ④組み立てられたプロンプトと生成結果を表示。
// 「利用者はプロンプトを書かない」= チャット欄が存在しないのがこの UI の要点。

import { useEffect, useMemo, useState } from "react";
import { API_BASE, GenerateResponse, Template } from "../lib/types";

export default function Home() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/templates`)
      .then((res) => res.json())
      .then(setTemplates)
      .catch(() => setError("バックエンド (localhost:8000) に接続できません"));
  }, []);

  const selected = useMemo(
    () => templates.find((t) => t.id === selectedId) ?? null,
    [templates, selectedId],
  );

  function selectTemplate(t: Template) {
    setSelectedId(t.id);
    setInputs({}); // テンプレートを切り替えたら入力はリセット
    setResult(null);
    setError(null);
  }

  async function run() {
    if (!selected) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ template_id: selected.id, variables: inputs }),
      });
      if (!res.ok) {
        const body = await res.json();
        throw new Error(body.detail ?? `HTTP ${res.status}`);
      }
      setResult((await res.json()) as GenerateResponse);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }

  const allFilled = selected?.variables.every((v) => (inputs[v.name] ?? "").trim() !== "") ?? false;

  return (
    <main>
      <h1>Preset Prompt Studio (demo)</h1>
      <p className="lede">
        プリセットを選び、空欄を埋めて実行する——利用者がプロンプトを書かない非チャット形式のデモ
      </p>

      <div className="template-list">
        {templates.map((t) => (
          <button
            key={t.id}
            className={`template-card ${t.id === selectedId ? "selected" : ""}`}
            onClick={() => selectTemplate(t)}
          >
            <h2>{t.title}</h2>
            <p>{t.description}</p>
          </button>
        ))}
      </div>

      {selected && (
        <>
          <div className="var-form">
            {selected.variables.map((v) => (
              <label key={v.name}>
                {v.label}
                {v.name === "received_email" || v.name === "meeting_notes" ? (
                  <textarea
                    rows={4}
                    placeholder={v.example}
                    value={inputs[v.name] ?? ""}
                    onChange={(e) => setInputs({ ...inputs, [v.name]: e.target.value })}
                  />
                ) : (
                  <input
                    placeholder={v.example}
                    value={inputs[v.name] ?? ""}
                    onChange={(e) => setInputs({ ...inputs, [v.name]: e.target.value })}
                  />
                )}
              </label>
            ))}
          </div>
          <button className="run-button" onClick={run} disabled={!allFilled || loading}>
            {loading ? "生成中…" : "実行"}
          </button>
        </>
      )}

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <section>
            <h3>組み立てられたプロンプト</h3>
            <pre>{result.filled_prompt}</pre>
          </section>
          <section>
            <h3>
              生成結果 <span className="provider-badge">provider: {result.provider}</span>
            </h3>
            <pre>{result.output}</pre>
          </section>
        </div>
      )}
    </main>
  );
}
