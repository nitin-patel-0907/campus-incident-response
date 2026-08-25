# Campus Incident Response System - Port 8082 Setup

## 🚀 Quick Start on Port 8082

Everything is now configured to run on **https://localhost:8082** with comprehensive analytics and demo data.

### Option 1: One-Click Start (Recommended)

```bash
python start_demo_8082.py
```

This will:
- Generate demo data if not present
- Build the React frontend
- Start the unified server on port 8082
- Serve both API and frontend from the same port

### Option 2: Manual Setup

1. **Generate Demo Data** (if not done already):
   ```bash
   python generate_demo_data.py
   python add_recent_trends.py
   python enhance_demo_patterns.py
   ```

2. **Build Frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Start Server**:
   ```bash
   python start_unified_server_8082.py
   ```

## 📊 What You'll Get

### Analytics Dashboard Features
- **Real-time Performance Metrics**: Overall quality score with trends
- **Interactive Visualizations**: Radar charts, pie charts, bar charts
- **Incident Analysis**: 100+ realistic incidents with patterns
- **Temporal Patterns**: Friday security spikes, Monday medical incidents
- **AI Insights**: Generated lessons and recommendations
- **Policy Compliance**: Real-time monitoring

### Demo Data Highlights
- **100+ Incidents** across 5 categories (Security, Medical, Harassment, Maintenance, Theft)
- **Realistic Patterns**: 
  - Friday evening security incidents (party-related)
  - Monday morning medical incidents (weekend recovery)
  - Exam period harassment spikes
  - Lunch hour theft clustering
- **Performance Metrics**: 81.3/100 average score
- **Anonymous Reporting**: 42% rate with variations by type
- **Resolution Rate**: 86% success rate

## 🌐 Access Points

Once started, visit: **https://localhost:8082**

### Main Pages
- **Dashboard**: Overview of incidents and metrics
- **Report Incident**: Submit new incidents (will generate real-time analytics)
- **AI Insights & Evaluation**: 📈 **Main analytics dashboard**
- **Incident History**: View all processed incidents
- **Human Review**: Review queue management

### API Endpoints
- `POST /api/v1/incidents/process` - Process new incidents
- `GET /api/analytics/overview` - Analytics overview
- `GET /api/analytics/trends` - Trend analysis
- `GET /api/analytics/policies` - Policy compliance
- `GET /api/v1/dashboard/analytics` - Dashboard data
- `GET /health` - Health check

## 🎯 Demo Walkthrough

1. **Start the server**: `python start_demo_8082.py`
2. **Open browser**: https://localhost:8082
3. **Navigate to**: "AI Insights & Evaluation"
4. **Explore tabs**:
   - **Trends**: Incident patterns and distributions
   - **Performance**: Radar chart and metrics
   - **AI Insights**: Generated lessons and recommendations

### Key Features to Demonstrate

1. **Overall Quality Score**: 81.3/100 with trend indicators
2. **Performance Radar**: 6-category visualization
3. **Incident Trends**: 
   - Security: 27% (highest)
   - Maintenance: 23%
   - Medical: 21%
4. **Temporal Patterns**: Friday peak (25 incidents)
5. **Anonymous Reporting**: 42% rate
6. **Real-time Updates**: Auto-refresh every 30 seconds

## 🔧 Troubleshooting

### Frontend Build Issues
If frontend build fails:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
cd ..
```

### Port Already in Use
If port 8082 is busy:
```bash
# Find and kill process using port 8082
lsof -ti:8082 | xargs kill -9
```

### Missing Dependencies
```bash
pip install fastapi uvicorn websockets langgraph langchain langchain-core flask
```

### No Demo Data
```bash
python generate_demo_data.py
```

## 📱 Mobile/Responsive

The dashboard is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile devices

## 🎭 Demo Tips

- **Auto-refresh**: Dashboard updates every 30 seconds
- **Manual refresh**: Click the refresh button
- **Tooltips**: Hover over charts for details
- **Tab switching**: Explore different views
- **Pattern recognition**: Notice Friday security spikes
- **Performance tracking**: Watch the radar chart
- **AI insights**: Read generated recommendations

## 🚀 Production Notes

For production deployment:
- Add SSL certificates
- Configure proper CORS origins
- Set up database instead of JSON files
- Add authentication/authorization
- Configure logging and monitoring

---

**Ready to explore!** 🎉

Start with `python start_demo_8082.py` and visit https://localhost:8082