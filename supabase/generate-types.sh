#!/bin/bash
# Generate TypeScript types from Supabase schema
# Install the Supabase CLI first: https://supabase.com/docs/guides/cli

# Make sure you're logged in: npx supabase login
# Then run this script: ./supabase/generate-types.sh

npx supabase gen types typescript \
  --project-id wjhrxogbluuxbcbxruqu \
  --schema public \
  > src/lib/database.types.ts

echo "✅ Types generated at src/lib/database.types.ts"
echo "You can now import these types in your code:"
echo "import { Database } from '@/lib/database.types'"
