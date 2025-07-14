from backend_mlaas.ml.load_to_postgres import CreateDatabase, LoadToPostgres
from backend_mlaas.ml.train_model import TrainModel  # Uncomment when you have this
import os
import tempfile

from sqlalchemy import text  # <-- ADD THIS LINE

class LoadDataAndTrain(CreateDatabase, LoadToPostgres, TrainModel):
    """
    Enhanced version of your LoadDataAndTrain class.

    KEY IMPROVEMENTS (non-breaking):
    1. ✅ Works with the enhanced LoadToPostgres (auto table creation)
    2. ✅ Better integration with your existing ML pipeline
    3. ✅ Added helper methods for new data processing
    4. ✅ All your original methods work unchanged
    5. ✅ Same multiple inheritance pattern you designed
    """

    def __init__(
            self,
            db_name="mlapp",
            user="postgres",
            password="pass",
            host="localhost",
            port="5432",
            csv_path="data/creditcard.csv",
            table_name="transactions",
            model_path="model/model.pkl"
    ):
        """
        UNCHANGED interface - same parameters as your original
        """
        # Set up DB creation credentials - SAME as your original
        CreateDatabase.__init__(self, db_name, user, password, host, port)

        # Set up data loading config - SAME as your original
        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
        LoadToPostgres.__init__(self, db_url, csv_path, table_name)

        # Train Model

        TrainModel.__init__(self,data_path= csv_path)

        # Store config - SAME as your original
        self.model_path = model_path
        self.db_url = db_url

    def run_pipeline(self):
        """
        ENHANCED version of your original method
        - Same core logic, now benefits from auto table creation
        - Better error handling
        """
        # Step 1: Create DB if it doesn't exist - UNCHANGED
        self.create_database_if_missing()

        # Step 2: Load data into PostgreSQL - SAME call, enhanced behavior
        print("📥 Loading CSV to PostgreSQL...")
        self.run(use_upsert=False)  # Enhanced: now auto-creates tables

        # Step 3: Train model if needed - SAME logic as your original
        if not os.path.exists(self.model_path):
            print("🧠 Training fraud detection model...")
            self.train_model()  # Uncomment when TrainModel is integrated
            # print("⚠️ TrainModel integration pending - add your train_model() call here")
        else:
            print("✅ Model already exists at:", self.model_path)

    def load_new_data_to_postgres(self, csv_path: str, new_table_name: str = "new_transactions"):
        """
        NEW METHOD - Enhanced data loading for new datasets
        Creates tables automatically, handles any CSV format

        This method allows you to:
        - Load any new CSV file
        - Create new tables automatically
        - Return the DataFrame for further processing
        """
        print(f"🔄 Processing new data from: {csv_path}")

        # Create a new LoadToPostgres instance for the new table
        # Uses enhanced version that auto-creates tables
        loader = LoadToPostgres(
            db_url=self.db_url,
            csv_path=csv_path,
            table_name=new_table_name
        )

        # Load and insert data (table will be created automatically)
        print(f"📤 Loading data to table: {new_table_name}")
        loader.run(use_upsert=False)

        # Return the processed DataFrame for further use
        return loader.load_csv()

    def create_table_for_adapted_data(self, adapted_df, table_name: str):
        """
        NEW METHOD - Create table from already-processed DataFrame
        Useful when you have adapted data that needs to go to PostgreSQL
        """
        print(f"📤 Creating table '{table_name}' from adapted DataFrame...")

        # Save DataFrame to temporary CSV
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_csv_path = temp_file.name
            adapted_df.to_csv(temp_csv_path, index=False)

        try:
            # Use enhanced LoadToPostgres to create table and insert data
            loader = LoadToPostgres(
                db_url=self.db_url,
                csv_path=temp_csv_path,
                table_name=table_name
            )
            loader.run(use_upsert=False)
            print(f"✅ Successfully created table '{table_name}' with {len(adapted_df)} rows")

        finally:
            # Clean up temporary file
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)

    def get_table_info(self, table_name: str = None):
        """
        NEW METHOD - Get information about tables in your database
        Useful for debugging and monitoring your data pipeline
        """
        if table_name is None:
            table_name = self.table_name

        try:
            with self.engine.connect() as conn:
                # Get table info
                result = conn.execute(text(f"""
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """))

                columns_info = result.fetchall()

                if columns_info:
                    print(f"📋 Table '{table_name}' schema:")
                    for col_name, data_type, nullable in columns_info:
                        print(f"  {col_name}: {data_type} ({'NULL' if nullable == 'YES' else 'NOT NULL'})")
                else:
                    print(f"❌ Table '{table_name}' does not exist")

        except Exception as e:
            print(f"❌ Error getting table info: {e}")


# # Example usage showing backward compatibility
# if __name__ == "__main__":
#     """
#     Your existing code will work exactly the same!
#     Just with enhanced functionality under the hood.
#     """
#
#     # UNCHANGED - same way you call it now
#     pipeline = LoadDataAndTrain(
#         db_name="mlapp",
#         user="postgres",
#         password="pass",
#         host="localhost",
#         port="5432",
#         csv_path="data/creditcard.csv",
#         table_name="transactions",
#         model_path="model/model.pkl"
#     )
#
#     # UNCHANGED - same method call, enhanced behavior
#     pipeline.run_pipeline()
#
#     # NEW - Additional functionality you can now use
#     # Load new data (will auto-create tables)
#     # pipeline.load_new_data_to_postgres("testdata/fake_job_postings.csv", "job_postings")
#
#     # Check table structure
#     # pipeline.get_table_info("transactions")