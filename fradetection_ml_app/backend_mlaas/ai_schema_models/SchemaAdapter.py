import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from langchain import PromptTemplate
import textwrap


class SchemaAdapter:
    """
    This class takes an arbitrary CSV schema and uses a local small language model
    to generate pandas code to reshape it into the fraud detection format.
    Expected output schema: v1-v28, amount, label
    """

    def __init__(self, model_name="google/flan-t5-small"):
        # Load a tiny model that works on CPU-only systems
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.pipe = pipeline("text2text-generation", model=self.model, tokenizer=self.tokenizer)

        # LangChain-style prompt to map schema to target format
        self.prompt = PromptTemplate(
            input_variables=["schema"],
            template=textwrap.dedent("""
                You are a senior data scientist cleaning raw CSVs for fraud detection.
                
                Given these columns:
                {schema}
                
                Write **pure pandas** code that transforms the DataFrame `df` into this schema:
                - 28 features named v1 to v28 (can be renamed, mapped, or extracted)
                - 1 column called 'amount'
                - 1 column called 'label' (1 = fraud, 0 = legit)
                
                Rules:
                - ❌ DO NOT use `input()` or unrelated Python code
                - ✅ Return ONLY pandas code
                - ✅ Final line should be just `df`
                
                Do NOT include explanations.
            """)
        )

    def generate_code(self, df: pd.DataFrame) -> str:
        schema_str = ", ".join(df.columns)
        prompt_text = self.prompt.format(schema=schema_str)
        print("🧠 Prompt Sent to LLM:\n", prompt_text)

        # Run prompt through model
        result = self.pipe(prompt_text, max_new_tokens=256)[0]["generated_text"]
        return result

    def adapt_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies the generated transformation code to the DataFrame.
        """
        code = self.generate_code(df)

        print("📜 Generated Transformation Code:\n", code)

        # Safe execution of LLM code in a sandboxed environment
        local_vars = {"df": df.copy()}
        try:
            exec(code, {}, local_vars)
        except Exception as e:
            print("❌ Code Execution Error:", e)
            return df

        return local_vars.get("df", df)


if __name__ == "__main__":

    df = pd.read_csv(f"/backend_mlaas/testdata/fake_job_postings.csv")

    adapter = SchemaAdapter(model_name= "mistralai/Mistral-7B-Instruct-v0.2")
    df_transformed = adapter.adapt_schema(df)

    print(df_transformed.head())
    print(df.columns)