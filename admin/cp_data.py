import streamlit as st
import yaml
from yaml.loader import SafeLoader
from hasher import Hasher
from datetime import datetime
from authenticate import Authenticate
import plotly.express as px
from send_email import *
from db_fxn import *
import streamlit.components.v1 as components
from streamlit_toggle import st_toggle_switch
from streamlit_elements import dashboard
from streamlit_elements import elements, mui, html
import pandas as pd

st.title('Policy Numbers From Payment Booklets')
with st.expander('Entering Policy'):
    pn = st.text_input('enter policy number', key='picked policy_nos')
    btn_submit = st.button('Add', type='primary')
    
    if btn_submit:
        if enter_cpp(pn):
            st.success('Entered')
            st.balloons()
        else:
            st.warning('Error Policy number already exists')


# with st.expander('Captured Poilcies'):
#     st.write()