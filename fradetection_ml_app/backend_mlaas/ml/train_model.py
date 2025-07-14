# train_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.utils import resample
from joblib import dump, load
import os


class TrainModel:

    def __init__(self, data_path):
        self.data_path = data_path
        self.data = self.load_data()

    def load_data(self):
        df = pd.read_csv(self.data_path)
        return df

    def X_y_generator(self):
        df = self.data.copy()
        # Downsample the majority class to balance the dataset
        df_majority = df[df.Class == 0]
        df_minority = df[df.Class == 1]
        df_majority_downsampled = resample(df_majority,
                                           replace=False,
                                           n_samples=len(df_minority) * 5,
                                           random_state=42)

        df_balanced = pd.concat([df_majority_downsampled, df_minority])
        df_balanced = df_balanced.sample(frac=1).reset_index(drop=True)

        # Features and labels
        X = df_balanced.drop(columns=["Class", "Time"])
        y = df_balanced["Class"]

        return X, y

    def train_model(self):
        X, y = self.X_y_generator()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train model
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)

        # Evaluate
        y_pred = clf.predict(X_test)
        y_proba = clf.predict_proba(X_test)[:, 1]

        print("Classification Report:\n", classification_report(y_test, y_pred))
        print("AUC Score:", roc_auc_score(y_test, y_proba))

        # Save model
        os.makedirs("model", exist_ok=True)
        dump(clf, "model/model.pkl")
        print("✅ Model saved to model/model.pkl")

    def load_model(self, model_path="model/model.pkl"):
        """
        Load the trained model from pickle file
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"❌ Model not found at {model_path}. Train model first!")

        model = load(model_path)
        print(f"✅ Model loaded from {model_path}")
        return model