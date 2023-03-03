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

tab1, tab2 = st.tabs(["Register Employee", "Update Employee Data"])

with st.form('employee_form'):
    col1,col2 = st.columns(2)
    with col1:
        first_name = st.text_input("First Name")
        password = st.text_input('Password', type="password")
        role = st.selectbox("role", ('--PLEASE SELECT---','Receptionist', 'Driver', 'Manager', 'Admin','Sound Engeneer', 'Undertaker'))
    with col2:
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        status = st.selectbox('Status',('--PLEASE SELECT---','Active', 'Suspended', 'Inactive'))
    submit = st.form_submit_button('Add', type="primary", use_container_width=True)

if submit:
    emp_id = generate_employee_id()
    hashed_pss = Hasher(password.encode())
    print(hashed_pss)
    register_employee(emp_id,first_name,last_name,email,password,role,status)
    st.balloons()