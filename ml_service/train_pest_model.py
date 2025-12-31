import pandas as pd
import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# ==========================
# 📌 LOAD & CLEAN DATA
# ==========================
df = pd.read_csv("datasets/dataset_indian_crop_price.csv", encoding="latin1")

df.columns = (
    df.columns.str.strip()
              .str.replace('\n','')
              .str.replace('\r','')
)

# Detect temperature column automatically
temp_col = next((c for c in df.columns if "temp" in c.lower()), None)
if not temp_col:
    raise Exception("❌ Temperature column not found in dataset!")

print(f"🔍 Temperature column detected as: {temp_col}")

# ==========================
# 🧠 AUTO-CALCULATE PEST INDEX (B3 LOGIC)
# ==========================
def generate_pest_index(row):
    score = 0.5  # baseline

    if row[temp_col] >= 35: score += 0.2
    elif row[temp_col] <= 20: score -= 0.1

    if row["Rainfall (mm)"] > 800: score += 0.15
    elif row["Rainfall (mm)"] < 300: score += 0.2

    if row["Season"] == "Zaid": score += 0.1
    if row["Season"] == "Kharif": score += 0.05
    if row["Season"] == "Rabi": score -= 0.1

    high_risk_crops = ["Cotton","Brinjal","Chilli","Tomato"]
    if row["Crop Type"] in high_risk_crops:
        score += 0.1

    return max(0, min(1, score))

df["Auto_Pest_Index"] = df.apply(generate_pest_index, axis=1)
print("🆕 Auto_Pest_Index created ✔️")

# ==========================
# 🤖 CLUSTER TO GENERATE PEST RISK LABELS
# ==========================
features = [temp_col, "Rainfall (mm)", "Auto_Pest_Index"]
scaler = StandardScaler()
scaled = scaler.fit_transform(df[features])

kmeans = KMeans(n_clusters=3, random_state=42)
df["cluster"] = kmeans.fit_predict(scaled)

cluster_scores = kmeans.cluster_centers_.sum(axis=1)
order = cluster_scores.argsort()
labels = ["Low","Medium","High"]
cluster_map = {order[i]: labels[i] for i in range(3)}
df["Pest Risk"] = df["cluster"].map(cluster_map)
df.drop(columns=["cluster"], inplace=True)

print("\n🎯 Learned Pest Risk Groups:")
for i,c in enumerate(cluster_scores):
    print(f"{cluster_map[i]} → Score {c:.2f}")

# ==========================
# 🤖 TRAIN FINAL ML MODEL
# ==========================
X = df[["State","Crop Type","Season", temp_col, "Rainfall (mm)", "Auto_Pest_Index"]]
y = df["Pest Risk"]

categorical = ["State","Crop Type","Season"]
numeric = [temp_col,"Rainfall (mm)","Auto_Pest_Index"]

processor = ColumnTransformer([
    ("cat",OneHotEncoder(handle_unknown="ignore"),categorical),
    ("num",StandardScaler(),numeric)
])

model = Pipeline([
    ("process",processor),
    ("clf",RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42))
])

model.fit(X, y)

# ==========================
# 💾 SAVE MODELS
# ==========================
joblib.dump(model,"pest_risk_model.pkl")
joblib.dump(kmeans,"pest_cluster_model.pkl")
joblib.dump(scaler,"risk_scaler.pkl")

print("\n🚀 Training Complete — Model Saved Successfully!")
