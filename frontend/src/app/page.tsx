"use client"

import { useState } from "react"
import { runDeal } from "@/lib/api"

type FormState = {
  customer_name: string
  customer_input_raw: string
  industry: string
  company_size: string
  geo: string
  currency: string
  thread_id: string
}

type ValidationErrors = Partial<Record<keyof FormState, string>>

const initialForm: FormState = {
  customer_name: "",
  customer_input_raw: "",
  industry: "",
  company_size: "",
  geo: "",
  currency: "USD",
  thread_id: "demo-thread-1",
}

const sampleForm: FormState = {
  customer_name: "ABC Retail",
  customer_input_raw: "We want AI to improve support and recommendations.",
  industry: "Retail",
  company_size: "Mid-market",
  geo: "UAE",
  currency: "AED",
  thread_id: "demo-thread-1",
}

const industries = ["", "Retail", "Banking", "Government", "Healthcare", "Logistics", "Manufacturing", "Telecommunications", "Education", "Other"]
const companySizes = ["", "Startup", "SME", "Mid-market", "Enterprise", "Public Sector"]
const currencies = ["USD", "AED", "EUR", "GBP", "SAR"]

export default function HomePage() {
  const [form, setForm] = useState<FormState>(initialForm)
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState("")

  const updateField = (key: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
    setValidationErrors((prev) => ({ ...prev, [key]: "" }))
  }

  const resetForm = () => {
    setForm(initialForm)
    setValidationErrors({})
    setError("")
  }

  const loadSampleData = () => {
    setForm(sampleForm)
    setValidationErrors({})
    setError("")
  }

  const validateForm = () => {
    const errors: ValidationErrors = {}

    if (!form.customer_name.trim()) {
      errors.customer_name = "Customer name is required."
    }

    if (!form.customer_input_raw.trim()) {
      errors.customer_input_raw = "Customer need description is required."
    }

    if (!form.industry.trim()) {
      errors.industry = "Please select an industry."
    }

    if (!form.company_size.trim()) {
      errors.company_size = "Please select a company size."
    }

    if (!form.currency.trim()) {
      errors.currency = "Please select a currency."
    }

    return errors
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const errors = validateForm()

    if (Object.keys(errors).length > 0) {
      setValidationErrors(errors)
      setError("Please correct the highlighted fields before submitting.")
      return
    }

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
        <div style={{ display: "grid", gap: 6 }}>
          <input
            placeholder="Customer name"
            value={form.customer_name}
            onChange={(e) => updateField("customer_name", e.target.value)}
            style={{ padding: 10, border: `1px solid ${validationErrors.customer_name ? "#d32f2f" : "#ccc"}`, borderRadius: 6 }}
          />
          {validationErrors.customer_name && <span style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors.customer_name}</span>}
        </div>

        <div style={{ display: "grid", gap: 6 }}>
          <textarea
            placeholder="Describe the customer need"
            value={form.customer_input_raw}
            onChange={(e) => updateField("customer_input_raw", e.target.value)}
            rows={6}
            style={{ padding: 10, border: `1px solid ${validationErrors.customer_input_raw ? "#d32f2f" : "#ccc"}`, borderRadius: 6 }}
          />
          {validationErrors.customer_input_raw && <span style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors.customer_input_raw}</span>}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
          <div style={{ display: "grid", gap: 6 }}>
            <select
              value={form.industry}
              onChange={(e) => updateField("industry", e.target.value)}
              style={{ padding: 10, border: `1px solid ${validationErrors.industry ? "#d32f2f" : "#ccc"}`, borderRadius: 6, background: "white" }}
            >
              {industries.map((industry) => (
                <option key={industry || "placeholder"} value={industry}>
                  {industry || "Select industry"}
                </option>
              ))}
            </select>
            {validationErrors.industry && <span style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors.industry}</span>}
          </div>

          <div style={{ display: "grid", gap: 6 }}>
            <select
              value={form.company_size}
              onChange={(e) => updateField("company_size", e.target.value)}
              style={{ padding: 10, border: `1px solid ${validationErrors.company_size ? "#d32f2f" : "#ccc"}`, borderRadius: 6, background: "white" }}
            >
              {companySizes.map((size) => (
                <option key={size || "placeholder"} value={size}>
                  {size || "Select company size"}
                </option>
              ))}
            </select>
            {validationErrors.company_size && <span style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors.company_size}</span>}
          </div>

          <div style={{ display: "grid", gap: 6 }}>
            <input
              placeholder="Geography"
              value={form.geo}
              onChange={(e) => updateField("geo", e.target.value)}
              style={{ padding: 10, border: "1px solid #ccc", borderRadius: 6 }}
            />
          </div>

          <div style={{ display: "grid", gap: 6 }}>
            <select
              value={form.currency}
              onChange={(e) => updateField("currency", e.target.value)}
              style={{ padding: 10, border: `1px solid ${validationErrors.currency ? "#d32f2f" : "#ccc"}`, borderRadius: 6, background: "white" }}
            >
              {currencies.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
            {validationErrors.currency && <span style={{ color: "#d32f2f", fontSize: 13 }}>{validationErrors.currency}</span>}
          </div>
        </div>

        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
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

          <button
            type="button"
            onClick={loadSampleData}
            disabled={loading}
            style={{
              padding: 12,
              background: "#f1f3f5",
              color: "#111",
              border: "1px solid #ccc",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            Load sample data
          </button>

          <button
            type="button"
            onClick={resetForm}
            disabled={loading}
            style={{
              padding: 12,
              background: "white",
              color: "#111",
              border: "1px solid #ccc",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            Reset form
          </button>
        </div>
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
