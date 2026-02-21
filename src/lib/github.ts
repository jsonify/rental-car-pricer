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

export interface WorkflowRun {
  id: number
  status: 'queued' | 'in_progress' | 'completed'
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null
  html_url: string
  created_at: string
  updated_at: string
}

export interface WorkflowStep {
  name: string
  status: 'queued' | 'in_progress' | 'completed'
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null
  number: number
  started_at: string | null
  completed_at: string | null
}

export interface WorkflowJob {
  id: number
  name: string
  status: 'queued' | 'in_progress' | 'completed'
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null
  started_at: string
  completed_at: string | null
  steps: WorkflowStep[]
}

export interface WorkflowRunDetails extends WorkflowRun {
  jobs: WorkflowJob[]
  currentStep?: string
  progress?: number
}

/**
 * Trigger a GitHub Actions workflow and return the run ID
 */
export async function triggerWorkflow(inputs: WorkflowDispatchInputs): Promise<number> {
  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
    const missing = []
    if (!GITHUB_TOKEN) missing.push('VITE_GITHUB_TOKEN')
    if (!GITHUB_OWNER) missing.push('VITE_GITHUB_OWNER')
    if (!GITHUB_REPO) missing.push('VITE_GITHUB_REPO')
    throw new Error(`GitHub configuration is missing: ${missing.join(', ')}`)
  }

  console.log('Triggering workflow with inputs:', inputs)

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/price-checker.yaml/dispatches`

  const response = await fetch(url, {
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
  })

  console.log('Workflow dispatch response:', response.status, response.statusText)

  if (!response.ok) {
    const error = await response.text()
    console.error('Workflow dispatch failed:', error)
    throw new Error(`Failed to trigger workflow: ${response.status} ${response.statusText} - ${error}`)
  }

  console.log('Workflow triggered successfully!')

  // Get the latest workflow run ID (GitHub doesn't return it in the dispatch response)
  // We need to poll the runs list to find the one we just created
  await new Promise(resolve => setTimeout(resolve, 1000)) // Wait 1s for GitHub to register the run

  const runsUrl = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/price-checker.yaml/runs?per_page=1`
  const runsResponse = await fetch(runsUrl, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `Bearer ${GITHUB_TOKEN}`,
    },
  })

  if (!runsResponse.ok) {
    throw new Error('Failed to fetch workflow run ID')
  }

  const runsData = await runsResponse.json()
  if (!runsData.workflow_runs || runsData.workflow_runs.length === 0) {
    throw new Error('No workflow runs found')
  }

  return runsData.workflow_runs[0].id
}

/**
 * Get the status of a specific workflow run
 */
export async function getWorkflowRun(runId: number): Promise<WorkflowRun> {
  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
    throw new Error('GitHub configuration is missing')
  }

  const url = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}`

  const response = await fetch(url, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `Bearer ${GITHUB_TOKEN}`,
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to fetch workflow run: ${response.statusText}`)
  }

  const data = await response.json()
  return {
    id: data.id,
    status: data.status,
    conclusion: data.conclusion,
    html_url: data.html_url,
    created_at: data.created_at,
    updated_at: data.updated_at,
  }
}

/**
 * Get detailed status including jobs and steps for a workflow run
 */
export async function getWorkflowRunDetails(runId: number): Promise<WorkflowRunDetails> {
  if (!GITHUB_TOKEN || !GITHUB_OWNER || !GITHUB_REPO) {
    throw new Error('GitHub configuration is missing')
  }

  // Fetch the run metadata
  const run = await getWorkflowRun(runId)

  // Fetch jobs for this run
  const jobsUrl = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}/jobs`
  const jobsResponse = await fetch(jobsUrl, {
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `Bearer ${GITHUB_TOKEN}`,
    },
  })

  if (!jobsResponse.ok) {
    throw new Error(`Failed to fetch workflow jobs: ${jobsResponse.statusText}`)
  }

  const jobsData = await jobsResponse.json()
  const jobs: WorkflowJob[] = jobsData.jobs.map((job: any) => ({
    id: job.id,
    name: job.name,
    status: job.status,
    conclusion: job.conclusion,
    started_at: job.started_at,
    completed_at: job.completed_at,
    steps: (job.steps || []).map((step: any) => ({
      name: step.name,
      status: step.status,
      conclusion: step.conclusion,
      number: step.number,
      started_at: step.started_at,
      completed_at: step.completed_at,
    })),
  }))

  // Calculate current step and progress
  let currentStep: string | undefined
  let progress = 0

  if (jobs.length > 0) {
    const activeJob = jobs.find(job => job.status === 'in_progress') || jobs[jobs.length - 1]
    const completedSteps = activeJob.steps.filter(step => step.status === 'completed')

    if (activeJob.status === 'in_progress') {
      const inProgressStep = activeJob.steps.find(step => step.status === 'in_progress')
      if (inProgressStep) {
        currentStep = inProgressStep.name
      }
    }

    // Calculate progress (percentage of completed steps)
    if (activeJob.steps.length > 0) {
      progress = Math.round((completedSteps.length / activeJob.steps.length) * 100)
    }
  }

  return {
    ...run,
    jobs,
    currentStep,
    progress,
  }
}
