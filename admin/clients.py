import streamlit as st
import yaml
from yaml.loader import SafeLoader
from hasher import Hasher
from datetime import datetime
from authenticate import Authenticate
import plotly.express as px
from PIL import Image
from io import BytesIO
import time
from send_email import *
from db_fxn import *
import streamlit.components.v1 as components
from streamlit_toggle import st_toggle_switch
from streamlit_elements import dashboard
from streamlit_elements import elements, mui, html
import pandas as pd

from streamlit_login_auth_ui.widgets import __login__
import streamlit_book as stb

with st.container():
    st.title('Admin Dashboard')
    reg_tab, visual_tab, update_tab = st.tabs(["📊Capture Data", "👀Visualize Data", "✍️Update Data"])
    
    # with reg_tab:
    st.header('📊Register Clients')
    st.subheader('Principle member')
    
    col1,col2 = st.columns(2)
    if "photo" not in st.session_state:
        st.session_state["photo"]="not done"
        
    def change_photo_state():
        st.session_state["photo"]="done"
        
    id_photo = ""
    
    with col1:
        first_name = st.text_input("First name")
        id_no = st.text_input("ID Number", max_chars=13)
        email = st.text_input("Email")
        gender = st.selectbox("Gender", ('Male', 'Female','Transgender', 'Rather not say'))
        payment_date = st.date_input("Payment date").isoformat()
        image_file = st.camera_input(label='Take a picture of the ID photo' ,key=None, help='picture must be clear, well lit and not cropped', on_change=change_photo_state, args=None, kwargs=None, disabled=False)
    if image_file is not None:
        progress_bar = st.progress(0)
        for percent_bar in range(100):
            time.sleep(.05)
            progress_bar.progress(percent_bar+1)
        
        # Convert the image to bytes
        image_bytes = BytesIO(image_file.read())
    
        
    with col2:
        last_name = st.text_input("last name")
        dob = st.date_input("Date of Birth")
        phone_no = st.text_input("Mobile number", max_chars=12)
        race = st.selectbox("Ethnecity", ('African', 'Colored', 'Indian', 'Asian', 'Other' 'White'))
        reminder_date = st.date_input("Reminder date").isoformat()
        age = calculate_age(dob)
        if image_file is not None:
            progress_bar.progress(100)
            image = Image.open(image_bytes)
            st.image(image, caption="Uploaded image", use_column_width=True)
    address = st.text_area('Physical address', height=50)
    st.markdown('---')
    st.subheader('Beneficiary/Next of kin')
    ben_col1,ben_col2, ben_col3 = st.columns(3)
    with ben_col1:
        beneficiary_names = st.text_input("Beneficiary's First and Last Names")
    with ben_col2:
        beneficiary_phone = st.text_input("Beneficiary's contact number", max_chars=12)
    with ben_col3:
        ben_relation = st.text_input(f"Relation with the principle member", key='beneficiary_relation')

    st.subheader('Policy Cover/Type')
    pol_col1,pol_col2,pol_col3 = st.columns(3)
    with pol_col1: 
        policy_type = st.radio("Policy type", ('silver', 'gold', 'platinum'), horizontal=False)
    with pol_col2:
        policy_cover = st.radio("Policy cover", ('single', 'family'))
        num_dependents = 0
    with pol_col3:
        payment_method = st.radio("Payment method", ('Cash', 'SASSA','Direct-Bank'), horizontal=False)
    if policy_cover == 'family':
        num_dependents = st.number_input("Number of Dependents", min_value=1, step=1, max_value=6, help='maximum of 3 dependants, then extra charges for extended additional members')
            
    dependents = []
    dep_col1, dep_col2,dep_col3,dep_col4 = st.columns(4)

    for i in range(num_dependents):
        with dep_col1:
            dependent_names = st.text_input(f"Dependent {i+1} Full Name")
        with dep_col2:
            dependent_id = st.text_input(f"Dependent {i+1} ID number", max_chars=13)
        with dep_col3:
            relation = st.text_input(f"Relation with member", key={i+1})
        with dep_col4:
            dependent_dob = st.date_input(f"Dependent {i+1} Date of Birth")
        dependent_age = calculate_age(dependent_dob)
        dependents.append({"name" : dependent_names ,"id" : dependent_id , "age" : dependent_age, "relation": relation})

    policy_premium = calculate_premium(policy_type, policy_cover, age, num_dependents)
    
    sub1,sub2 = st.columns(2)
    
    with sub1:
        has_paid = st.checkbox('Has paid the amount due upon signup?', key='has_paid', help='Amount due today')
    with sub2:
        has_agreed = st.checkbox('Do you agree to our Terms & Conditions?', key='has_agreed_terms', help='TFS Tcs & Cs to be read out by the sales rep')

    with st.container():
        st.markdown(f"Pay Monthly Premium of :green[R{policy_premium}], maximum of 3 members, then additional **:red[R20 per member for extended family]** package.")
    if has_agreed is True:
        submit_button = st.button('submit', disabled=False, key='submit_client')
        if submit_button:
            insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,address,image_bytes.getvalue(),payment_method,beneficiary_names,beneficiary_phone,ben_relation,policy_type,policy_cover,policy_premium,payment_date,reminder_date,age,has_paid,dependents)
            st.success('success')
            st.balloons()
    else:
        submit_button = st.button('submit', disabled=True, key='submit_client')

