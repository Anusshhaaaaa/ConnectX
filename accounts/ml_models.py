import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from django.conf import settings

class ToxicityClassifier:
    def __init__(self, model_path=None):
        self.model_path = model_path or os.path.join(settings.BASE_DIR, 'ml_models', 'toxicity_model.pkl')
        self.model = self._load_model()
        
        # Fallback keyword-based detection if model isn't trained
        self.fallback_keywords = {
            'hate', 'stupid', 'idiot', 'fool', 'dumb', 'ugly', 'pathetic', 
            'trash', 'garbage', 'sucks', 'loser', 'dead', 'kill', 'shut up'
        }

    def _load_model(self):
        """Load the trained model from disk if it exists."""
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading model: {e}")
        return None

    def train(self, dataset_path, text_column='text', label_column='is_toxic'):
        """
        Train the model on a dataset (CSV/JSON).
        dataset_path: Path to the dataset file.
        text_column: Name of the column containing text.
        label_column: Name of the column containing labels (0 for safe, 1 for toxic).
        """
        try:
            # Load dataset
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith('.json'):
                df = pd.read_json(dataset_path)
            else:
                raise ValueError("Unsupported file format. Use CSV or JSON.")
            
            # Create a pipeline: TF-IDF -> Naive Bayes
            # This is scalable and efficient for initial large datasets
            model = make_pipeline(TfidfVectorizer(), MultinomialNB())
            
            # Train
            model.fit(df[text_column], df[label_column])
            
            # Save
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            with open(self.model_path, 'wb') as f:
                pickle.dump(model, f)
            
            self.model = model
            return True, "Model trained successfully."
        except Exception as e:
            return False, str(e)

    def predict(self, text):
        """
        Predict if text is toxic.
        Returns: (is_toxic, probability)
        """
        if not text:
            return False, 0.0

        if self.model:
            try:
                # Predict probability
                prob = self.model.predict_proba([text])[0][1]
                return prob > 0.5, prob
            except Exception as e:
                print(f"Prediction error: {e}")
        
        # Fallback to simple keyword matching if model fails or doesn't exist
        text_lower = text.lower()
        for word in self.fallback_keywords:
            if word in text_lower:
                return True, 0.8  # Arbitrary high confidence for direct keyword match
        
        return False, 0.0
