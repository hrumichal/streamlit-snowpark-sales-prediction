import hydralit_components as hc
import page.Accuracies as ac
import page.Individual_Forecasts as ind
import page.Generate_Prophet_Predictions as gen
import Login as login
import streamlit as st
from ui import setUI
from PIL import Image

st.set_page_config(
    page_title="Model Dashboard",
    page_icon="🍕",
    layout="wide",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
setUI()

def init():
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"]=""   
    if st.session_state["authentication_status"]!=True:
        login.getPage()
        return
    # image = Image.open('streamlit.png')

    col1,col2=st.columns([1,5])
    st.image('https://alteirac.com/st.svg?t=t',width=100)
    menu_data = [
        {'id':'accu','icon':"fas fa-map-signs",'label':"Models Accuracy"},
        {'id':'forecast','icon':"fab fa-buysellads",'label':"Forecast"},
        {'id':'prophet','icon':"fas fa-sliders-h",'label':"Prophet Predictions"},
        # {'id':'login','icon':"fab fa-battle-net",'label':"Login"}

    ]

    over_theme = {'txc_active':'#5d5d5d','txc_inactive': '#adadad', 'menu_background':'#f0f2f6'}#'#f0f2f6'

    page = hc.nav_bar(
        menu_definition=menu_data,
        override_theme=over_theme,
        hide_streamlit_markers=False, 
        sticky_nav=True, 
        login_name='Logout',
        sticky_mode='pinned', 
    )
  
    if page == "Logout":
        del st.session_state["authentication_status"]
        login.getPage()  

    if page == 'accu':
        ac.getPage()    
    if page == 'forecast':
        ind.getPage() 
    if page == "prophet":
        gen.getPage()  

init()       

