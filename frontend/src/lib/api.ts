export type RunDealRequest = {
  customer_name: string
  customer_input_raw: string
  industry: string
  company_size: string
  geo: string
  currency: string
  thread_id?: string
}

export async function runDeal(payload: RunDealRequest) {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL

  if (!baseUrl) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not set")
  }

  const response = await fetch(`${baseUrl}/run-deal`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(`API request failed: ${response.status} ${text}`)
  }

  return response.json()
}
