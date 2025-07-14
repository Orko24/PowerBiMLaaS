from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import sys
import json

# Try to import from backend_mlaas, fallback to direct import
try:
    # Add the backend_mlaas directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(current_dir, '..', '..')
    backend_mlaas_path = os.path.join(project_root, 'backend_mlaas')
    sys.path.insert(0, backend_mlaas_path)
    
    from ai_schema_models.schema_adapter_anthropic_v2 import SchemaAdapterClaude
    from ai_schema_models.claude_api_key import claude_api_key
    print("✅ Successfully imported from backend_mlaas")
except ImportError as e:
    print(f"⚠️ Could not import from backend_mlaas: {e}")
    print("🔄 Using direct Claude API integration...")
    
    # Fallback: Direct Claude integration
    from langchain_anthropic import ChatAnthropic
    
    # Claude API key (you'll need to set this)
    claude_api_key = "put your api key here"
    
    class SchemaAdapterClaude:
        def __init__(self, model="claude-3-5-sonnet-20241022", api_key=claude_api_key, temperature=0.1):
            self.llm = ChatAnthropic(
                model=model,
                api_key=api_key,
                temperature=temperature
            )
            self.model = model
            self.api_key = api_key
            self.temperature = temperature
        
        def generate_dax_from_prompt(self, table_name: str, columns: list, prompt: str) -> str:
            """Generate DAX code from natural language prompt"""
            claude_prompt = f"""
            You are a Power BI DAX expert. Convert natural language queries into DAX.
            
            Table: {table_name}
            Columns: {', '.join(columns)}
            
            User Request: {prompt}
            
            Generate DAX code that:
            1. Uses proper DAX syntax
            2. Handles the specific table and columns
            3. Returns meaningful results
            
            Return ONLY the DAX code, no explanations.
            """
            
            try:
                response = self.llm.invoke(claude_prompt)
                code = response.content.strip()
                
                # Clean up code
                if code.startswith('```dax'):
                    code = code[7:]
                if code.startswith('```'):
                    code = code[3:]
                if code.endswith('```'):
                    code = code[:-3]
                    
                return code.strip()
            except Exception as e:
                print(f"Error generating DAX: {e}")
                return f"// Error generating DAX: {e}"
        
        def generate_sql_from_prompt(self, table_name: str, columns: list, prompt: str) -> str:
            """Generate SQL code from natural language prompt"""
            claude_prompt = f"""
            You are a SQL expert. Convert natural language queries into SQL.
            
            Table: {table_name}
            Columns: {', '.join(columns)}
            
            User Request: {prompt}
            
            Generate SQL code that:
            1. Uses proper SQL syntax
            2. Handles the specific table and columns
            3. Returns meaningful results
            
            Return ONLY the SQL code, no explanations.
            """
            
            try:
                response = self.llm.invoke(claude_prompt)
                code = response.content.strip()
                
                # Clean up code
                if code.startswith('```sql'):
                    code = code[7:]
                if code.startswith('```'):
                    code = code[3:]
                if code.endswith('```'):
                    code = code[:-3]
                    
                return code.strip()
            except Exception as e:
                print(f"Error generating SQL: {e}")
                return f"-- Error generating SQL: {e}"

app = FastAPI(title="AI Analytics API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Claude adapter
claude_adapter = SchemaAdapterClaude(
    model="claude-3-5-sonnet-20241022",
    api_key=claude_api_key,
    temperature=0.1
)

# Pydantic models
class GenerateDashboardRequest(BaseModel):
    table: str
    prompt: str
    columns: List[Dict[str, str]]

class GenerateDashboardResponse(BaseModel):
    dax: str
    sql: str
    columns: List[Dict[str, str]]

class TableInfo(BaseModel):
    table_name: str
    columns: List[Dict[str, str]]

# Database connection (you'll need to implement this based on your setup)
def get_db_connection():
    # This should connect to your PostgreSQL database
    # For now, we'll use a placeholder
    pass

@app.get("/")
async def root():
    return {"message": "AI Analytics API is running"}

@app.get("/api/tables")
async def get_tables():
    """Get all tables from the connected database"""
    try:
        # This should query your database
        # For now, return a placeholder
        return ["transactions", "predictions", "job_postings_test"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-dashboard", response_model=GenerateDashboardResponse)
async def generate_dashboard(request: GenerateDashboardRequest):
    """Generate DAX and SQL from natural language prompt"""
    try:
        # Extract column names for the prompt
        column_names = [col['name'] for col in request.columns]
        
        # Generate DAX and SQL using the adapter methods
        dax_code = claude_adapter.generate_dax_from_prompt(
            table_name=request.table,
            columns=column_names,
            prompt=request.prompt
        )
        
        sql_code = claude_adapter.generate_sql_from_prompt(
            table_name=request.table,
            columns=column_names,
            prompt=request.prompt
        )
        
        return GenerateDashboardResponse(
            dax=dax_code,
            sql=sql_code,
            columns=request.columns
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

@app.get("/api/dashboard/{table}/data")
async def get_dashboard_data(table: str):
    """Get data for Power BI connection"""
    try:
        # This should query your database and return data
        # For now, return a placeholder
        return {
            "table": table,
            "data": [],
            "message": "Data endpoint - implement database query here"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Analytics API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
