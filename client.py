import datetime
import streamlit as st
from db_fxn import *
from streamlit_option_menu import option_menu


selected = option_menu(
    menu_title=None,
    options=["Data Entry", "Data Visualization", "Data Manipulation"],
    icons=["pencil-fill", "bar-chart-fill", "bar-chart"],
    orientation="horizontal",
)

# --- INPUT & SAVE PERIODS ---
if selected == "Data Entry":

    with st.expander('Principle member', expanded=True):
        col1,col2 = st.columns(2)
        id_photo = ""
        
        with col1:
            first_name = st.text_input("First name", value="Tebza")
            id_no = st.text_input("ID Number", value=1130125766082, max_chars=13)
            email = st.text_input("Email", value="tebza.mre@gmail.com")
            gender = st.selectbox("Gender", ('Male', 'Female','Transgender', 'Rather not say'))
            start_date = st.date_input("Start date").isoformat()
        selected_id_photo_method = st.radio('Do you wish to upload an existing photo of your ID? or take a picture using camera?', ('Upload existing', 'Take a picture'))
        if selected_id_photo_method == 'Upload existing':
            uploaded_id_photo = st.file_uploader('Upload ID photo')
            if uploaded_id_photo is not None:
                id_photo = uploaded_id_photo
        else:
            taken_id_photo = st.camera_input(label='Take a picture of the ID photo', key=None, help='picture must be clear, well lit and not cropped', on_change=None, args=None, kwargs=None, disabled=False)
            if taken_id_photo is not None:
                id_photo = taken_id_photo
            
        with col2:
            last_name = st.text_input("last name", value="selepe")
            dob = st.date_input("Date of Birth")
            phone_no = st.text_input("Mobile number", value='+27', max_chars=12)
            race = st.selectbox("Ethnecity", ('African', 'Colored', 'Indian', 'Asian', 'Other' 'White'))
            payment_date = st.date_input("Payment date").isoformat()
        st.markdown('---')
        ben_col1,ben_col2 = st.columns(2)
        with ben_col1:
            beneficiary_names = st.text_input("Beneficiary's First and Last Names", value="kgomotso selepe")
        with ben_col2:
            beneficiary_phone = st.text_input("Beneficiary's contact number", value='+27', max_chars=12)

with st.expander('Dependants & Beneficiaries'):
    pol_col1,pol_col2,pol_col3 = st.columns(3)
    with pol_col1: 
        policy_type = st.radio("Policy type", ('Gold', 'Silver', 'Platinum'), horizontal=False)
    with pol_col2:
        policy_cover = st.radio("Policy cover", ('single', 'family'))
    num_dependents = 0
    with pol_col3:
        payment_method = st.radio("Payment method", ('Cash', 'SASSA','Direct-Bank'), horizontal=False)
    if policy_cover == 'family':
            num_dependents = st.slider("Number of Dependents", min_value=1, step=1, max_value=3, help='minimum of 1, maximum of 3 dependants')
        
st.markdown('---')
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
    dependents.append({"name" : dependent_names ,"id" : dependent_id , "age" : dependent_age})
policy_premium = calculate_premium(policy_type, num_dependents)