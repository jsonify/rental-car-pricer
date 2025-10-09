#!/bin/bash

# Load environment variables from .env
source .env

echo "Please go to the Supabase SQL Editor to run the migration:"
echo ""
echo "URL: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/sql/new"
echo ""
echo "Copy and paste the contents of supabase/schema_update.sql"
echo ""
cat supabase/schema_update.sql
