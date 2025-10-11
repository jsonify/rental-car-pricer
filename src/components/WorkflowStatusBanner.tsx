import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Loader2, CheckCircle2, XCircle, ExternalLink } from 'lucide-react'
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import type { WorkflowStatus } from '@/hooks/useWorkflowStatus'

interface WorkflowStatusBannerProps {
  status: WorkflowStatus
  onDismiss?: () => void
}

export function WorkflowStatusBanner({ status, onDismiss }: WorkflowStatusBannerProps) {
  if (!status.runId) return null

  const getStatusIcon = () => {
    if (status.error) {
      return <XCircle className="h-4 w-4 text-destructive" />
    }

    if (status.status === 'completed') {
      if (status.conclusion === 'success') {
        return <CheckCircle2 className="h-4 w-4 text-green-600" />
      } else if (status.conclusion === 'failure') {
        return <XCircle className="h-4 w-4 text-destructive" />
      }
      return <CheckCircle2 className="h-4 w-4" />
    }

    return <Loader2 className="h-4 w-4 animate-spin" />
  }

  const getStatusText = () => {
    if (status.error) {
      return `Error: ${status.error}`
    }

    if (status.status === 'queued') {
      return 'Workflow queued...'
    }

    if (status.status === 'in_progress') {
      if (status.currentStep) {
        // Clean up step names for better readability
        const cleanStep = status.currentStep
          .replace(/^(Run|Set up|Post|Checkout) /, '')
          .replace(/\s+/g, ' ')
          .trim()
        return cleanStep
      }
      return 'Checking prices...'
    }

    if (status.status === 'completed') {
      if (status.conclusion === 'success') {
        return 'Price check completed successfully!'
      } else if (status.conclusion === 'failure') {
        return 'Workflow failed. Check GitHub Actions for details.'
      } else if (status.conclusion === 'cancelled') {
        return 'Workflow was cancelled.'
      }
      return 'Workflow completed.'
    }

    return 'Unknown status'
  }

  const getVariant = () => {
    if (status.error || status.conclusion === 'failure') {
      return 'destructive'
    }
    return 'default'
  }

  const showDismissButton = status.status === 'completed' || !!status.error

  const showProgress = status.status === 'in_progress' && status.progress !== undefined

  return (
    <Alert variant={getVariant()}>
      <div className="flex items-start gap-2">
        <div className="flex-shrink-0 mt-0.5">
          {getStatusIcon()}
        </div>
        <div className="flex-1 min-w-0">
          <AlertTitle>Workflow Status</AlertTitle>
          <AlertDescription className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span>{getStatusText()}</span>
              {showProgress && (
                <span className="text-xs text-muted-foreground">
                  ({status.progress}%)
                </span>
              )}
              {status.url && (
                <a
                  href={status.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm underline hover:no-underline"
                >
                  View details
                  <ExternalLink className="h-3 w-3" />
                </a>
              )}
            </div>
            {showProgress && (
              <Progress value={status.progress} className="h-2" />
            )}
          </AlertDescription>
        </div>
        {showDismissButton && onDismiss && (
          <Button variant="ghost" size="sm" onClick={onDismiss} className="flex-shrink-0">
            Dismiss
          </Button>
        )}
      </div>
    </Alert>
  )
}
