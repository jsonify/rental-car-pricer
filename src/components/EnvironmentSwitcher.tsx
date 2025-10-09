// src/components/EnvironmentSwitcher.tsx
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useEnvironment } from '@/contexts/EnvironmentContext'

export function EnvironmentSwitcher() {
  const { isTestEnvironment, setIsTestEnvironment } = useEnvironment()

  return (
    <Card className={`mb-4 ${isTestEnvironment ? 'border-yellow-500 border-2' : 'border-green-500 border-2'}`}>
      <CardHeader>
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          Environment Settings
          <span className={`text-xs px-2 py-1 rounded ${isTestEnvironment ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
            {isTestEnvironment ? '🧪 TEST MODE' : '🚀 PRODUCTION'}
          </span>
        </CardTitle>
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
            ? "Using mock data stored in localStorage (for testing)"
            : "Using live Supabase database (real data)"}
        </p>
      </CardContent>
    </Card>
  )
}