import streamlit as st

import pandas as pd
from datetime import date


stripe_file = st.file_uploader(
    "Choose the Stripe file"
)

odoo_file = st.file_uploader(
    "Choose the Odoo file"
)



def stripe_sub_details(file):
    # Load the CSV file
    df = pd.read_csv(file, parse_dates=["Ended At (UTC)", "Start Date (UTC)"])

    # Define the mapping for the status column
    status_mapping = {
        "past_due": "active",
        "incomplete_expired": "canceled"
    }
    df["Status"] = df["Status"].replace(status_mapping)

    # Extract month and year for grouping
    df["End-Month"] = df["Ended At (UTC)"].dt.to_period("M")
    df["Start-Month"] = df["Start Date (UTC)"].dt.to_period("M")

    # Count New Subscriptions based on Start Date (UTC)
    new_subscriptions = df.groupby("Start-Month").size().rename("New Subscriptions")
    # print(new_subscriptions)

    # Count Canceled Subscriptions
    canceled_subscriptions = df.groupby("End-Month").size().rename("Canceled Subscriptions")
    # print(canceled_subscriptions)

    # Calculate Active Subscriptions
    def count_active_subscriptions(df, period):
        return ((df["Start-Month"] <= period) & (df["End-Month"] >= period)).sum()

    active_subscriptions = pd.Series(
        {period: count_active_subscriptions(df, period) for period in df["End-Month"].sort_values().unique()},
        name="Active Subscriptions"
    )

    # Combine into a final report
    report = pd.concat([new_subscriptions, canceled_subscriptions, active_subscriptions], axis=1).fillna(0).astype(int)
    report = report.rename_axis('Month')

    # Save the summary table
    # report.to_csv("stripe_summary.csv")

    return report

def odoo_sub_details(file):

    df = pd.read_csv(file, parse_dates=["End Date", "Start Date"])
    df.iloc[:, :-1] = df.iloc[:, :-1].ffill()

    df["End-Month"] = df["End Date"].dt.to_period("M")
    df["Start-Month"] = df["Start Date"].dt.to_period("M")

    # Count New Subscriptions based on Start Date (UTC)
    new_subscriptions = df.groupby("Start-Month").size().rename("New Subscriptions")
    # print(new_subscriptions)

    # Count Canceled Subscriptions
    canceled_subscriptions = df.groupby("End-Month").size().rename("Canceled Subscriptions")
    # print(canceled_subscriptions)

    # Calculate Active Subscriptions
    def count_active_subscriptions(df, period):
        return ((df["Start-Month"] <= period) & (df["End-Month"] >= period)).sum()

    active_subscriptions = pd.Series(
        {period: count_active_subscriptions(df, period) for period in df["End-Month"].sort_values().unique()},
        name="Active Subscriptions"
    )

    # Combine into a final report
    report = pd.concat([new_subscriptions, canceled_subscriptions, active_subscriptions], axis=1).fillna(0).astype(int)
    report = report.rename_axis('Month')

    # Save the summary table

    final_end_month = pd.Period(date.today(), freq='M')
    report = report[report.index<=final_end_month]
    # report.to_csv("odoo_summary.csv")
    return report

if st.button('Get Report'):
    @st.cache_data
    def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode("utf-8")

    csv = convert_df(stripe_sub_details(stripe_file).add(odoo_sub_details(odoo_file), fill_value=0))

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="summary.csv",
        mime="text/csv",
    )
