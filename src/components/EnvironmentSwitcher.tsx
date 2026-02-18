// src/components/EnvironmentSwitcher.tsx
import { Switch } from '@/components/ui/switch'
import { useEnvironment } from '@/contexts/EnvironmentContext'

export function EnvironmentSwitcher() {
  const { isTestEnvironment, setIsTestEnvironment } = useEnvironment()

  return (
    <div className="flex items-center justify-between py-2 px-3 rounded-lg bg-gray-900 border border-gray-800 text-xs text-gray-500">
      <span>
        {isTestEnvironment ? (
          <span className="text-yellow-500 font-medium">TEST MODE</span>
        ) : (
          <span className="text-green-500 font-medium">PRODUCTION</span>
        )}
        <span className="ml-2">{isTestEnvironment ? 'using mock data' : 'using live Supabase'}</span>
      </span>
      <Switch
        id="test-mode"
        checked={isTestEnvironment}
        onCheckedChange={setIsTestEnvironment}
      />
    </div>
  )
}
