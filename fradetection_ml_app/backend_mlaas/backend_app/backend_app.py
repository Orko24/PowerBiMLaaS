from backend_mlaas.ai_schema_models.schema_adapter_anthropic_v2 import SchemaAdapterClaude
from backend_mlaas.ai_schema_models.claude_api_key import claude_api_key
from backend_mlaas.ml.LoadAndTrain import LoadDataAndTrain
from sklearn.metrics import accuracy_score
import pandas as pd
import tempfile
import os


class DataPredictor(LoadDataAndTrain, SchemaAdapterClaude):
    """
    Enhanced version of your DataPredictor class.

    KEY IMPROVEMENTS (non-breaking):
    1. ✅ Fixed column name case mismatch (V1 vs v1) that caused prediction errors
    2. ✅ Better error handling with informative messages
    3. ✅ Automatic table creation for new data
    4. ✅ More robust data processing pipeline
    5. ✅ All your original methods work unchanged
    6. ✅ Same multiple inheritance pattern you designed
    """

    def __init__(
            self, model="claude-3-5-sonnet-20241022", api_key=claude_api_key, temperature=0.1,
            db_name="mlapp", user="postgres", password="pass", host="localhost", port="5432",
            csv_path="data/creditcard.csv", table_name="transactions", model_path="model/model.pkl"
    ):
        """
        UNCHANGED interface - same parameters as your original
        """
        # Initialize both parent classes - SAME as your original
        SchemaAdapterClaude.__init__(self, model=model, api_key=api_key, temperature=temperature)
        LoadDataAndTrain.__init__(
            self, db_name=db_name, user=user, password=password, host=host, port=port,
            csv_path=csv_path, table_name=table_name, model_path=model_path
        )

        # Load and train base data - SAME as your original
        self.run_pipeline()

    def load_new_data_to_postgres(self, csv_path, new_table_name="new_transactions"):
        """
        ENHANCED version of your original method
        - Fixes the table creation issue you encountered
        - Better error handling and validation
        - Same interface as your original
        """
        print(f"🔄 Processing new data from: {csv_path}")

        # 1. Load and adapt schema - SAME logic as your original
        print("📊 Loading CSV data...")
        data = pd.read_csv(csv_path)
        print(f"Original data shape: {data.shape}")

        print("🔧 Adapting schema using Claude...")
        adapted_data = self.adapt_schema(data)
        print(f"Adapted data shape: {adapted_data.shape}")
        print(f"Adapted data head: {adapted_data.head()}")

        # CRITICAL FIX: Ensure column names are lowercase for ML model compatibility
        adapted_data.columns = [col.lower() for col in adapted_data.columns]

        # 2. Save adapted data to temporary CSV - SAME as your original
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            temp_csv_path = temp_file.name
            adapted_data.to_csv(temp_csv_path, index=False)

        try:
            # 3. Upload to PostgreSQL - ENHANCED with auto table creation
            print(f"📤 Uploading adapted data to PostgreSQL table: {new_table_name}")

            # Use enhanced LoadToPostgres that auto-creates tables
            from backend_mlaas.ml.load_to_postgres import LoadToPostgres
            loader = LoadToPostgres(
                db_url=self.db_url,
                csv_path=temp_csv_path,
                table_name=new_table_name
            )
            loader.run()  # Now handles table creation automatically!

            print(f"✅ Successfully uploaded {len(adapted_data)} rows to {new_table_name}")
            return adapted_data

        except Exception as e:
            print(f"❌ Error uploading data: {e}")
            # Still return the adapted data even if upload fails
            return adapted_data

        finally:
            # Clean up temporary file - SAME as your original
            if os.path.exists(temp_csv_path):
                os.unlink(temp_csv_path)

    # Fix for your DataPredictor class - add this method and update your prediction methods

    def standardize_column_names_for_model(self, df):
        """
        Ensure column names match what the ML model expects
        Convert lowercase to uppercase to match training data format
        """
        # Create mapping for standardization
        column_mapping = {}

        # Map v1-v28 to V1-V28
        for i in range(1, 29):
            if f'v{i}' in df.columns:
                column_mapping[f'v{i}'] = f'V{i}'

        # Map amount to Amount
        if 'amount' in df.columns:
            column_mapping['amount'] = 'Amount'

        # Keep label as lowercase (target column)
        # Don't change 'label' - it should stay lowercase

        # Apply the mapping
        df_standardized = df.rename(columns=column_mapping)

        print(f"🔧 Standardized column names: {list(df_standardized.columns)}")
        return df_standardized

    def test_model_accuracy_on_new_data(self, csv_path, new_table_name="new_transactions"):
        """
        FIXED version - handles column name case matching
        """
        try:
            # Load and upload new data
            adapted_data = self.load_new_data_to_postgres(csv_path, new_table_name)

            # Check if we have labels for accuracy testing
            if 'label' not in adapted_data.columns:
                print("⚠️  No 'label' column found - cannot compute accuracy")
                return None

            # FIX: Standardize column names to match model training format
            adapted_data = self.standardize_column_names_for_model(adapted_data)

            # Prepare features for prediction - USE UPPERCASE NAMES
            feature_cols = [f'V{i}' for i in range(1, 29)] + ['Amount']
            missing_cols = [col for col in feature_cols if col not in adapted_data.columns]

            if missing_cols:
                print(f"❌ Missing required columns for prediction: {missing_cols}")
                print(f"Available columns: {list(adapted_data.columns)}")
                return None

            X_new = adapted_data[feature_cols]
            y_true = adapted_data['label']

            # Load trained model and make predictions
            print("🔮 Making predictions on new data...")
            model = self.load_model()
            y_pred = model.predict(X_new)

            # Calculate accuracy
            # from sklearn.metrics import accuracy_score
            accuracy = accuracy_score(y_true, y_pred)
            print(f"📈 Model accuracy on new data: {accuracy:.4f}")

            return {
                'accuracy': accuracy,
                'predictions': y_pred,
                'true_labels': y_true,
                'adapted_data': adapted_data
            }

        except Exception as e:
            print(f"❌ Error in accuracy test: {e}")
            return None

    def predict_and_save_to_postgres(self, csv_path, new_table_name="predictions"):
        """
        FIXED version - handles column name case matching
        """
        try:
            # Load and process new data
            print(f"🔄 Processing data for predictions from: {csv_path}")

            # Load CSV and adapt schema
            data = pd.read_csv(csv_path)
            print(f"Original data shape: {data.shape}")

            adapted_data = self.adapt_schema(data)
            print(f"Adapted data shape: {adapted_data.shape}")

            # FIX: Standardize column names to match model training format
            adapted_data = self.standardize_column_names_for_model(adapted_data)

            # Validate required columns exist - USE UPPERCASE NAMES
            feature_cols = [f'V{i}' for i in range(1, 29)] + ['Amount']
            missing_cols = [col for col in feature_cols if col not in adapted_data.columns]

            if missing_cols:
                print(f"❌ Cannot make predictions - missing columns: {missing_cols}")
                print(f"Available columns: {list(adapted_data.columns)}")
                return None

            # Prepare features for prediction
            X_new = adapted_data[feature_cols]

            # Make predictions
            print("🔮 Making predictions on new data...")
            model = self.load_model()
            predictions = model.predict(X_new)
            prediction_proba = model.predict_proba(X_new)[:, 1]  # Probability of fraud

            # Add predictions to the adapted data
            adapted_data['prediction'] = predictions
            adapted_data['fraud_probability'] = prediction_proba

            # Save predictions to PostgreSQL
            print(f"💾 Saving predictions to table: {new_table_name}")
            self.create_table_for_adapted_data(adapted_data, new_table_name)

            print(f"✅ Saved {len(adapted_data)} predictions to table: {new_table_name}")

            # Summary statistics
            fraud_count = sum(predictions)
            total_count = len(predictions)
            fraud_rate = (fraud_count / total_count) * 100
            print(f"📊 Prediction Summary: {fraud_count}/{total_count} ({fraud_rate:.2f}%) flagged as fraud")

            return adapted_data

        except Exception as e:
            print(f"❌ Error in predictions: {e}")
            return None

    def batch_process_multiple_files(self, file_paths: list, base_table_name: str = "batch_predictions"):
        """
        NEW METHOD - Process multiple CSV files in batch
        Useful for processing multiple datasets at once
        """
        results = {}

        for i, csv_path in enumerate(file_paths):
            table_name = f"{base_table_name}_{i + 1}"
            print(f"\n🔄 Processing file {i + 1}/{len(file_paths)}: {csv_path}")

            try:
                result = self.predict_and_save_to_postgres(csv_path, table_name)
                results[csv_path] = {
                    'table_name': table_name,
                    'success': result is not None,
                    'data': result
                }
            except Exception as e:
                print(f"❌ Failed to process {csv_path}: {e}")
                results[csv_path] = {
                    'table_name': table_name,
                    'success': False,
                    'error': str(e)
                }

        # Summary
        successful = sum(1 for r in results.values() if r['success'])
        total = len(file_paths)
        print(f"\n📊 Batch Processing Complete: {successful}/{total} files processed successfully")

        return results

    def validate_model_performance(self, test_csv_paths: list):
        """
        NEW METHOD - Validate model performance across multiple test datasets
        Returns comprehensive performance metrics
        """
        all_results = []

        for csv_path in test_csv_paths:
            print(f"\n🧪 Testing model on: {csv_path}")
            result = self.test_model_accuracy_on_new_data(csv_path)

            if result:
                all_results.append({
                    'file': csv_path,
                    'accuracy': result['accuracy'],
                    'total_samples': len(result['true_labels']),
                    'fraud_samples': sum(result['true_labels']),
                    'predicted_fraud': sum(result['predictions'])
                })

        if all_results:
            # Calculate overall metrics
            total_samples = sum(r['total_samples'] for r in all_results)
            weighted_accuracy = sum(r['accuracy'] * r['total_samples'] for r in all_results) / total_samples

            print(f"\n📊 Overall Model Performance:")
            print(f"   Average Accuracy: {weighted_accuracy:.4f}")
            print(f"   Total Samples Tested: {total_samples}")
            print(f"   Files Tested: {len(all_results)}")

        return all_results


# # Example usage showing your original workflow still works
# if __name__ == "__main__":
#     """
#     Your existing code will work the same, just with enhanced reliability!
#     """
#
#     base_data_path = "C:\\Users\\heman\\OneDrive\\Desktop\\2025_apps\\Technical_Notes\\BoC\\fradetection_ml_app\\ml\\data\\creditcard.csv"
#
#     # Initialize predictor - SAME as your original
#     predictor = DataPredictor(
#         db_name="mlapp",
#         user="postgres",
#         password="pass",
#         host="localhost",
#         port="5432",
#         csv_path= base_data_path,
#         table_name="transactions",
#         model_path="model/model.pkl"
#     )
#
#     # Test accuracy on new data - SAME call, enhanced behavior
#     # Now handles table creation and column name issues automatically
#
#     testing_data = "C:\\Users\\heman\\OneDrive\\Desktop\\2025_apps\\Technical_Notes\\BoC\\fradetection_ml_app\\testdata\\fake_job_postings.csv"
#
#     result = predictor.test_model_accuracy_on_new_data(
#         csv_path= testing_data, new_table_name= "job_postings_test"
#     )
#
#     # Make predictions - SAME call, enhanced reliability
#     predictions = predictor.predict_and_save_to_postgres(
#         csv_path= testing_data, new_table_name= "job_postings_predictions"
#     )