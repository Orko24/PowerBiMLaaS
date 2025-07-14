# backend_test.py
import sys
import os

# Add the parent directory to Python path for imports
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_app.backend_app import DataPredictor

# Example usage
# Example usage showing your original workflow still works
if __name__ == "__main__":
    """
    Your existing code will work the same, just with enhanced reliability!
    """

    base_data_path = "/backend_mlaas/ml/data/creditcard.csv"

    # Initialize predictor - SAME as your original
    predictor = DataPredictor(
        db_name="mlapp",
        user="postgres",
        password="pass",
        host="localhost",
        port="5432",
        csv_path= base_data_path,
        table_name="transactions",
        model_path="model/model.pkl"
    )

    # Test accuracy on new data - SAME call, enhanced behavior
    # Now handles table creation and column name issues automatically

    testing_data = "C:\\Users\\heman\\OneDrive\\Desktop\\2025_apps\\Technical_Notes\\BoC\\fradetection_ml_app\\testdata\\fake_job_postings.csv"

    result = predictor.test_model_accuracy_on_new_data(
        csv_path= testing_data, new_table_name= "job_postings_test"
    )

    # Make predictions - SAME call, enhanced reliability
    predictions = predictor.predict_and_save_to_postgres(
        csv_path= testing_data, new_table_name= "job_postings_predictions"
    )