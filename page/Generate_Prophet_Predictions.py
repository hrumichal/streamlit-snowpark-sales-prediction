import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

from snowflake.snowpark import Session
from snowflake.snowpark.functions import udf, col, lit, is_null, iff, initcap
from src.settings import ACCURACY_MONITORING_TAB
from src.helpers import prophetize
from src.helpers import push_to_keboola
from datetime import datetime

def getPage():  
    colSpanLeft,colFilter,colContent,colSpanRight=st.columns([1,28,120,4])
    with colFilter:
        if 'authentication_status' not in st.session_state:
            login.getPage()

        # st.title("Generate Prediction")    
        
        # Get user inputs
        with st.expander('Filters',expanded=True):
            category = st.selectbox("Enter category", ['Takeaway', 'Eat In'])
            meal = st.selectbox("Enter meal", ['lunch', 'dinner'])
            prediction_period = st.number_input("Enter prediction period (in days)", min_value=1, value=30)
        # training_start_date = st.date_input("Enter training start date")
        # training_start_date = st.text_input("Enter training start date")
        # formatted_date = training_start_date.strftime("%Y-%m-%d")

    with colContent:
        if st.button("Generate Plot"):
            if category and meal and prediction_period:
                prophet = prophetize(ACCURACY_MONITORING_TAB, category, meal, prediction_period)

                # Pivot the DataFrame
                pivot_df = prophet.pivot(index='D', columns='ID', values='Y')

                # Plotting the line chart
                plt.figure(figsize=(8, 4))

                for group, data in pivot_df.items():
                    plt.plot(data.index, data.values, label=group)

                plt.xlabel('Date')
                plt.ylabel('Cnt Orders')
                plt.title('Line Chart of Order Counts for Dates and Category')
                plt.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()

                # Display the chart
                st.pyplot(plt)


        if st.button("Submit predictions to Keboola"):
            message_placeholder = st.empty()
            prophet = prophetize(ACCURACY_MONITORING_TAB, category, meal, prediction_period)
            message_placeholder.text('Sending data to Keboola...')
            destination = '"current_predictions"'
            push_to_keboola(prophet, destination)
            message_placeholder.text('Done! Your data is ready in ' + destination + ' table.')