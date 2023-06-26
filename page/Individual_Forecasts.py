import streamlit as st
from src.settings import ACCURACY_MONITORING_TAB
from src.graphs import preprocess_data, create_series_plot_new
from src.graphs import filter_by_date
from src.helpers import read_df, calculate_categories
from src.helpers import MAPE
import pandas as pd
import Login as login
import datetime
from streamlit_kpi import streamlit_kpi
import numbers

def getCard(text,val,icon, key,compare=False,titleTextSize="11vw",content_text_size="7vw",unit="%",height='150',iconLeft=90,iconTop=95,backgroundColor='#ffffff', animate=True, progressValue=100 ):
    pgcol='green'
    if isinstance(val, numbers.Number):
        if val<0:
            pgcol='red'
    if compare==False:
        pgcol='darkgrey'
    if compare==False:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,unit=unit,iconLeft=iconLeft,showProgress=False,iconTop=iconTop,backgroundColor=backgroundColor, animate=animate, borderSize='1px')
    else:
        streamlit_kpi(key=key+"_n",height=height,title=text,value=val,icon=icon,progressValue=progressValue,unit=unit,iconLeft=iconLeft,showProgress=True,progressColor=pgcol,iconTop=iconTop,backgroundColor=backgroundColor, animate=animate, borderSize='1px')  


def getPage():
    colSpanLeft,colFilter,colContent,colSpanRight=st.columns([1,28,120,4])
    if 'authentication_status' not in st.session_state:
            login.getPage()

    # if st.session_state["authentication_status"]:
    #df_meals = read_df(ACCURACY_MONITORING_MEALS_TAB, date_col=["approximate_timestamp"])
    df_accuracy = read_df(ACCURACY_MONITORING_TAB, date_col="ds")
    df_accuracy["metric_actual"] = df_accuracy["metric_actual"].apply(int)
    df_accuracy["metric_forecast"] = df_accuracy["metric_forecast"].apply(float)
    df_accuracy["metric_forecast_lgbm"] = df_accuracy["metric_forecast_lgbm"].apply(float)
    df_accuracy["metric_forecast_rf"] = df_accuracy["metric_forecast_rf"].apply(float)
    #df_actuals = read_df(ACTUALS_NONAGG_TAB, date_col=["ds"])
    cat1, cat2, cat3 = calculate_categories(df_accuracy)
    
    # with st.sidebar:
    
        
    if "start_date" in st.session_state:
        stdatevalue = st.session_state["start_date"]
    else:
        stdatevalue = df_accuracy.ds.min().date()
    if "end_date" in st.session_state:
        endatevalue = st.session_state["end_date"]
    else:
        endatevalue = df_accuracy.ds.max().date()   
    with colFilter:
        with st.expander('Filters',expanded=True):
            category_type = st.selectbox("Category Type", cat1,key='cat1')
            outlet_type = st.selectbox("Outlet Type", cat2,key='cat2')
            outlet_number = st.selectbox("Outlet Number", cat3,key='cat3')
            category_selected = '~'.join([category_type, outlet_type, outlet_number])
            accu_preprocessed = preprocess_data(df_accuracy, category_selected, time_col='ds')
            
            start_date = st.date_input("Start Date", 
                                            value=stdatevalue,
                                            min_value=accu_preprocessed.dt.min().date(), 
                                            max_value=accu_preprocessed.dt.max().date()
                                            )
            st.session_state["start_date"] = start_date
            end_date = st.date_input("End Date", 
                                            value=endatevalue,
                                            min_value=stdatevalue, 
                                            max_value=accu_preprocessed.dt.max().date()
                                            )
        st.session_state["end_date"] = end_date    

            

        start_date = pd.to_datetime(start_date)
        # we need to include the last date of selection

        end_date = end_date + datetime.timedelta(days=1)
        end_date = pd.to_datetime(end_date)     
        #meals_preprocessed_filtered = filter_by_date(meals_preprocessed, start_date, end_date)
        accu_preprocessed_filtered = filter_by_date(accu_preprocessed, start_date, end_date)

        # 1. aggregate by category, date and meal_category
        group_cols = ["category", "date", "meal_category"]
        agg_cols = ["metric_actual", "metric_forecast", "metric_forecast_lgbm", "metric_forecast_rf"]
        accu_preprocessed_filtered_agg = accu_preprocessed_filtered.groupby(group_cols)[agg_cols].sum().reset_index()
        
        #st.write(accu_preprocessed_filtered_agg)
        # 2. calculate MAPE
        mape_pallet_prophet = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_forecast)

        mape_pallet_lgbm = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_forecast_lgbm)

        mape_pallet_rf = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='pallet'].metric_forecast_rf)

        mape_package_prophet = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_forecast)

        mape_package_lgbm = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_forecast_lgbm)

        mape_package_rf = MAPE(accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_actual, 
                                accu_preprocessed_filtered_agg.loc[accu_preprocessed_filtered_agg.meal_category=='package'].metric_forecast_rf)


        #if meals_preprocessed_filtered.empty:
        #    st.warning("No data for available for the selection.")
        #    st.stop()
        
        if accu_preprocessed_filtered.empty:
            st.warning("No data for available for the selection.")
            st.stop()

    with colContent:
        with st.container():
            coltl,coltr=st.columns(2)
            with coltl:
                st.markdown("### MAPE (pallet):")
                st.markdown("(Mean Average Percentage Error)")
                       
            with coltr:
                st.markdown("### MAPE (package):")
                st.markdown("(Mean Average Percentage Error)")

            col1, col2,col3,col4,col5,col6 = st.columns(6)

            col11, col12, col13 = st.columns(3)
            with col1:
                hg = 130
                getCard(f'''Prophet {f"{mape_pallet_prophet:.2f} %"}''',15-mape_pallet_prophet,'fa-brands fa-meta',key='one',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)
            with col2:
                getCard(f'''LightGBM {f"{mape_pallet_lgbm:.2f} %"}''',15-mape_pallet_lgbm,'fa fa-sitemap',key='tw',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)
            with col3:
                getCard(f'''RndForest {f"{mape_pallet_rf:.2f} %"}''',15-mape_pallet_rf,'fa fa-tree',key='thr',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)
     
            

            with col4:
                getCard(f'''Prophet {f"{mape_package_prophet:.2f} %"}''',15-mape_package_prophet,'fa-brands fa-meta',key='fr',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)
            with col5:
                getCard(f'''LightGBM {f"{mape_package_lgbm:.2f} %"}''',15-mape_package_lgbm,'fa fa-sitemap',key='fv',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)
            with col6:
                getCard(f'''RndForest {f"{mape_package_rf:.2f} %"}''',15-mape_package_rf,'fa fa-tree',key='six',height=hg,unit='%',progressValue=15 - mape_pallet_prophet,compare=True)


        #with col1:
        #figure, raw_data = st.tabs(["figure", "raw_data"])
        
        fig0 = create_series_plot_new(accu_preprocessed_filtered)
        fig0.update_layout(height=570)
        st.plotly_chart(fig0, use_container_width=True, theme="streamlit")
        
        with colFilter:
            with st.form("my_form"):
                        selectbox = st.selectbox("Select default model", ["Prophet", "LightGBM", "Random Forest"])
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            st.warning("Done! Selected model will be used in next run.") 
   

        
    
    
    
    
