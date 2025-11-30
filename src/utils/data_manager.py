import os
import pandas as pd
import json
from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)

class DataManager:
    def __init__(self, base_path="data/"):
        self.base_path = base_path
        self.ensure_directories()
        
    def ensure_directories(self):
        """Ensure all data directories exist"""
        directories = ['raw', 'processed', 'models', 'logs', 'temp']
        for dir_name in directories:
            path = os.path.join(self.base_path, dir_name)
            os.makedirs(path, exist_ok=True)
            
    def save_training_data(self, data, filename, metadata=None):
        """Save processed training data with metadata"""
        filepath = os.path.join(self.base_path, 'processed', filename)
        
        try:
            # Save data
            if isinstance(data, pd.DataFrame):
                data.to_csv(filepath, index=False)
            else:
                pd.DataFrame(data).to_csv(filepath, index=False)
                
            # Save metadata
            if metadata:
                meta_filepath = filepath.replace('.csv', '_metadata.json')
                with open(meta_filepath, 'w') as f:
                    json.dump(metadata, f, indent=4)
                    
            logger.info(f"Training data saved: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving training data: {e}")
            return False
            
    def load_training_data(self, filename):
        """Load processed training data"""
        filepath = os.path.join(self.base_path, 'processed', filename)
        
        try:
            data = pd.read_csv(filepath)
            logger.info(f"Training data loaded: {data.shape}")
            return data
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return None
            
    def save_model(self, model, model_name, metrics=None):
        """Save trained model with metrics"""
        import joblib
        
        model_path = os.path.join(self.base_path, 'models', f"{model_name}.pkl")
        metrics_path = os.path.join(self.base_path, 'models', f"{model_name}_metrics.json")
        
        try:
            # Save model
            joblib.dump(model, model_path)
            
            # Save metrics
            if metrics:
                metrics['save_timestamp'] = datetime.now().isoformat()
                with open(metrics_path, 'w') as f:
                    json.dump(metrics, f, indent=4)
                    
            logger.info(f"Model saved: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return False
            
    def list_models(self):
        """List all available trained models"""
        models_path = os.path.join(self.base_path, 'models')
        models = []
        
        for file in os.listdir(models_path):
            if file.endswith('.pkl'):
                model_info = {
                    'name': file.replace('.pkl', ''),
                    'path': os.path.join(models_path, file),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(os.path.join(models_path, file))
                    )
                }
                models.append(model_info)
                
        return models
        
    def get_data_statistics(self):
        """Get statistics about stored data"""
        stats = {
            'raw_files': len(os.listdir(os.path.join(self.base_path, 'raw'))),
            'processed_files': len(os.listdir(os.path.join(self.base_path, 'processed'))),
            'trained_models': len(self.list_models()),
            'total_size': self._get_directory_size(self.base_path)
        }
        
        return stats
        
    def _get_directory_size(self, path):
        """Calculate total directory size in MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)  # Convert to MB
