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
from streamlit_extras import *
from streamlit_elements import dashboard
from streamlit_elements import elements, mui, html
import pandas as pd
from streamlit_login_auth_ui.widgets import __login__
import streamlit_book as stb
import streamlit.components.v1 as stc
py_script =   """
                <script defer src="https://pyscript.net/latest/pyscript.js"></script>
                <link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
                """
                
def main():
    
    # stc.html(py_script,width=0)
        
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    
    # hashed_passwords = Hasher(['xxx', 'xxx']).generate()
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Creating the authenticator object
    authenticator = Authenticate(
        config['credentials'],
        config['cookie']['name'], 
        config['cookie']['key'], 
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    local_css("style.css")
    # creating a login widget
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        st.sidebar.subheader(f'Welcome back *{name}*')
        stb.set_book_config(
                menu_title=None,
                menu_icon="admin",
                options=[
                    "Dashboard",
                    "Clients",
                    "Employees",
                    "Cherry Picked",
                    ], 
                paths=[
                    "admin/dash.py",
                    "admin/clients.py",
                    "admin/employees.py",
                    "admin/cp_data.py"
                    ],
                save_answers=False,
                styles={
                    "nav-link": {"--hover-color": "#fde8ec"},
                    "nav-link-selected": {"background-color": "#862933"},
                    "nav-link": {"background": "0 0"}
                }
        )
        authenticator.logout('Logout', 'sidebar')
        
            
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
if __name__ == "__main__":
    # st.set_page_config(layout="wide")
    header_left,header_mid,header_right = st.columns([3,3,3],gap='small')
    with header_mid:
        st.image('images/logo.png', width=200)
    main()