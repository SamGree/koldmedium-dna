import streamlit as st
import pandas as pd
from CoolProp.CoolProp import PropsSI
import base64

# ----------------------------
# Helper: load background image
# ----------------------------
def get_base64_image(path):
    with open(path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Köldmedium-identifierare",
    layout="centered"
)

# Load background image
# NOTE: Ensure 'images/background.jpg' exists in your directory structure
bg_image = get_base64_image("images/background.jpg")

# ----------------------------
# Custom CSS (FIXED)
# ----------------------------
st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

.main {{
    background-color: rgba(255, 255, 255, 0.88);
    padding: 25px;
    border-radius: 12px;
}}

h1 {{
    color: white;
    border: 2px solid black;
    border-radius: 25px;
    background-color: white;
}}

.warning {{
    color: red;
    padding-top: 20px;
    padding-bottom: 20px;
    font-weight: bold;
    border-radius: 35px;
    background-color: white;
    text-align: center;
}}

.success {{
    color: green;
    font-weight: bold;
    border-radius: 25px;
    background-color: white;
}}


.info {{
    color: #003366;
    border-radius: 25px;
    border: 2px solid black;
    background-color: white;
    padding-top: 20px;
    padding-bottom: 20px;
    text-align: center;
}}
div[data-testid="stNumberInput"] label {{
    background-color: #e8f0fe;
    padding: 4px 8px;
    border-radius: 8px;
    display: inline-block;
    width: fit-content;
}}

.st-key-info_box {{
        background-color: #f0f2f6; /* Light gray background */
        padding: 20px;
        border-radius: 10px;
    }}

    /* Add this CSS rule to your existing <style> block */
footer {{
    visibility: hidden;
    display: none; /* Helps ensure no empty space is left behind */
}}


 /* --- Mobile Specific Styles (Max width 600px) --- */
@media (max-width: 600px) {{
    .warning, .success, .info {{
        padding: 8px 10px;
        font-size: 14px;
    }}
    
    div[data-testid="stNumberInput"] label {{
        padding: 2px 4px;
        font-size: 12px;
    }}
    
    /* Make the H1 title significantly smaller on mobile */
    h1 {{
        font-size: 20px !important; /* Use !important to force override */
        padding: 5px;
    }}
}}
   
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Title
# ----------------------------
st.title("🔍 Köldmedium-DNA (PT-metod)")
st.markdown(
    "<p class='info'>⚠️ Endast indikativt verktyg – ej godkänd identifieringsmetod</p>",
    unsafe_allow_html=True
)

# ----------------------------
# User input
# ----------------------------
P_bar = st.number_input("Tryck (bar (a))", min_value=0.0, value=5.0, step=0.1)
T_c = st.number_input("Temperatur (°C)", value=20.0, step=1.0)

# Unit conversion
P_measured = P_bar * 1e5       # Pa
T_measured = T_c + 273.15      # K

# ----------------------------
# Refrigerants
# ----------------------------
refrigerants = ["R134a", "R404A", "R407C", "R410A", "R717", "R744", "R12", "R22", "R1234yf", "R1234ze", "R32",
                "R417A", "R507", "R290", "R600a", "R718", "R1270"]
tolerance = 0.2e5  # ±0.2 bar

# ----------------------------
# Button Logic & Data Calculation
# ----------------------------
# This entire section runs only when the button is clicked
if st.button("Identifiera köldmedium"):
    results = []

    for ref in refrigerants:
        try:
            P_sat = PropsSI("P", "T", T_measured, "Q", 1, ref)
            diff_bar = (P_sat - P_measured) / 1e5
            confidence = max(0, 100 - abs(diff_bar) * 50)

            # Phase estimation
            try:
                T_sat = PropsSI("T", "P", P_measured, "Q", 1, ref)
                if abs(T_measured - T_sat) < 2:
                    phase = "Mättad"
                elif T_measured > T_sat:
                    phase = "Överhettad gas"
                else:
                    phase = "Underkyld vätska"
            except:
                phase = "Okänd"

            results.append({
                "Köldmedium": ref,
                "Mättnadstryck (bar)": round(P_sat / 1e5, 2),
                "Differens (bar)": round(diff_bar, 2),
                "Säkerhet (%)": round(confidence, 1),
                "Fas": phase
            })

        except:
            pass

    # 'df' and 'matches' are defined here
    df = pd.DataFrame(results)
    matches = df[abs(df["Differens (bar)"]) < tolerance / 1e5]

    # ----------------------------
    # Output Sections (Moved Inside Button Block or use Session State)
    # To fix the NameError permanently without using session state or 'in locals()', 
    # we display the output immediately after calculation inside the 'if' block:
    # ----------------------------

    if matches.empty:
        st.markdown(
            "<p class='warning'>❌ Ingen träff – möjligt luft / icke-kondenserbara gaser</p>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<p class='success'>✅ Möjliga köldmedier:</p>",
            unsafe_allow_html=True
        )
        st.dataframe(matches.reset_index(drop=True))
    
    st.write("---")

    with st.container(key="info_box"):
        st.markdown("### 📊 pt-jämförelse (alla köldmedier)")
        st.dataframe(df.reset_index(drop=True))
        st.markdown("""
        **Viktigt:**
        - PT-metoden ger endast indikation
        - Blandningar och luft kan ge felvisning
        - Säker identifiering kräver köldmedieidentifierare
        """)

# Note: The original code had the output sections outside the button block. 
# Moving them inside this 'if' statement is the cleanest fix for the NameError. 
# The output will now only appear after the user clicks "Identifiera köldmedium".
