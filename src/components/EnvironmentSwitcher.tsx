// src/components/EnvironmentSwitcher.tsx
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useEnvironment } from '@/contexts/EnvironmentContext'

export function EnvironmentSwitcher() {
  const { isTestEnvironment, setIsTestEnvironment } = useEnvironment()

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-sm font-medium">Environment Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          <Label htmlFor="test-mode" className="font-normal">
            Test Mode {isTestEnvironment ? 'Enabled' : 'Disabled'}
          </Label>
          <Switch
            id="test-mode"
            checked={isTestEnvironment}
            onCheckedChange={setIsTestEnvironment}
          />
        </div>
        <p className="text-sm text-gray-500 mt-2">
          {isTestEnvironment 
            ? "Using mock data for testing" 
            : "Using production Supabase data"}
        </p>
      </CardContent>
    </Card>
  )
}