"use client"

import { useState } from "react"
import { runDeal } from "@/lib/api"

export default function HomePage() {
  const [form, setForm] = useState({
    customer_name: "",
    customer_input_raw: "",
    industry: "",
    company_size: "",
    geo: "",
    currency: "USD",
    thread_id: "demo-thread-1",
  })

  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState("")

  const updateField = (key: string, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")
    setResult(null)

    try {
      const data = await runDeal(form)
      setResult(data)
    } catch (err: any) {
      setError(err.message || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main style={{ padding: 24, fontFamily: "Arial, sans-serif", maxWidth: 1000, margin: "0 auto" }}>
      <h1>AI Solutions Agency OS</h1>
      <p>Lead intake and deal orchestration</p>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12, marginTop: 20 }}>
        <input
          placeholder="Customer name"
          value={form.customer_name}
          onChange={(e) => updateField("customer_name", e.target.value)}
          required
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <textarea
          placeholder="Describe the customer need"
          value={form.customer_input_raw}
          onChange={(e) => updateField("customer_input_raw", e.target.value)}
          required
          rows={6}
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <input
          placeholder="Industry"
          value={form.industry}
          onChange={(e) => updateField("industry", e.target.value)}
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <input
          placeholder="Company size"
          value={form.company_size}
          onChange={(e) => updateField("company_size", e.target.value)}
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <input
          placeholder="Geography"
          value={form.geo}
          onChange={(e) => updateField("geo", e.target.value)}
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <input
          placeholder="Currency"
          value={form.currency}
          onChange={(e) => updateField("currency", e.target.value)}
          style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: 12,
            background: "#111",
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
          }}
        >
          {loading ? "Running..." : "Run deal"}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: 20, padding: 12, border: "1px solid red", color: "red", borderRadius: 6 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 24, display: "grid", gap: 20 }}>
          <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
            <h2>Current Stage</h2>
            <pre style={{ whiteSpace: "pre-wrap" }}>{JSON.stringify(result.current_stage, null, 2)}</pre>
          </section>

          <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
            <h2>Final Summary</h2>
            <pre style={{ whiteSpace: "pre-wrap", overflowX: "auto" }}>
              {JSON.stringify(result.final_summary, null, 2)}
            </pre>
          </section>

          <section style={{ padding: 16, border: "1px solid #ddd", borderRadius: 8 }}>
            <h2>Full Response</h2>
            <pre style={{ whiteSpace: "pre-wrap", overflowX: "auto" }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </section>
        </div>
      )}
    </main>
  )
}
