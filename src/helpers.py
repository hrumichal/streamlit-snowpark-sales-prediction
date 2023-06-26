#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 13:12:30 2023

@author: ondrejsvoboda
"""

import streamlit as st
from src.settings import snowpark_session
import pandas as pd
import numpy as np

def parse_credentials():
    config_dict = {}
    
    # 1. check the longest inner subscription
    
    # at this point, I do not check for preauthorized or cookies
    for key in st.secrets:
        if 'credentials' in key:
            creds_dict = config_dict.get("credentials", dict())
            username_dict = creds_dict.get("usernames", dict())    
            username = key.split('_')[-2]
            key_end = key.split('_')[-1]
            user_dict =  username_dict.get(username, dict())
            user_dict[key_end] = st.secrets[key]
            username_dict[username] = user_dict
            creds_dict["usernames"] = username_dict
            config_dict["credentials"] = creds_dict
    
    config_dict["cookie"] = {'expiry_days':0,
                             'key':"random_signature_key",
                             'name':"random_cookie_name"}
    
    config_dict["preauthorized"] = {'emails':["melsby@gmail.com"]}
    
    return config_dict

def MAPE(Y_actual,Y_Predicted):
    """
    Calculates mean average percentage error

    Parameters
    ----------
    Y_actual : 
        array of actuals.
    Y_Predicted : 
        array of forcasted data

    Returns
    -------
    mape : float
        returns the value of the metric.

    """
    mape = np.mean(np.abs((Y_actual - Y_Predicted)/Y_actual))*100
    return mape    

@st.cache_data
def read_df(table_id, index_col=None, date_col=None):
    # keboola_client.tables.export_to_file(table_id, '.')
    table = snowpark_session.table(table_id)
    # table_name = table_id.split(".")[-1]
    #return pd.read_csv(table_name, index_col=index_col, parse_dates=date_col)
    table = table.to_pandas()
    table[date_col] = pd.to_datetime(table[date_col])
    return table

@st.cache_data
def prophetize(dataframe, category, meal, prediction_period):    
    output = snowpark_session.sql('with data as (select "category_2" AS "Category", "date"::date AS "Date", sum("metric_actual"::number) AS "Value" from ' + dataframe + ' WHERE "category_2" = \''+ category + '\' and "meal_category"=\'' + meal +  '\' GROUP BY "category_2", "date") select p.* from data, table(prophetize_daily("Category", "Value", "Date", ' + str(prediction_period) + ') over (partition by "Category")) p;')
    df = output.to_pandas()
    df['D'] = pd.to_datetime(df['D'])
    return df

@st.cache_data
def push_to_keboola(source_pandas_df, destination):
    df = snowpark_session.create_dataframe(source_pandas_df)
    df.write.mode("overwrite").save_as_table(destination)

@st.cache_data
def calculate_categories(original_dataframe):
    split_series = original_dataframe.category.str.split('~', expand=True)
    cat1 = split_series[0].unique()
    cat2 = split_series[1].unique()
    cat3 = split_series[2].unique()
    return cat1, cat2, cat3

@st.cache_data
def group_accuracy_df(dataframe):
    dataframe["metric_actual"] = dataframe["metric_actual"].apply(int)
    dataframe["metric_forecast"] = dataframe["metric_forecast"].apply(float)
    dataframe["metric_forecast_lgbm"] = dataframe["metric_forecast_lgbm"].apply(float)
    dataframe["metric_forecast_rf"] = dataframe["metric_forecast_rf"].apply(float)
    dfgrouped = dataframe.groupby(["date", "category", "meal_category"])[["metric_actual", "metric_forecast", "metric_forecast_lgbm", "metric_forecast_rf"]].sum().reset_index()
    dfgrouped["APE_prophet"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast"])/dfgrouped["metric_actual"])
    dfgrouped["APE_lgbm"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast_lgbm"])/dfgrouped["metric_actual"])
    dfgrouped["APE_rf"]= np.abs((dfgrouped["metric_actual"] - dfgrouped["metric_forecast_rf"])/dfgrouped["metric_actual"])
    return dfgrouped

def create_summary_table(dataframe, start_date, end_date):
    dfgrouped = group_accuracy_df(dataframe)
    df_filtered = dfgrouped.loc[(dfgrouped.date>=start_date) & (dfgrouped.date<=end_date)]

    cols = ["metric_actual", 
        "APE_prophet", 
        "APE_lgbm", 
        "APE_rf"
       ]

    dff_grouped = df_filtered.groupby(["category", "meal_category"])[cols]
    summary_df = dff_grouped.agg(
        mape_prophet = pd.NamedAgg(column="APE_prophet", aggfunc="mean"),
        mape_lgbm = pd.NamedAgg(column="APE_lgbm", aggfunc="mean"),
        mape_rf = pd.NamedAgg(column="APE_rf", aggfunc="mean"),
        ).reset_index()
    
    summary_df["mape_prophet"] = 100 * summary_df["mape_prophet"]
    summary_df["mape_lgbm"] = 100 * summary_df["mape_lgbm"]
    summary_df["mape_rf"] = 100 * summary_df["mape_rf"]
    
    summary_df.pivot(columns=["meal_category"], index=["category"])
    summary_pivot_df = summary_df.pivot_table(columns=["meal_category"], index=["category"])
    colnames = ['_'.join([c1, c2]) for c1, c2 in summary_df.pivot_table(columns=["meal_category"], index=["category"]).columns]
    summary_pivot_df.columns=colnames
    summary_pivot_df["prophet_mean"] = (summary_pivot_df["mape_prophet_pallet"] + summary_pivot_df["mape_prophet_package"]) / 2
    summary_pivot_df["lgbm_mean"] = (summary_pivot_df["mape_lgbm_pallet"] + summary_pivot_df["mape_lgbm_package"]) / 2
    summary_pivot_df["rf_mean"] = (summary_pivot_df["mape_rf_pallet"] + summary_pivot_df["mape_rf_package"]) / 2
    
    summary_pivot_df.sort_values(by="prophet_mean", inplace=True)


    return summary_pivot_df














