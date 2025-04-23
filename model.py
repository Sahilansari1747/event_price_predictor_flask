import joblib
import pandas as pd

def load_model():
    model = joblib.load('model/model.pkl')
    return model

model = load_model()

def predict_price(event_type, guest_count, venue_area, food_type, decoration, entertainment, duration):
    input_data = pd.DataFrame([{
        "Event Type": event_type,
        "Guest Count": guest_count,
        "Venue Area (sq ft)": venue_area,
        "Food Type": food_type,
        "Decoration Level": decoration,
        "Entertainment": entertainment,
        "Event Duration (hrs)": duration
    }])

    prediction = model.predict(input_data)
    return int(prediction[0])