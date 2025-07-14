import pandas as pd
import numpy as np
from langchain_anthropic import ChatAnthropic
from backend_mlaas.ai_schema_models.claude_api_key import claude_api_key


class SchemaAdapterClaude:
    """
    Intelligently adapts any CSV schema to fraud detection format using Claude.
    Uses context-aware prompting based on data type analysis.
    """

    def __init__(self, model="claude-3-5-sonnet-20241022", api_key=claude_api_key, temperature=0.1):
        self.llm = ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=temperature
        )
        self.model = model
        self.api_key = api_key
        self.temperature = temperature

    def analyze_data_type(self, df: pd.DataFrame) -> dict:
        """Analyze the DataFrame to understand what type of data we're dealing with"""

        columns = df.columns.tolist()
        sample_data = df.head(3)

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

        # Check if it's already in target format
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

            # Check if boolean
            if col_data.dtype == bool or set(col_data.unique()).issubset({0, 1, True, False}):
                analysis['boolean_columns'].append(col)
            # Check if numerical
            elif pd.api.types.is_numeric_dtype(col_data):
                analysis['numerical_columns'].append(col)
            # Check if looks like text (long strings)
            elif col_data.dtype == object and col_data.str.len().mean() > 20:
                analysis['text_columns'].append(col)
            # Everything else is categorical
            elif col_data.dtype == object:
                analysis['categorical_columns'].append(col)

        # Determine data type based on columns
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

    def create_smart_prompt(self, df: pd.DataFrame, analysis: dict) -> str:
        """Create a context-aware prompt based on data analysis"""

        columns = df.columns.tolist()
        data_type = analysis['data_type']

        if data_type == 'already_formatted':
            return self._create_already_formatted_prompt(columns, analysis)
        elif data_type == 'job_postings':
            return self._create_job_postings_prompt(columns, analysis)
        elif data_type == 'financial':
            return self._create_financial_prompt(columns, analysis)
        elif data_type == 'text_heavy':
            return self._create_text_heavy_prompt(columns, analysis)
        else:
            return self._create_generic_prompt(columns, analysis)

    def _create_already_formatted_prompt(self, columns: list, analysis: dict) -> str:
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

    def _create_job_postings_prompt(self, columns: list, analysis: dict) -> str:
        target_col = analysis.get('target_column', 'fraudulent')
        text_cols = analysis['text_columns'][:4]  # Limit to top 4
        cat_cols = analysis['categorical_columns'][:6]  # Limit to top 6
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
        return f"""
You are transforming financial transaction data for fraud detection.

Current columns: {', '.join(columns)}

Keep existing V1-V28 columns if they exist, or create from numerical features.
For Amount: use existing amount/transaction_amount column
For label: use existing class/fraud column

Return ONLY pandas code, no explanations.
"""

    def _create_text_heavy_prompt(self, columns: list, analysis: dict) -> str:
        text_cols = analysis['text_columns']
        return f"""
You are transforming text-heavy data for fraud detection.

Text columns: {text_cols}

Create 28 features from text analysis:
- Text length and word count features
- Character diversity metrics  
- Keyword presence indicators
- Statistical text properties

Use feature engineering to create meaningful numerical representations.

Return ONLY pandas code, no explanations.
"""

    def _create_generic_prompt(self, columns: list, analysis: dict) -> str:
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

    def generate_code(self, df: pd.DataFrame) -> tuple[str, dict]:
        """Generate transformation code using intelligent prompting"""

        # Analyze the data first
        analysis = self.analyze_data_type(df)
        print(f"🔍 Data Type Detected: {analysis['data_type']}")
        print(f"📊 Analysis: {analysis}")

        # Create smart prompt
        prompt_text = self.create_smart_prompt(df, analysis)
        print("🧠 Prompt Sent to Claude:\n", prompt_text)
        print("-" * 50)

        # Get response from Claude
        response = self.llm.invoke(prompt_text)

        # Extract code
        if hasattr(response, 'content'):
            code = response.content
        else:
            code = str(response)

        # Clean up the code
        code = code.strip()
        if code.startswith('```python'):
            code = code[9:]
        if code.startswith('```'):
            code = code[3:]
        if code.endswith('```'):
            code = code[:-3]

        return code.strip(), analysis

    def adapt_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform DataFrame to target schema with intelligent prompting"""

        code, analysis = self.generate_code(df)

        print("📜 Generated Transformation Code:\n")
        print(code)
        print("-" * 50)

        # Execute code with error handling
        local_vars = {"df": df.copy(), "pd": pd, "np": np}
        try:
            exec(code, {"__builtins__": {}, "pd": pd, "np": np}, local_vars)
            result_df = local_vars.get("df", df)

            # Validate result
            expected_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
            actual_cols = result_df.columns.tolist()

            if set(expected_cols).issubset(set(actual_cols)):
                print("✅ Transformation successful!")
                # Return only the required columns in correct order
                return result_df[expected_cols]
            else:
                print("⚠️ Schema validation failed, attempting fallback...")
                return self._fallback_transformation(df, analysis)

        except Exception as e:
            print(f"❌ Code Execution Error: {e}")
            print("🔧 Using fallback transformation...")
            return self._fallback_transformation(df, analysis)

    def _fallback_transformation(self, df: pd.DataFrame, analysis: dict) -> pd.DataFrame:
        """Fallback transformation when AI-generated code fails"""

        print("🛠️ Executing fallback transformation...")
        result_df = df.copy()

        # Create 28 V columns using available data
        v_features = []

        # Use numerical columns first
        num_cols = analysis['numerical_columns']
        for col in num_cols[:20]:  # Use up to 20 numerical columns
            v_features.append(col)

        # Encode categorical columns
        cat_cols = analysis['categorical_columns']
        for col in cat_cols[:6]:  # Use up to 6 categorical columns
            if col in result_df.columns:
                result_df[f'{col}_encoded'] = pd.Categorical(result_df[col]).codes
                v_features.append(f'{col}_encoded')

        # Add boolean columns
        bool_cols = analysis['boolean_columns']
        for col in bool_cols[:4]:  # Use up to 4 boolean columns
            v_features.append(col)

        # Fill remaining slots with engineered features or zeros
        while len(v_features) < 28:
            v_features.append(f'feature_{len(v_features)}')
            result_df[f'feature_{len(v_features) - 1}'] = 0

        # Rename to V1-V28
        v_mapping = {old_name: f'V{i + 1}' for i, old_name in enumerate(v_features[:28])}
        result_df = result_df.rename(columns=v_mapping)

        # Create Amount column
        amount_candidates = ['amount', 'salary_range', 'price', 'value']
        result_df['Amount'] = 0
        for col in amount_candidates:
            if col in df.columns:
                # Try to extract numerical value
                try:
                    result_df['Amount'] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    break
                except:
                    result_df['Amount'] = 0

        # Create label column
        if analysis['has_target']:
            target_col = analysis['target_column']
            result_df['label'] = df[target_col].astype(int)
        else:
            result_df['label'] = 0  # Default to no fraud

        # Select final columns
        final_cols = [f'V{i}' for i in range(1, 29)] + ['Amount', 'label']
        result_df = result_df[final_cols].fillna(0)

        print(f"✅ Fallback transformation complete: {result_df.shape}")
        return result_df

    def preview_data(self, df: pd.DataFrame, n_rows: int = 5):
        """Preview the transformed data"""
        print(f"\n📊 Data Preview (first {n_rows} rows):")
        print(df.head(n_rows))
        print(f"\n📈 Data Shape: {df.shape}")
        print(f"\n🔍 Column Names: {list(df.columns)}")
        print(f"\n📋 Data Types Summary:")
        print(df.dtypes.value_counts())
        if 'label' in df.columns:
            print(f"\n🎯 Label Distribution:")
            print(df['label'].value_counts())


# Example usage
if __name__ == "__main__":
    # Test with job postings data
    testing_file = "/backend_mlaas/testdata/fake_job_postings.csv"


    df = pd.read_csv(testing_file)

    print("🔄 Original DataFrame Info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("\n" + "=" * 60 + "\n")

    # Create improved adapter
    adapter = SchemaAdapterClaude()
    df_transformed = adapter.adapt_schema(df)

    print("\n" + "=" * 60 + "\n")
    print("✅ Transformation Complete!")

    # Preview results
    adapter.preview_data(df_transformed)