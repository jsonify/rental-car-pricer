/**
 * GitHub API client for triggering workflows
 */

const GITHUB_TOKEN = import.meta.env.VITE_GITHUB_TOKEN
const GITHUB_OWNER = import.meta.env.VITE_GITHUB_OWNER
const GITHUB_REPO = import.meta.env.VITE_GITHUB_REPO

export interface WorkflowDispatchInputs {
  action: 'add-booking' | 'update-holding-prices' | 'delete-booking' | 'check-prices'
  new_booking_location?: string
  new_booking_pickup_date?: string
  new_booking_dropoff_date?: string
  new_booking_category?: string
  new_booking_holding_price?: string
  booking_updates_json?: string
  booking_to_delete?: string
}

/**
 * Trigger a GitHub Actions workflow
 */
export async function triggerWorkflow(inputs: WorkflowDispatchInputs): Promise<void> {
  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
    throw new Error('GitHub configuration is missing. Please set VITE_GITHUB_TOKEN, VITE_GITHUB_OWNER, and VITE_GITHUB_REPO')
  }

  const response = await fetch(
    `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/price-checker.yaml/dispatches`,
    {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${GITHUB_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ref: 'main',
        inputs,
      }),
    }
  )

  if (!response.ok) {
    const error = await response.text()
    throw new Error(`Failed to trigger workflow: ${response.status} ${error}`)
  }
}
