import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# --------------------------------------------------
# 1. Locate project root and data directory
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[3]   # OceanFront/

DATA_DIR = Path(
    "D:/Documents/ACADEMIC/BTECH/TY/Sem-I_Mod-V/EDAI-V/"
    "OceanFrontRepo/OceanFront/oceanFrontData/Parquet"
)

# Take first 5 PARQUET files (sorted for consistency)
files = sorted(DATA_DIR.glob("*.parquet"))[:5]

if len(files) < 5:
    raise ValueError("Less than 5 Parquet files found in Parquet directory")

print("Loading Parquet files:")
for f in files:
    print(" -", f.name)

# --------------------------------------------------
# 2. Load PARQUET files
# --------------------------------------------------
dfs = []

for f in files:
    df_part = pd.read_parquet(f)
    dfs.append(df_part)

# Combine all files
df = pd.concat(dfs, ignore_index=True)

# Clean column names
df.columns = df.columns.str.strip()

print("\nCombined dataset shape:", df.shape)
print("Columns available:", df.columns.tolist())

# --------------------------------------------------
# 3. Feature selection
# --------------------------------------------------
features = [
    'latitude', 'longitude', 'position_qc', 'positioning_system', 'vertical_sampling_scheme'
]
target = "n_prof"

X = df[features]
y = df[target]

# --------------------------------------------------
# 4. Train-test split
# --------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# --------------------------------------------------
# 5. Train Random Forest model
# --------------------------------------------------
rf = RandomForestRegressor(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)

# --------------------------------------------------
# 6. Evaluate model
# --------------------------------------------------
y_pred = rf.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\nModel Performance:")
print(f"MSE: {mse:.4f}")
print(f"R²: {r2:.4f}")

# --------------------------------------------------
# 7. Save trained model
# --------------------------------------------------
MODEL_DIR = BASE_DIR / "backend" / "models" / "RandomForest"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

joblib.dump(rf, MODEL_DIR / "random_forest_model.pkl")
print("\nModel saved successfully.")

# --------------------------------------------------
# 8. User input for prediction
# --------------------------------------------------
print("\nEnter values for depth prediction:")

latitude_min = float(input("Latitude Min: "))
latitude_max = float(input("Latitude Max: "))
longitude_min = float(input("Longitude Min: "))
longitude_max = float(input("Longitude Max: "))
depth_min = float(input("Depth Min: "))

user_input = [[
latitude,
longitude,
position_qc,
positioning_system, 
vertical_sampling_scheme
]]

predicted_depth = rf.predict(user_input)

print(f"\nPredicted Maximum Depth: {predicted_depth[0]:.2f}")
print(f"Model Accuracy (R²): {r2:.4f}")
