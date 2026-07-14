# Phase 3: Frontend - Quick Start Guide

## ✅ What's Running

### Backend (Port 8000)
- ✅ FastAPI server with OAuth endpoints
- ✅ Dashboard metrics APIs
- ✅ Chat/Q&A endpoints
- ✅ Mock data generator

### Frontend (Port 3000)
- ✅ Next.js development server
- ✅ Tailwind CSS styling
- ✅ Recharts for visualizations
- ✅ Zustand state management

---

## 🌐 Access Points

### Frontend Dashboard
```
http://localhost:3000
```

Available pages:
- **Dashboard** (`/home`) - Key metrics and charts
- **Chat** (`/chat`) - Natural language Q&A with Claude
- **Reports** (`/reports`) - Generate custom business reports
- **Settings** (`/settings`) - System status and configuration

### Backend API Documentation
```
http://localhost:8000/docs
```

Available endpoints:
- `GET /api/dashboard/metrics` - Key metrics (revenue, invoices, customers, avg transaction)
- `GET /api/dashboard/revenue-trend` - Revenue over time
- `GET /api/dashboard/top-products` - Top selling products
- `GET /api/dashboard/summary` - Complete dashboard snapshot
- `POST /api/query/chat` - Natural language business questions
- `POST /api/query/insights` - Auto-generated business insights
- `POST /api/query/report` - Formatted business reports

### OAuth/Authentication
- `GET /api/auth/zoho/login` - Get Zoho Books OAuth login URL
- `GET /api/auth/zoho/callback` - OAuth callback handler
- `GET /api/auth/zoho/status` - Check authentication status

---

## 🧪 Testing Workflow

### 1. Test Dashboard
1. Open http://localhost:3000
2. Should redirect to `/home` dashboard
3. You'll see 4 metric cards with mock data
4. Below: Revenue Trend chart and Top Products chart
5. Try clicking period buttons (today, week, month, etc.)

### 2. Test Chat
1. Go to http://localhost:3000/chat
2. Try questions like:
   - "What was my total revenue last month?"
   - "Which products are selling best?"
   - "What's my customer count?"
3. Watch the chat populate with Claude AI responses

### 3. Test Reports
1. Go to http://localhost:3000/reports
2. Modify report title if desired
3. Select time period
4. Click "Generate Report"
5. View formatted report with insights

### 4. Test Settings
1. Go to http://localhost:3000/settings
2. View system status
3. Check API configuration

---

## 🔧 Development Tips

### API Integration
The frontend uses a centralized API client at `lib/api/client.ts`:
```typescript
import { apiClient } from '@/lib/api/client';

// Call any backend endpoint
const metrics = await apiClient.getMetrics('month');
const chat = await apiClient.sendChat({ message: 'Your question' });
```

### State Management
Zustand store at `lib/store/dashboardStore.ts`:
```typescript
import { useDashboardStore } from '@/lib/store/dashboardStore';

const { metrics, setMetrics, isLoading } = useDashboardStore();
```

### Hooks
Reusable data hooks at `hooks/useDashboard.ts`:
```typescript
const { metrics, revenueTrend, refresh } = useDashboard();
const { messages, sendMessage } = useChat();
```

### Adding New Components
1. Create in `components/` folder
2. Mark with `'use client'` at top
3. Use TypeScript types from `lib/types/`
4. Import from `lib/api/client` for API calls

---

## 📦 Installed Dependencies

**Frontend:**
- `next` - React framework
- `react-dom` - React DOM
- `recharts` - Charts library
- `axios` - HTTP client
- `zustand` - State management
- `date-fns` - Date utilities
- `react-markdown` - Markdown rendering
- `tailwindcss` - Styling

**Backend:**
(Already installed - see backend/requirements.txt)

---

## 🚀 Next Steps (Phase 3 Continuation)

1. **Polish Dashboard**
   - Add loading states ✓ (done)
   - Add error boundaries
   - Add refresh button ✓ (done)
   - Add date range picker

2. **Chat Improvements**
   - Conversation history
   - Clear conversation button
   - Copy message to clipboard
   - Share conversation

3. **Reports Enhancement**
   - PDF export
   - Email report
   - Schedule reports
   - Custom metrics

4. **Authentication**
   - User login/logout
   - Session management
   - API key management

5. **Data Sources**
   - QuickBooks integration
   - Stripe integration
   - Custom database connector

---

## ⚡ Common Issues & Fixes

### "Failed to connect to backend"
- Check backend is running: `http://localhost:8000/health`
- Check CORS is enabled in backend
- Verify `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`

### Charts not showing
- Recharts requires width/height - check ResponsiveContainer
- Mock data should auto-populate on first load

### Chat not responding
- Check ANTHROPIC_API_KEY in backend `.env`
- View backend logs for Claude API errors

### Type errors in frontend
- Run `npm run build` to check TypeScript
- Check `lib/types/index.ts` for API response shapes

---

## 📝 File Structure

```
frontend/
├── app/
│   ├── (dashboard)/
│   │   └── home/page.tsx      # Main dashboard page
│   ├── chat/page.tsx          # Chat interface
│   ├── reports/page.tsx       # Report generation
│   ├── settings/page.tsx      # System settings
│   ├── layout.tsx             # Root layout with Header
│   └── page.tsx               # Root redirect to /home
├── components/
│   ├── dashboard/             # Dashboard-specific
│   ├── charts/                # Recharts components
│   ├── chat/                  # Chat UI components
│   └── common/                # Header, Skeletons, etc.
├── lib/
│   ├── api/client.ts          # API client
│   ├── store/                 # Zustand stores
│   └── types/index.ts         # TypeScript types
├── hooks/
│   └── useDashboard.ts        # Data hooks
└── utils/
    └── formatters.ts          # Number/date formatting
```

---

## 🎯 Success Criteria

- [ ] Dashboard loads with 4 metric cards
- [ ] Charts render with mock data
- [ ] Period selector works (today/week/month/quarter/year)
- [ ] Chat interface responds to questions
- [ ] Report generation works
- [ ] Settings page shows system status
- [ ] No console errors
- [ ] API responses match TypeScript types

---

## 📞 Need Help?

1. Check backend logs: Look at the terminal running the backend
2. Check frontend logs: Open browser DevTools (F12)
3. Check API: Visit http://localhost:8000/docs to test endpoints
4. Test connectivity: `curl http://localhost:8000/health`

Enjoy! 🚀
