import streamlit as st
import pandas as pd
import time
import talabat


# Different ways to use the API
uploaded_file = st.file_uploader(
    "Choose a CSV file"
)

if uploaded_file is not None:
    
    with st.spinner(text="In progress..."):
        time.sleep(5)
        talabat.process_and_send_stock(uploaded_file)
        # dataframe = pd.read_csv(uploaded_file)

    # st.write(dataframe)


st.session_state.processed = False
if st.button('Do Something'):
    pass
    with st.spinner(text="In progress..."):
        time.sleep(5)
    # st.session_state.processed = True
    st.write('Done!')
