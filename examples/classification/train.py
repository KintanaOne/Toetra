from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ==========================================================
# Paths
# ==========================================================
#
# Resolve all paths relative to this script location.
#
# This avoids issues caused by:
# - current working directory
# - IDE execution
# - CI/CD execution
# - pytest execution
#
# ==========================================================

ROOT = Path(__file__).resolve().parent

DATASET_PATH = ROOT / "heart-disease-cleveland.csv"

MODEL_PATH = ROOT / "heart_model.joblib"

CLEAN_DATASET_PATH = ROOT / "heart_clean.csv"

SCHEMA_PATH = ROOT / "schema.json"


# ==========================================================
# Load dataset
# ==========================================================

data = pd.read_csv(DATASET_PATH)


# ==========================================================
# Dataset normalization
# ==========================================================
#
# The Cleveland dataset may contain:
# - missing values represented as '?'
# - mixed column types
#
# We normalize the dataset before training.
#
# ==========================================================

# Replace '?' markers with pandas missing values
data = data.replace("?", pd.NA)


# ==========================================================
# Explicit numeric conversion
# ==========================================================
#
# Toetra relies heavily on semantic typing.
#
# We therefore avoid:
# - implicit conversions
# - dynamic inference magic
#
# and instead explicitly define the expected
# numeric columns.
#
# ==========================================================

NUMERIC_COLUMNS = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]

for column in NUMERIC_COLUMNS:

    data[column] = pd.to_numeric(data[column], errors="coerce")


# ==========================================================
# Remove invalid rows
# ==========================================================
#
# Rows containing unresolved values are removed.
#
# A future version of Toetra may support:
# - advanced imputation
# - uncertainty modeling
# - missing value constraints
#
# ==========================================================

data = data.dropna()


# ==========================================================
# Features / Target split
# ==========================================================

TARGET_COLUMN = "target"

X = data.drop(columns=[TARGET_COLUMN])

y = data[TARGET_COLUMN]


# ==========================================================
# Save cleaned dataset
# ==========================================================
#
# Toetra may later reuse this dataset for:
# - schema inference
# - semantic validation
# - domain extraction
# - SMT constraints
# - neighborhood generation
#
# ==========================================================

clean_data = pd.concat([X, y], axis=1)

clean_data.to_csv(CLEAN_DATASET_PATH, index=False)


# ==========================================================
# Export simplified schema
# ==========================================================
#
# The schema is intentionally simple for the MVP.
#
# Future versions may include:
# - domains
# - categorical values
# - nullable constraints
# - semantic metadata
#
# ==========================================================

schema = {}

for column, dtype in data.dtypes.items():

    dtype_str = str(dtype)

    if "int" in dtype_str:
        schema[column] = "int"

    elif "float" in dtype_str:
        schema[column] = "float"

    elif "bool" in dtype_str:
        schema[column] = "bool"

    else:
        schema[column] = "string"


pd.Series(schema).to_json(SCHEMA_PATH, indent=4)


# ==========================================================
# Train / Test split
# ==========================================================
#
# We keep:
# - deterministic split
# - stratification
#
# to ensure reproducible experiments.
#
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)


# ==========================================================
# Numeric preprocessing
# ==========================================================
#
# StandardScaler is applied to numeric features.
#
# The preprocessing pipeline is intentionally simple.
#
# ==========================================================

numeric_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

numeric_transformer = Pipeline(
    [("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
)


# ==========================================================
# Column preprocessing
# ==========================================================

preprocessor = ColumnTransformer([("numeric", numeric_transformer, numeric_features)])


# ==========================================================
# Model pipeline
# ==========================================================
#
# LogisticRegression is intentionally chosen because:
# - simple
# - interpretable
# - stable
# - suitable for first formal reasoning experiments
#
# ==========================================================

pipeline = Pipeline(
    [
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ]
)


# ==========================================================
# Train model
# ==========================================================

pipeline.fit(X_train, y_train)


# ==========================================================
# Evaluate model
# ==========================================================

predictions = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print(f"Accuracy: {accuracy:.4f}")


# ==========================================================
# Save trained model
# ==========================================================

joblib.dump(pipeline, MODEL_PATH)

print(f"Model saved to: {MODEL_PATH}")

print(f"Schema saved to: {SCHEMA_PATH}")

print(f"Clean dataset saved to: {CLEAN_DATASET_PATH}")
