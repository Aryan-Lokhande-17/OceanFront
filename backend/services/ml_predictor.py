"""
ML Prediction Service
Handles predictions using LSTM, RandomForest, and XGBoost models
Provides unified interface for getting predictions from Argo buoy data
"""

import os
import numpy as np
from pathlib import Path
from config import config

class MLPredictor:
    """Unified interface for ML predictions on oceanographic data"""
    
    def __init__(self):
        self.models_path = Path(config.PARQUET_DATA_PATH).parent / "models"
        self.lstm_model = None
        self.rf_model = None
        self.xgb_model = None
        self._load_models()
    
    def _load_models(self):
        """Lazy load ML models"""
        try:
            # Try to load LSTM model
            lstm_path = self.models_path / "lstm_mld_best.keras"
            if lstm_path.exists():
                try:
                    import tensorflow as tf
                    self.lstm_model = tf.keras.models.load_model(lstm_path)
                    print("[OK] LSTM model loaded")
                except:
                    print("[!] Could not load LSTM model")
        except Exception as e:
            print(f"[!] Error loading LSTM: {e}")
    
    def predict_temperature_profile(self, latitude, longitude, depth_levels=10):
        """
        Predict temperature profile for a given location
        
        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            depth_levels: Number of depth levels to predict
        
        Returns:
            dict with predictions or error
        """
        try:
            if self.lstm_model is None:
                return {
                    "success": False,
                    "error": "LSTM model not available",
                    "model": "lstm"
                }
            
            # Create input features (normalize lat/lon)
            input_data = np.array([[
                latitude / 90.0,  # Normalize latitude (-90 to 90)
                (longitude + 180) / 360.0  # Normalize longitude (-180 to 180)
            ]])
            
            # Make prediction
            prediction = self.lstm_model.predict(input_data, verbose=0)
            
            return {
                "success": True,
                "model": "lstm",
                "predictions": prediction.tolist() if prediction is not None else [],
                "latitude": latitude,
                "longitude": longitude,
                "depths": list(range(0, depth_levels * 100, 100))  # 0m to depth_levels*100m
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "lstm"
            }
    
    def predict_salinity_anomaly(self, temperature, latitude):
        """
        Predict salinity anomaly based on temperature and location
        
        Args:
            temperature: Water temperature in Celsius
            latitude: Latitude of the location
        
        Returns:
            dict with prediction
        """
        try:
            # Simple heuristic: salinity varies with latitude and temperature
            # Higher latitudes and lower temperatures → higher salinity
            # This is a placeholder; real model would use RandomForest
            
            base_salinity = 35.0
            temp_effect = (25 - temperature) * 0.05  # ~0.05 PSU per 1°C difference
            lat_effect = abs(latitude) * 0.01  # Polar regions more saline
            
            predicted_salinity = base_salinity + temp_effect + lat_effect
            
            return {
                "success": True,
                "model": "heuristic",
                "predicted_salinity": round(predicted_salinity, 2),
                "temperature": temperature,
                "latitude": latitude,
                "factors": {
                    "base_salinity": base_salinity,
                    "temperature_effect": round(temp_effect, 3),
                    "latitude_effect": round(lat_effect, 3)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "heuristic"
            }
    
    def predict_mixed_layer_depth(self, temperature, latitude, longitude):
        """
        Predict mixed layer depth (MLD) for a given location and temperature
        Uses heuristic based on oceanographic principles
        
        Args:
            temperature: Sea surface temperature
            latitude: Latitude
            longitude: Longitude
        
        Returns:
            dict with MLD prediction
        """
        try:
            # Heuristic for MLD:
            # Colder waters → deeper MLD
            # Tropical waters → shallower MLD
            # Higher latitude → generally deeper MLD
            
            # Base MLD (typical tropical waters)
            base_mld = 50.0  # meters
            
            # Temperature effect (colder = deeper)
            temp_effect = (20 - temperature) * 10  # 10m per 1°C below 20°C
            
            # Latitude effect (higher latitude = deeper)
            lat_effect = abs(latitude) * 2
            
            # Monsoon regions (Arabian Sea/Bay of Bengal) have variable MLD
            regional_effect = 0
            if longitude < 72:
                regional_effect = 20  # Arabian Sea slightly deeper
            elif longitude > 85:
                regional_effect = 30  # Bay of Bengal varies with monsoon
            
            predicted_mld = max(10, base_mld + temp_effect + lat_effect + regional_effect)
            
            return {
                "success": True,
                "model": "mld_heuristic",
                "predicted_mld_meters": round(predicted_mld, 1),
                "temperature": temperature,
                "latitude": latitude,
                "longitude": longitude,
                "factors": {
                    "base_mld": base_mld,
                    "temperature_effect": round(temp_effect, 1),
                    "latitude_effect": round(lat_effect, 1),
                    "regional_effect": round(regional_effect, 1)
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "mld_heuristic"
            }
    
    def get_prediction_summary(self, buoy_data: dict) -> dict:
        """
        Get comprehensive prediction summary for a buoy location
        
        Args:
            buoy_data: dict with keys latitude, longitude, temperature, salinity
        
        Returns:
            dict with all predictions
        """
        try:
            predictions = {
                "buoy_id": buoy_data.get("buoy_id", "Unknown"),
                "latitude": buoy_data.get("latitude"),
                "longitude": buoy_data.get("longitude"),
                "models": {}
            }
            
            # Get predictions from each model
            predictions["models"]["temperature_profile"] = self.predict_temperature_profile(
                buoy_data.get("latitude", 0),
                buoy_data.get("longitude", 0)
            )
            
            predictions["models"]["salinity_anomaly"] = self.predict_salinity_anomaly(
                buoy_data.get("temperature", 25),
                buoy_data.get("latitude", 0)
            )
            
            predictions["models"]["mixed_layer_depth"] = self.predict_mixed_layer_depth(
                buoy_data.get("temperature", 25),
                buoy_data.get("latitude", 0),
                buoy_data.get("longitude", 0)
            )
            
            return predictions
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
ml_predictor = MLPredictor()
