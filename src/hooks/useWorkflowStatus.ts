import { useState, useEffect, useCallback } from 'react'
import { getWorkflowRun, type WorkflowRun } from '@/lib/github'

export interface WorkflowStatus {
  runId: number | null
  status: 'queued' | 'in_progress' | 'completed' | null
  conclusion: 'success' | 'failure' | 'cancelled' | 'skipped' | null
  url: string | null
  error: string | null
}

/**
 * Hook to track workflow status with automatic polling
 */
export function useWorkflowStatus() {
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus>({
    runId: null,
    status: null,
    conclusion: null,
    url: null,
    error: null,
  })

  const [isPolling, setIsPolling] = useState(false)

  const startTracking = useCallback((runId: number) => {
    setWorkflowStatus({
      runId,
      status: 'queued',
      conclusion: null,
      url: null,
      error: null,
    })
    setIsPolling(true)
  }, [])

  const stopTracking = useCallback(() => {
    setIsPolling(false)
  }, [])

  const reset = useCallback(() => {
    setWorkflowStatus({
      runId: null,
      status: null,
      conclusion: null,
      url: null,
      error: null,
    })
    setIsPolling(false)
  }, [])

  useEffect(() => {
    if (!isPolling || !workflowStatus.runId) return

    let cancelled = false

    const pollStatus = async () => {
      try {
        const run: WorkflowRun = await getWorkflowRun(workflowStatus.runId!)

        if (cancelled) return

        setWorkflowStatus({
          runId: run.id,
          status: run.status,
          conclusion: run.conclusion,
          url: run.html_url,
          error: null,
        })

        // Stop polling if workflow is complete
        if (run.status === 'completed') {
          setIsPolling(false)
        }
      } catch (error) {
        if (cancelled) return

        console.error('Error polling workflow status:', error)
        setWorkflowStatus(prev => ({
          ...prev,
          error: error instanceof Error ? error.message : 'Failed to fetch status',
        }))
        setIsPolling(false)
      }
    }

    // Poll immediately
    pollStatus()

    // Then poll every 5 seconds
    const interval = setInterval(pollStatus, 5000)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [isPolling, workflowStatus.runId])

  return {
    workflowStatus,
    startTracking,
    stopTracking,
    reset,
    isTracking: isPolling,
  }
}
