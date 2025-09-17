import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from auth import login_page, register_page, logout

# Handle Authentication
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["login"])[0]
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if not st.session_state.logged_in:
    if current_page == "register":
        register_page()
    else:
        login_page()
    st.stop()

# Logout button
st.sidebar.button("Logout", on_click=logout)

# Set background image function
def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Set background for the main page
set_background("https://www.shutterstock.com/image-photo/doctor-female-patient-meeting-hospital-600nw-767724232.jpg")
# Set page configuration (MUST be first Streamlit command)
#st.set_page_config(page_title="Mental Health Prediction", page_icon="🧠", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    file_path = "C:/Users/USER/Desktop/PATIENT/data.csv"
    df = pd.read_csv(file_path)
    return df

df = load_data()

#st.title("Patient Health Diagnosis & Treatment Prediction")

# Create sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Prediction", "Comparison Graph"])

if page == "Prediction":
    st.subheader("Enter Patient Details")

    # Identify categorical and numerical columns
    categorical_cols = df.select_dtypes(include=['object']).columns.drop("Label")  # Exclude target
    numerical_cols = df.select_dtypes(include=['number']).columns

    # Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le

    # Define features and target
    X = df.drop(columns=["Label"])  # Features
    y = df["Label"]  # Target

    # Encode target variable
    y_encoder = LabelEncoder()
    y = y_encoder.fit_transform(y)

    # Split data and train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # User input form
    def user_input():
        input_data = {}
        for col in X.columns:
            if col in categorical_cols:
                input_data[col] = st.selectbox(f"Select {col}", label_encoders[col].classes_)
            else:
                input_data[col] = st.number_input(f"Enter {col}", min_value=float(df[col].min()), max_value=float(df[col].max()), value=float(df[col].mean()))
        return pd.DataFrame([input_data])

    input_df = user_input()

    # Predict button
    if st.button("Predict"):
        # Convert categorical input to numeric
        for col in categorical_cols:
            input_df[col] = label_encoders[col].transform(input_df[col].astype(str))

        # Make prediction
        prediction = model.predict(input_df)
        predicted_label = y_encoder.inverse_transform(prediction)[0]

        # Recommendations based on predicted label
        recommendations = {
            "Anxious": "Practice mindfulness, deep breathing, and seek therapy if needed.",
            "Neutral": "Maintain a balanced lifestyle and keep engaging in positive activities.",
            "Happy": "Continue your current lifestyle and spread positivity to others.",
            "Excited": "Channel your energy into productive activities and enjoy the moment!",
            "Stressed": "Take breaks, engage in physical activity, and talk to someone about your concerns.",
            "Depressed": "Seek professional help, talk to loved ones, and engage in activities that bring you joy."
        }
        recommendation = recommendations.get(predicted_label, "No specific recommendation available.")

        st.subheader("Prediction")
        st.write(f"Predicted Label: {predicted_label}")
        st.subheader("Recommendation")
        st.write(recommendation)

elif page == "Comparison Graph":
    st.subheader("Comparison of Mental Health Labels")
    label_counts = df["Label"].value_counts()
    
    fig, ax = plt.subplots()
    label_counts.plot(kind='bar', color=['blue', 'green', 'red', 'purple', 'orange', 'cyan'], ax=ax)
    ax.set_xlabel("Mental Health Labels")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Mental Health Labels in Dataset")
    st.pyplot(fig)
