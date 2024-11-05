import streamlit as st
import pandas as pd
import time
import talabat


# Different ways to use the API
uploaded_file = st.file_uploader(
    "Choose a CSV file"
)

if uploaded_file is not None:
    talabat.process_and_send_stock(uploaded_file)


