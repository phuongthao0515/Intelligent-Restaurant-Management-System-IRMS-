# KDS Test Data Reset Guide

When you test the KDS UI and mark all dishes as "Ready", they disappear from the display. Use one of these methods to reset the test data:

## Option 1: Quick Reset (Recommended) ⚡

**Node.js (cross-platform):**
```bash
node reset-kds-data.js
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/v1/kds/reset
```

This clears the data **without restarting** the servers. Just refresh your browser!

## Option 2: Full Restart

If you need to restart everything:

**Windows:**
```bash
# Kill processes and restart (requires bash)
./reset-demo.sh
```

**Manual restart:**
```bash
# Kill backend
pkill -f uvicorn

# Restart backend from project root
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, restart frontend
cd frontend
npm run dev
```

## What Gets Reset

✅ All 4 test orders
✅ All order items (back to QUEUED status)  
✅ All 5 kitchen stations
✅ All 12 menu items
✅ All event history

The timer will restart from each item's prep_time_min.

## API Endpoint

**POST** `http://localhost:8000/api/v1/kds/reset`

Response:
```json
{
  "message": "✅ KDS data reset to initial state",
  "orders": 4,
  "items": 12
}
```
