#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 16 15:01:11 2023

@author: ondrejsvoboda
"""

import streamlit as st
import datetime

from streamlit_extras.switch_page_button import switch_page
from src.helpers import read_df, create_summary_table
from src.settings import ACCURACY_MONITORING_TAB
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode,GridUpdateMode
import Login as login


def getNbRenderer(prefix="",suffix="", black='no',arr=0):
    rd = f'''
    class TotalValueRenderer {{
        init(params) {{
            var black="{black}";
            var color='red';
            if(params.value<=4)
                color="green";
            if(params.value>4 && params.value<4.5)
                color="#ffc700";  
            if (black=="yes"){{
                color="black"
            }}    
            this.eGui = document.createElement('div');
            this.eGui.innerHTML = `
                <span>
                    <span style="color:${{color}}" class="my-value"></span>
                </span>`;

            this.eValue = this.eGui.querySelector('.my-value');
            this.cellValue = this.getValueToDisplay(params);
            this.eValue.innerHTML = this.cellValue;
        }}

        getGui() {{
            return this.eGui;
        }}

        refresh(params) {{
            this.cellValue = this.getValueToDisplay(params);
            this.eValue.innerHTML = this.cellValue;
            return true;
        }}
        destroy() {{
            if (this.eButton) {{
                this.eButton.removeEventListener('click', this.eventListener);
            }}
        }}

        getValueToDisplay(params) {{
            var v=parseFloat(params.value).toFixed({arr});
            if({arr}>0){{
                return "{prefix}" + parseFloat(v).toFixed({arr}).toLocaleString('en-US', {{maximumFractionDigits:2}})+"{suffix}"
            }}
            return "{prefix}" + parseFloat(v).toLocaleString('en-US', {{maximumFractionDigits:2}})+"{suffix}"
        }}
    }}'''
    return JsCode(rd) 

def getTable(df,key):
    
    ob = GridOptionsBuilder.from_dataframe(df)
    ob.configure_column("cat_mean", header_name='CATEGORY',pinned='left') #CHECK ANGULAR DOC
    for (columnName, columnData) in df.iteritems():
        if columnName!='cat_mean':
            ob.configure_column(columnName, header_name=columnName.replace('mape_',' ').replace("_"," ").upper(),rowGroup=False,hide= False,cellRenderer=getNbRenderer(suffix='%',arr=2))
    ob.configure_grid_options(suppressAggFuncInHeader = True)
    custom_css = {
        ".ag-header":{
            "border":"0px",
            "border-radius":"8px"
        },
        '.ag-header-cell-label': {
            "justify-content": "center",
            'text-align': 'center!important'
        },
        '.ag-cell-value:not([col-id="ag-Grid-AutoColumn"])' :{
            'text-align': 'center!important'
        },
        '.ag-cell-value[col-id="cat_mean"]' :{
            'text-align': 'left!important'
        },
        ".ag-row-level-1 .ag-group-expanded, .ag-row-level-1 .ag-group-contracted":{
            "display":"none!important",
        },
        ".ag-watermark":{
            "display":"none!important"
        },
        ".ag-root-wrapper":{
            "border":"0px"
            #  "margin-top":"2px",
            #  "border-bottom": "2px",
            #  "border-bottom-color": "#b9b5b5",
            #  "border-bottom-style": "double"
             }
        }
    gripOption=ob.build()
    AgGrid(df,gripOption, enable_enterprise_modules=True,fit_columns_on_grid_load=True,height=654,custom_css=custom_css,allow_unsafe_jscode=True, update_mode=GridUpdateMode.NO_UPDATE,key=key)

def color_negative_red(value):
  """
  Colors elements in a dateframe
  green if positive and red if
  negative. Does not color NaN
  values.
  """

  if value < 15:
    color = 'green'
  elif value > 0:
    color = 'red'
  else:
    color = 'black'

  return 'color: %s' % color

def getPage():

    df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col = "ds")
    colSpanLeft,colFilter,colContent,colSpanRight=st.columns([1,28,120,4])
    with colFilter:
        with st.expander("Filters",expanded=True):
            if "start_date" in st.session_state:
                value = st.session_state["start_date"]
            else:
                value = df_accuracy.ds.min().date()
            start_date = st.date_input("Start Date", 
                                        value=value,
                                        min_value=df_accuracy.ds.min().date(), 
                                        max_value=df_accuracy.ds.max().date()
                                        )
            st.session_state["start_date"] = start_date

            if "end_date" in st.session_state:
                value = st.session_state["end_date"]
            else:
                value = df_accuracy.ds.max().date()

            end_date = st.date_input("End Date", 
                                        value=value,
                                        min_value=start_date, 
                                        max_value=df_accuracy.ds.max().date()
                                        )
    with colContent:
        

        # we need to include the last date of selection
        end_date = end_date + datetime.timedelta(days=1)
        summary_df = create_summary_table(df_accuracy, str(start_date), str(end_date))

        st.markdown("### Mean Average Percentage Error (MAPE) over defined period")

        t1, t2 = st.tabs(["Summary", "Detailed"])

        summary_df['cat_mean'] = summary_df.index
        cols = ["cat_mean","prophet_mean", "lgbm_mean", "rf_mean"]

        with t1:
            # st.dataframe(summary_df[cols].style.applymap(color_negative_red).format('{:.2f} %'))
            getTable(summary_df[cols],'simple')

        with t2:
            cols = [c for c in summary_df.columns if not c.endswith("_mean")]
            cols.insert(0,'cat_mean')
            # st.dataframe(summary_df[cols].style.applymap(color_negative_red).format('{:.2f} %'))
            getTable(summary_df[cols],'detailled')






