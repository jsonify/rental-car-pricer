// src/lib/github-actions.ts
import { Octokit } from '@octokit/rest'

const octokit = new Octokit({
  auth: import.meta.env.VITE_GITHUB_TOKEN
})

// GitHub repository details
const owner = import.meta.env.VITE_GITHUB_OWNER
const repo = import.meta.env.VITE_GITHUB_REPO

export const githubActions = {
  triggerWorkflow: async (action: string, inputs: Record<string, string> = {}) => {
    try {
      const response = await octokit.actions.createWorkflowDispatch({
        owner,
        repo,
        workflow_id: 'price-checker.yaml',
        ref: 'main',
        inputs: {
          action,
          ...inputs
        }
      })

      return { success: true }
    } catch (error) {
      console.error('Error triggering workflow:', error)
      throw new Error('Failed to trigger GitHub workflow')
    }
  },

  getWorkflowStatus: async () => {
    try {
      const { data } = await octokit.actions.listWorkflowRuns({
        owner,
        repo,
        workflow_id: 'price-checker.yaml',
        per_page: 1
      })

      return data.workflow_runs[0]?.status || 'unknown'
    } catch (error) {
      console.error('Error getting workflow status:', error)
      return 'unknown'
    }
  }
}