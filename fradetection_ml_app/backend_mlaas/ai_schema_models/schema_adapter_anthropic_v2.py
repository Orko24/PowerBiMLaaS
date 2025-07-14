import pandas as pd
import numpy as np
import time
import random
from langchain_anthropic import ChatAnthropic
from anthropic._exceptions import OverloadedError
from backend_mlaas.ai_schema_models.claude_api_key import claude_api_key


class SchemaAdapterClaude:
    """
    Enhanced version of your SchemaAdapterClaude class.

    KEY IMPROVEMENTS (non-breaking):
    1. ✅ Added retry logic with exponential backoff (fixes API overload errors)
    2. ✅ Added circuit breaker pattern for resilience
    3. ✅ Enhanced fallback transformations that actually work
    4. ✅ Better error handling and debugging info
    5. ✅ All your original methods work unchanged
    6. ✅ Added offline mode for testing without API calls
    """

    def __init__(self, model="claude-3-5-sonnet-20241022", api_key=claude_api_key, temperature=0.1):
        # UNCHANGED - same interface as your original
        self.llm = ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

        # NEW - Resilience features
        self.max_retries = 3
        self.base_delay = 1
        self.circuit_breaker_failures = 0
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 60

    def analyze_data_type(self, df: pd.DataFrame) -> dict:
        """
        UNCHANGED from your original - same smart data analysis logic
        Your architecture correctly identifies different data types
        """
        columns = df.columns.tolist()

        analysis = {
            'data_type': 'unknown',
            'has_target': False,
            'target_column': None,
            'text_columns': [],
            'categorical_columns': [],
            'numerical_columns': [],
            'boolean_columns': [],
            'needs_feature_engineering': True
        }

        # Check if already formatted
        v_columns = [col for col in columns if col.upper().startswith('V') and col[1:].isdigit()]
        has_amount = any(col.lower() == 'amount' for col in columns)
        has_class = any(col.lower() in ['class', 'label', 'target'] for col in columns)

        if len(v_columns) >= 20 and has_amount and has_class:
            analysis['data_type'] = 'already_formatted'
            analysis['needs_feature_engineering'] = False
            return analysis

        # Detect target column
        target_candidates = ['fraudulent', 'fraud', 'class', 'label', 'target', 'is_fake', 'is_spam']
        for col in columns:
            if col.lower() in target_candidates:
                analysis['has_target'] = True
                analysis['target_column'] = col
                break

        # Categorize columns by type
        for col in columns:
            col_data = df[col].dropna()
            if len(col_data) == 0:
                continue

            if col_data.dtype == bool or set(col_data.unique()).issubset({0, 1, True, False}):
                analysis['boolean_columns'].append(col)
            elif pd.api.types.is_numeric_dtype(col_data):
                analysis['numerical_columns'].append(col)
            elif col_data.dtype == object and col_data.str.len().mean() > 20:
                analysis['text_columns'].append(col)
            elif col_data.dtype == object:
                analysis['categorical_columns'].append(col)

        # Determine data type
        if any(col.lower() in ['title', 'description', 'job_id'] for col in columns):
            analysis['data_type'] = 'job_postings'
        elif any(col.lower() in ['transaction', 'amount', 'time'] for col in columns):
            analysis['data_type'] = 'financial'
        elif len(analysis['text_columns']) > 2:
            analysis['data_type'] = 'text_heavy'
        elif len(analysis['numerical_columns']) > 10:
            analysis['data_type'] = 'numerical'
        else:
            analysis['data_type'] = 'mixed'

        return analysis

    def _is_circuit_breaker_open(self) -> bool:
        """NEW - Circuit breaker pattern for API resilience"""
        if self.circuit_breaker_failures >= self.circuit_breaker_threshold:
            time_since_last_failure = time.time() - self.circuit_breaker_last_failure
            if time_since_last_failure < self.circuit_breaker_timeout:
                return True
            else:
                self.circuit_breaker_failures = 0
        return False

    def _record_failure(self):
        """NEW - Track API failures for circuit breaker"""
        self.circuit_breaker_failures += 1
        self.circuit_breaker_last_failure = time.time()

    def create_smart_prompt(self, df: pd.DataFrame, analysis: dict) -> str:
        """
        UNCHANGED from your original - same intelligent prompting logic
        Your context-aware prompting strategy is excellent
        """
        columns = df.columns.tolist()
        data_type = analysis['data_type']

        if data_type == 'job_postings':
            return self._create_job_postings_prompt(columns, analysis)
        elif data_type == 'financial':
            return self._create_financial_prompt(columns, analysis)
        elif data_type == 'already_formatted':
            return self._create_already_formatted_prompt(columns, analysis)
        else:
            return self._create_generic_prompt(columns, analysis)

    def _create_job_postings_prompt(self, columns: list, analysis: dict) -> str:
        """UNCHANGED - your original job postings prompt logic"""
        target_col = analysis.get('target_column', 'fraudulent')
        text_cols = analysis['text_columns'][:4]
        cat_cols = analysis['categorical_columns'][:6]
        bool_cols = analysis['boolean_columns']

        return f"""
You are transforming job posting data for fraud detection.

Current columns: {', '.join(columns)}
Target column for fraud: {target_col}
Text columns: {text_cols}
Categorical columns: {cat_cols}
Boolean columns: {bool_cols}

Create exactly 28 features (V1-V28) using smart feature engineering:

Text Features (use for V1-V8):
- Text length: len(str(col))
- Word count: str(col).split().__len__()
- Character diversity: len(set(str(col)))
- Has suspicious keywords: int('urgent' in str(col).lower())

Categorical Features (use for V9-V20):
- Label encoding: pd.Categorical(col).codes
- Value counts: col.map(col.value_counts())

Boolean Features (use for V21-V24):
- Direct conversion: col.astype(int)

Engineered Features (use for V25-V28):
- Ratios, combinations, interaction terms

Amount: Extract from salary_range if exists, else 0
Label: {target_col} converted to int (1=fraud, 0=legit)

Return ONLY pandas code, no explanations.
"""

    def _create_financial_prompt(self, columns: list, analysis: dict) -> str:
        """UNCHANGED - your original financial prompt logic"""
        return f"""
You are transforming financial transaction data for fraud detection.
Current columns: {', '.join(columns)}
Keep existing V1-V28 columns if they exist, or create from numerical features.
For Amount: use existing amount/transaction_amount column
For label: use existing class/fraud column
Return ONLY pandas code, no explanations.
"""

    def _create_already_formatted_prompt(self, columns: list, analysis: dict) -> str:
        """UNCHANGED - your original already formatted prompt logic"""
        return f"""
You are working with data that's already close to the target format.
Current columns: {', '.join(columns)}
Task: Clean and standardize to exact target format:
- Ensure columns V1 to V28 exist (uppercase V)
- Ensure 'Amount' column exists (uppercase A)
- Ensure 'label' column exists (lowercase, 1=fraud, 0=legit)
- Drop unnecessary columns like 'Time' 
- Handle any missing V columns by creating them with value 0
Return ONLY pandas code, no explanations.
"""

    def _create_generic_prompt(self, columns: list, analysis: dict) -> str:
        """UNCHANGED - your original generic prompt logic"""
        num_cols = analysis['numerical_columns']
        cat_cols = analysis['categorical_columns']
        return f"""
You are transforming mixed data for fraud detection.
Numerical columns: {num_cols}
Categorical columns: {cat_cols}
Strategy:
1. Use numerical columns directly for V1-VX
2. Encode categorical columns for remaining V features  
3. Create interaction/engineered features to reach 28 total
4. Set Amount to first numerical column or 0
5. Create binary label (default 0 if no target found)
Return ONLY pandas code, no explanations.
"""

    def _generate_robust_fallback_code(self, df: pd.DataFrame, analysis: dict) -> str:
        """
        ENHANCED - Much more robust fallback code that actually works
        Fixed the V24 indexing issue from your original
        """
        if analysis['data_type'] == 'job_postings':
            return '''
# ROBUST Job postings transformation
import pandas as pd
import numpy as np

# Initialize all V columns first
for i in range(1, 29):
    df[f'V{i}'] = 0

# Text features (V1-V8) - safe extraction
text_cols = ['title', 'company_profile', 'description', 'requirements']
v_idx = 1
for col in text_cols[:4]:
    if col in df.columns:
        df[f'V{v_idx}'] = df[col].astype(str).str.len()
        df[f'V{v_idx+1}'] = df[col].astype(str).str.split().str.len()
        v_idx += 2

# Categorical features (V9-V20)
cat_cols = ['location', 'department', 'employment_type', 'industry', 'function', 'required_experience']
v_idx = 9
for col in cat_cols:
    if col in df.columns and v_idx <= 20:
        df[f'V{v_idx}'] = pd.Categorical(df[col].fillna('unknown')).codes
        v_idx += 1

# Boolean features (V21-V24)
bool_cols = ['telecommuting', 'has_company_logo', 'has_questions']
v_idx = 21
for col in bool_cols:
    if col in df.columns and v_idx <= 24:
        df[f'V{v_idx}'] = df[col].astype(int)
        v_idx += 1

# Engineered features (V25-V28) - safe operations
df['V25'] = df['V1'] / (df['V2'] + 1)
df['V26'] = df['V3'] / (df['V4'] + 1)  
df['V27'] = df['V21'] + df['V22'] + df['V23']
df['V28'] = df['V9'] + df['V10']

# Amount and label
if 'salary_range' in df.columns:
    df['Amount'] = pd.to_numeric(df['salary_range'].astype(str).str.extract(r'(\\d+)')[0], errors='coerce').fillna(0)
else:
    df['Amount'] = 0

if 'fraudulent' in df.columns:
    df['label'] = df['fraudulent'].astype(int)
else:
    df['label'] = 0

# Select final columns
final_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
df = df[final_cols].fillna(0)
'''
        else:
            return '''
# ROBUST Generic transformation
import pandas as pd
import numpy as np

# Initialize all V columns
for i in range(1, 29):
    df[f'V{i}'] = 0

# Use available numerical columns
num_cols = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
for i, col in enumerate(num_cols[:28]):
    df[f'V{i+1}'] = df[col].fillna(0)

# Use categorical columns
cat_cols = [col for col in df.columns if df[col].dtype == 'object']
for i, col in enumerate(cat_cols[:5]):
    if 28 - len(num_cols) > i:
        df[f'V{len(num_cols)+i+1}'] = pd.Categorical(df[col].fillna('unknown')).codes

df['Amount'] = df[num_cols[0]] if num_cols else 0
df['label'] = 0

final_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
df = df[final_cols].fillna(0)
'''

    def generate_code(self, df: pd.DataFrame) -> tuple[str, dict]:
        """
        ENHANCED with retry logic and circuit breaker
        Your original logic preserved, just made more resilient
        """
        analysis = self.analyze_data_type(df)
        print(f"🔍 Data Type Detected: {analysis['data_type']}")
        print(f"📊 Analysis: {analysis}")

        # NEW - Check circuit breaker
        if self._is_circuit_breaker_open():
            print("🔒 Circuit breaker open, using fallback...")
            return self._generate_robust_fallback_code(df, analysis), analysis

        prompt_text = self.create_smart_prompt(df, analysis)
        print("🧠 Prompt Sent to Claude:\n", prompt_text)
        print("-" * 50)

        # response = None
        # NEW - Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                response = self.llm.invoke(prompt_text)
                self.circuit_breaker_failures = 0  # Reset on success
                break

            except OverloadedError as e:
                self._record_failure()
                if attempt == self.max_retries - 1:
                    print(f"❌ API overloaded after {self.max_retries} attempts. Using fallback...")
                    return self._generate_robust_fallback_code(df, analysis), analysis

                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                print(
                    f"⏳ API overloaded, retrying in {delay:.2f} seconds... (attempt {attempt + 1}/{self.max_retries})")
                time.sleep(delay)

            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                return self._generate_robust_fallback_code(df, analysis), analysis

        # Extract and clean code - SAME as your original
        if hasattr(response, 'content'):
            code = response.content
        else:
            code = str(response)

        code = code.strip()
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]

        return code.strip(), analysis

    def adapt_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        ENHANCED version of your original method
        Same interface, better error handling and fallback
        """
        code, analysis = self.generate_code(df)

        print("📜 Generated Transformation Code:\n")
        print(code)
        print("-" * 50)

        # Execute with better error handling
        local_vars = {"df": df.copy(), "pd": pd, "np": np}
        try:
            exec(code, globals(), local_vars)
            result_df = local_vars.get("df", df)

            # Validate result
            expected_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
            actual_cols = result_df.columns.tolist()

            if set(expected_cols).issubset(set(actual_cols)):
                print("✅ Transformation successful!")
                return result_df[expected_cols]
            else:
                print("⚠️ Schema validation failed, attempting fallback...")
                return self._fallback_transformation(df, analysis)

        except Exception as e:
            print(f"❌ Code Execution Error: {e}")
            print("🔧 Using fallback transformation...")
            return self._fallback_transformation(df, analysis)

    def adapt_schema_offline(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        NEW METHOD - Skip API entirely for testing
        Useful when you want to test without API calls
        """
        analysis = self.analyze_data_type(df)
        print(f"🔄 Using offline transformation for {analysis['data_type']} data")
        return self._fallback_transformation(df, analysis)

    def _fallback_transformation(self, df: pd.DataFrame, analysis: dict) -> pd.DataFrame:
        """
        ENHANCED - More robust fallback that handles edge cases better
        """
        print("🛠️ Executing fallback transformation...")
        result_df = df.copy()

        # Create all V columns with zeros first
        for i in range(1, 29):
            result_df[f'V{i}'] = 0

        # Use numerical columns
        num_cols = [col for col in analysis['numerical_columns'] if col in result_df.columns]
        for i, col in enumerate(num_cols[:28]):
            result_df[f'V{i + 1}'] = result_df[col].fillna(0)

        # Use categorical columns
        remaining_slots = 28 - len(num_cols)
        cat_cols = [col for col in analysis['categorical_columns'] if col in result_df.columns]
        for i, col in enumerate(cat_cols[:remaining_slots]):
            result_df[f'V{len(num_cols) + i + 1}'] = pd.Categorical(result_df[col].fillna('unknown')).codes

        # Amount column
        amount_candidates = ['amount', 'salary_range', 'price', 'value']
        result_df['Amount'] = 0
        for col in amount_candidates:
            if col in df.columns:
                try:
                    result_df['Amount'] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    break
                except:
                    result_df['Amount'] = 0

        # Label column
        if analysis['has_target']:
            target_col = analysis['target_column']
            result_df['label'] = df[target_col].astype(int)
        else:
            result_df['label'] = 0

        # Final selection and cleanup
        final_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
        result_df = result_df[final_cols].fillna(0)

        print(f"✅ Fallback transformation complete: {result_df.shape}")
        return result_df

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

    def analyze_table_schema(self, table_name: str, db_connection) -> dict:
        """Analyze table schema for better prompting"""
        
        query = f"""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
        """
        
        columns = db_connection.execute(query).fetchall()
        
        return {
            'table_name': table_name,
            'columns': [{'name': c[0], 'type': c[1], 'nullable': c[2]} for c in columns],
            'total_columns': len(columns)
        }

    def preview_data(self, df: pd.DataFrame, n_rows: int = 5):
        """UNCHANGED - your original preview method works perfectly"""
        print(f"\n📊 Data Preview (first {n_rows} rows):")
        print(df.head(n_rows))
        print(f"\n📈 Data Shape: {df.shape}")
        print(f"\n🔍 Column Names: {list(df.columns)}")
        print(f"\n📋 Data Types Summary:")
        print(df.dtypes.value_counts())
        if 'label' in df.columns:
            print(f"\n🎯 Label Distribution:")
            print(df['label'].value_counts())