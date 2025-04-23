import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib

# Match these column names exactly with the ones used in prediction
data = pd.DataFrame({
    'Event Type': ['wedding', 'conference', 'birthday', 'wedding'],
    'Guest Count': [100, 50, 30, 200],
    'Venue Area (sq ft)': [500, 300, 200, 800],
    'Food Type': ['veg', 'non-veg', 'veg', 'non-veg'],
    'Decoration Level': ['simple', 'grand', 'simple', 'grand'],
    'Entertainment': ['DJ', 'Live Band', 'None', 'DJ'],
    'Event Duration (hrs)': [5, 3, 2, 6],
    'Price': [50000, 40000, 20000, 90000]
})

X = data.drop('Price', axis=1)
y = data['Price']

categorical_features = ['Event Type', 'Food Type', 'Decoration Level', 'Entertainment']
categorical_transformer = OneHotEncoder(handle_unknown='ignore')

preprocessor = ColumnTransformer(
    transformers=[('cat', categorical_transformer, categorical_features)],
    remainder='passthrough'
)

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor())
])

model.fit(X, y)

# Save the trained pipeline (this is what you load and call .predict() on)
joblib.dump(model, 'model/model.pkl')
print("✅ Model trained and saved as model/model.pkl")