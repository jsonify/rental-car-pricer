# TypeScript/React Styleguide

## Components

- One component per file, filename matches export name (PascalCase)
- Prefer functional components; no class components
- Export components as named exports, not default exports
- Co-locate component-specific types in the same file unless shared

```tsx
// ✅ Good
export function BookingCard({ booking }: { booking: Booking }) { ... }

// ❌ Avoid
export default function({ booking }) { ... }
```

## TypeScript

- Always type function parameters and return values explicitly when not obvious
- Use interfaces for object shapes shared across files; put them in `src/lib/types.ts`
- Prefer `type` for unions and aliases, `interface` for object contracts
- No `any` — use `unknown` if the type is genuinely unknown, then narrow it
- Use the `@/` alias for all imports from `src/`

```ts
// ✅ Good
import { Booking } from '@/lib/types'

// ❌ Avoid
import { Booking } from '../../lib/types'
```

## Hooks

- Custom hooks go in `src/hooks/`, named `use<Name>.ts`
- Hooks own data fetching and side effects; components receive data as props or via hooks
- Keep hook return shapes stable — avoid returning different shapes conditionally

## State Management

- Prefer `useState` + `useEffect` for local component state
- Use React Context (`src/contexts/`) only for truly global state (e.g., environment toggle)
- Do not use global state for data that can be derived from fetched data

## File Structure

```
src/
  components/    # UI components (pure, no direct Supabase calls)
  contexts/      # React Context providers
  hooks/         # Custom hooks (data fetching, side effects)
  lib/           # Utilities, Supabase client, types, mock data
```

## Styling

- Use Tailwind utility classes directly on elements
- No inline `style={{}}` unless for dynamic values that can't be expressed as Tailwind
- Compose variants using `clsx` / `cn()` from `@/lib/utils`
- Responsive: mobile-first (`sm:`, `md:`, `lg:`)

## Error Handling

- Handle loading and error states explicitly in every data-fetching hook
- Surface errors to the user in the UI, not just console.error
- Never swallow errors silently

## Imports Order

1. React and React ecosystem (`react`, `react-dom`)
2. Third-party libraries
3. Internal `@/` imports (types, lib, hooks, components)
4. Relative imports

Separate each group with a blank line.
