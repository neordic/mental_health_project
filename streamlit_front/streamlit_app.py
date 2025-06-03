import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")


if "token" not in st.session_state:
    st.session_state["token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "form"


auth_mode = st.sidebar.radio("Choose action", ["Login", "Register"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")


if auth_mode == "Register":
    username = st.sidebar.text_input("Username")

if auth_mode == "Login":
    if st.sidebar.button("Login"):
        response = requests.post(
            f"{API_URL}/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            st.session_state["token"] = response.json()["access_token"]
            st.success("Successfully logged in!")
        else:
            st.error("Login failed")

if auth_mode == "Register":
    if st.sidebar.button("Register"):
        response = requests.post(
            f"{API_URL}/auth/register",
            json={"username": username, "email": email, "password": password}
        )
        if response.status_code == 200:
            st.success("Successfully registered! You can now log in.")
        elif response.status_code == 409:
            st.warning("This email is already registered. Please log in.")
        else:
            st.error(f"Registration failed: {response.status_code}")


token = st.session_state.get("token")
headers = {"Authorization": f"Bearer {token}"} if token else {}


st.sidebar.markdown("---")
if st.sidebar.button("🧠 Check Depression Risk"):
    st.session_state["page"] = "form"

if st.sidebar.button("📜 Previous Checks"):
    st.session_state["page"] = "history"

if st.sidebar.button("💰 Balance & Transactions"):
    st.session_state["page"] = "billing"

if st.sidebar.button("🚪 Logout"):
    st.session_state["token"] = None
    st.session_state["page"] = "form"
    st.success("Logged out successfully")
    st.rerun()


# --- Main Content ---

# Not authenticated
if not token:
    st.warning("Please log in to continue.")
    st.stop()

# Page: Inference Form
if st.session_state["page"] == "form":
    st.title("🧠 Mental Health Assessment")
    st.subheader("Enter user data:")
    input_data = {
        "Age": st.number_input("Age", min_value=10, max_value=100, value=30),
        "Income": st.number_input("Daily Income (USD)", min_value=0, step=100),
        "Employment_Status": st.radio("Employment Status", ["Unemployed", "Employed"]),
        "Education_Level": st.selectbox("Education Level", ["High School", "Bachelor's Degree", "Master's Degree", "PhD"]),
        "Marital_Status": st.selectbox("Marital Status", ["Single", "Divorced", "Widowed", "Separated", "Married", "In a relationship"]),
        "Number_of_Children": st.number_input("Number of Children", min_value=0, max_value=10, step=1),
        "Family_History_of_Depression": st.radio("Family History of Depression", ["Yes", "No"]),
        "History_of_Mental_Illness": st.radio("Personal History of Mental Illness", ["Yes", "No"]),
        "Chronic_Medical_Conditions": st.radio("Chronic Medical Conditions", ["Yes", "No"]),
        "Smoking_Status": st.radio("Smoking Status", ["Never", "Former", "Current"]),
        "Alcohol_Consumption": st.radio("Alcohol Consumption", ["None", "Moderate", "High"]),
        "Physical_Activity_Level": st.radio("Physical Activity Level", ["Low", "Moderate", "Active"]),
        "Dietary_Habits": st.radio("Dietary Habits", ["Poor", "Moderate", "Healthy"]),
        "Sleep_Patterns": st.radio("Sleep Patterns", ["Poor", "Fair", "Good"]),
    }

    model_type = st.radio("Model Type", ["simple", "advanced", "premium"])
    if st.button("🔍 Check Depression Risk"):
        payload = {
            "model_type": model_type,
            "input_data": input_data
        }
        response = requests.post(f"{API_URL}/inference/submit", json=payload, headers=headers)
        if response.status_code == 200:
            task = response.json()
            st.success(f"Result: {task.get('result')}")
        else:
            st.error(f"Error: {response.status_code}, {response.text}")

elif st.session_state["page"] == "history":
    st.title("📜 Previous Checks")

    response = requests.get(f"{API_URL}/inference/history", headers=headers)
    if response.status_code == 200:
        history = response.json()
        for item in history:
            st.markdown(f"""
            **Date:** {item['created_at']}  
            **Model:** {item['model_type']}  
            **Result:** {item.get('result', '—')}  
            **Score:** {item.get('score', '—')}
            """)
            with st.expander("Show Input Data"):
                st.json(item["input_data"])
    else:
        st.error("Failed to load inference history")


elif st.session_state["page"] == "billing":
    st.title("💰 Balance & Transactions")

    credit_resp = requests.get(f"{API_URL}/billing/balance", headers=headers)
    billing_resp = requests.get(f"{API_URL}/billing/history_detailed", headers=headers)

    if credit_resp.status_code == 200:
        balance = credit_resp.json()["balance"]
        st.subheader("💳 Current Balance:")
        st.info(f"{balance} credits")
    else:
        st.error("Failed to fetch balance")

    if billing_resp.status_code == 200:
        history = billing_resp.json()
        st.subheader("📊 Billing History:")
        for rec in history:
            st.markdown(f"""
            **Date:** {rec['timestamp']}  
            **Model:** {rec.get('model_type', 'N/A')}  
            **Amount:** {rec['amount']}  
            **Description:** {rec.get('explanation', '—')}
            """)
    else:
        st.error("Failed to load billing history")                  