# 🤖 AI Analytics Dashboard

A self-serve AI analytics layer that allows users to create Power BI dashboards using natural language prompts, powered by Claude AI.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL running on port 5432
- Claude API key (already configured in your project)

### Start the System

**On Windows:**
```bash
start_ai_analytics.bat
```

**On Linux/Mac:**
```bash
chmod +x start_ai_analytics.sh
./start_ai_analytics.sh
```

### Access the Dashboard
1. Open your browser to: http://localhost:3004
2. Navigate to the "AI Analytics" menu item
3. Select a table from your database
4. Enter a natural language prompt
5. Generate DAX/SQL code and export to Power BI

## 🏗️ Architecture

### Frontend (Prostgles UI)
- **Location**: `frontend/prostgles/client/src/pages/AIAnalytics/`
- **Components**:
  - `AIAnalyticsDashboard.tsx` - Main dashboard interface
  - `DashboardBuilder.tsx` - Modal for creating dashboards
  - `PromptToDAX.tsx` - Natural language input component
  - `PowerBIExport.tsx` - Export functionality

### Backend (FastAPI)
- **Location**: `fastapi_middleware/api/main.py`
- **Endpoints**:
  - `GET /api/tables` - List database tables
  - `POST /api/generate-dashboard` - Generate DAX/SQL from prompt
  - `GET /api/dashboard/{table}/data` - Export data for Power BI

### AI Integration
- **Location**: `backend_mlaas/ai_schema_models/schema_adapter_anthropic_v2.py`
- **Features**:
  - Natural language to DAX conversion
  - Natural language to SQL conversion
  - Schema-aware prompting

## 📊 How It Works

### 1. Table Selection
- Users select a table from their PostgreSQL database
- System automatically fetches table schema (column names, types)

### 2. Natural Language Input
- Users enter prompts like:
  - "Show me total fraud by month"
  - "Create a chart showing fraud amount trends over time"
  - "Display fraud percentage by category"

### 3. AI Code Generation
- Claude AI analyzes the prompt and table schema
- Generates both DAX (Power BI) and SQL code
- Provides context-aware suggestions

### 4. Export Options
- **Power BI (.pbids)**: Direct connection file for Power BI Desktop
- **DAX Code**: Copy-paste into Power BI measures
- **SQL Code**: Use for direct database queries

## 🎯 Example Usage

### Step 1: Access AI Analytics
1. Go to http://localhost:3004
2. Click "AI Analytics" in the navigation menu

### Step 2: Select Table
1. Choose a table from the dropdown (e.g., "transactions")
2. Click "Create Dashboard"

### Step 3: Enter Prompt
1. Type: "Show me total fraud by month"
2. Click "Generate Dashboard"

### Step 4: Review Generated Code
- **DAX**: `FraudByMonth = CALCULATE(COUNT(transactions[fraud_flag]), transactions[fraud_flag] = 1)`
- **SQL**: `SELECT DATE_TRUNC('month', date) as month, COUNT(*) as fraud_count FROM transactions WHERE fraud_flag = 1 GROUP BY month`

### Step 5: Export
1. Download .pbids file for Power BI Desktop
2. Or copy DAX/SQL code for manual use

## 🔧 Configuration

### Claude API Key
The system uses your existing Claude API key from:
```
backend_mlaas/ai_schema_models/claude_api_key.py
```

### Database Connection
The system connects to your existing PostgreSQL database:
- **Host**: localhost
- **Port**: 5432
- **Database**: mlapp
- **User**: postgres

### Ports
- **Frontend**: 3004 (Prostgles)
- **Backend**: 8000 (FastAPI)
- **Database**: 5432 (PostgreSQL)

## 🛠️ Development

### Adding New Features

#### 1. New AI Prompts
Edit `backend_mlaas/ai_schema_models/schema_adapter_anthropic_v2.py`:
```python
def generate_custom_prompt(self, table_name: str, columns: list, prompt: str) -> str:
    # Add your custom prompt logic here
    pass
```

#### 2. New Export Formats
Edit `frontend/prostgles/client/src/pages/AIAnalytics/PowerBIExport.tsx`:
```typescript
const downloadCustomFormat = () => {
    // Add your custom export logic here
};
```

#### 3. New API Endpoints
Edit `fastapi_middleware/api/main.py`:
```python
@app.post("/api/custom-endpoint")
async def custom_endpoint():
    # Add your custom endpoint logic here
    pass
```

### Testing

#### Test the API
```bash
curl -X POST "http://localhost:8000/api/generate-dashboard" \
  -H "Content-Type: application/json" \
  -d '{
    "table": "transactions",
    "prompt": "Show me total fraud by month",
    "columns": [{"name": "fraud_flag", "type": "boolean"}]
  }'
```

#### Test the Frontend
1. Start the system
2. Navigate to http://localhost:3004/ai-analytics
3. Test with different prompts and tables

## 🐛 Troubleshooting

### Common Issues

#### 1. "Failed to fetch tables"
- Ensure PostgreSQL is running on port 5432
- Check database connection settings
- Verify table permissions

#### 2. "Failed to generate dashboard"
- Check Claude API key is valid
- Ensure internet connection for API calls
- Check API rate limits

#### 3. "Port already in use"
- Stop existing services on ports 3004/8000
- Use `netstat -an | find "3004"` (Windows) or `lsof -i :3004` (Linux/Mac)

#### 4. "Module not found"
- Install dependencies: `pip install -r fastapi_middleware/requirements.txt`
- Ensure Python path includes backend_mlaas directory

### Logs
- **Frontend**: Check browser console (F12)
- **Backend**: Check FastAPI logs in terminal
- **Database**: Check PostgreSQL logs

## 📈 Future Enhancements

### Planned Features
1. **More BI Tools**: Tableau, Looker integration
2. **Advanced Prompts**: Multi-table joins, complex aggregations
3. **Template Library**: Pre-built dashboard templates
4. **Collaboration**: Share dashboards with team members
5. **Scheduling**: Automated dashboard refresh

### Customization Options
1. **Custom AI Models**: Support for other LLMs
2. **Custom Export Formats**: Excel, CSV, JSON
3. **Custom Visualizations**: Chart.js, D3.js integration
4. **Custom Authentication**: OAuth, SSO integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of your fraud detection ML application and follows the same license terms.

---

**Need Help?** Check the troubleshooting section or create an issue in the repository. 