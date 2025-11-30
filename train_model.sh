#!/bin/bash

echo "Training AI Firewall Models..."

# Activate virtual environment
source ai_firewall_env/bin/activate

# Create sample training data and train models
python -c "
from src.data_processing.data_loader import DataLoader
from src.ml_models.model_trainer import ModelTrainer
import numpy as np

# Create sample data
loader = DataLoader()
data = loader.create_sample_data(1000)

# Prepare features and labels
X = data.drop('label', axis=1).values
y = data['label'].values

# Train models
trainer = ModelTrainer()
anomaly_detector = trainer.train_anomaly_detector(X)
classifier, accuracy = trainer.train_threat_classifier(X, y)

print(f'Model training completed with accuracy: {accuracy:.4f}')
"

echo "Model training completed!"
