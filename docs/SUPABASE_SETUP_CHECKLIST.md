# 🎯 Supabase Setup Checklist

Quick setup guide for your new Supabase project: `wjhrxogbluuxbcbxruqu`

## ☑️ Step-by-Step

### 1. Run the Schema
- [ ] Go to SQL Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/sql/new
- [ ] Copy contents from `supabase/schema.sql`
- [ ] Paste and click "Run"
- [ ] Verify 3 tables created: `bookings`, `price_histories`, `holding_price_histories`

### 2. Get API Keys
- [ ] Go to Settings → API: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/settings/api
- [ ] Copy `URL`: https://wjhrxogbluuxbcbxruqu.supabase.co
- [ ] Copy `anon public` key (for frontend)
- [ ] Copy `service_role` key (for Python)

### 3. Update Frontend Environment
- [ ] Create/update `.env.local` in project root:
```bash
VITE_SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
VITE_SUPABASE_ANON_KEY=<paste-anon-key-here>
```

### 4. Update Python Environment
- [ ] Update `.env` file (keep existing Chrome/email settings):
```bash
SUPABASE_URL=https://wjhrxogbluuxbcbxruqu.supabase.co
SUPABASE_SERVICE_KEY=<paste-service-role-key-here>
```

### 5. Test Frontend
- [ ] Run `npm run dev`
- [ ] Open http://localhost:5173
- [ ] Toggle test mode OFF (to use real Supabase)
- [ ] Verify you see 2 sample bookings (KOA and HNL)
- [ ] Try adding a booking via Admin Controls

### 6. Test Python
- [ ] Run: `python3 -c "from supabase_client import get_supabase_client; print('✅ Connected')"`
- [ ] Or run full scraper: `python3 main.py -i`

### 7. Optional - Clean Sample Data
- [ ] Go to Table Editor: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu/editor
- [ ] Delete KOA and HNL sample bookings
- [ ] Add your real bookings via UI or Python

## 🎉 You're Done!

Your rental car price tracker is now connected to the new Supabase project.

## 📚 Additional Resources

- Full setup guide: `supabase/SETUP.md`
- Schema file: `supabase/schema.sql`
- Migration guide: `supabase/migrate-old-data.md` (if you need old data)
- Supabase Dashboard: https://supabase.com/dashboard/project/wjhrxogbluuxbcbxruqu

## 🔧 Troubleshooting

**Frontend shows "Failed to fetch":**
- Restart dev server after changing `.env.local`
- Check VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY are correct

**Python can't connect:**
- Verify `.env` has SUPABASE_URL and SUPABASE_SERVICE_KEY
- Make sure you're using `service_role` key, not `anon` key

**No data showing:**
- Toggle test environment switch OFF
- Check Table Editor to see if data exists in Supabase
- Open browser console for errors
