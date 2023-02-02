import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit.components.v1 as components
from hasher import Hasher
from authenticate import Authenticate
from db_fxn import *

def read():
    df = pd.read_csv( 
        "data.csv"
    )

def main():
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
    # creating a login widget
    name, authentication_status, username = authenticator.login('Login', 'main')
    if authentication_status:
        authenticator.logout('Logout', 'main')
        st.write(f'Welcome *{name}*')
        st.title('Some content')
        tab1, tab2, tab3 = st.tabs(["existing clients", "insert new clients", "update client data"])
        
        with tab1:
            # st.table(show_existing_client_data())
            st.markdown('sdf')
        with tab2:
            # with st.form('client_form', clear_on_submit=True):
            id_photo = ""
            first_name = st.text_input("First name", value="Tebza", key='fn')
            last_name = st.text_input("last name", value="selepe", key='ln')
            dob = st.date_input("Date of Birth", key='dob')
            id_no = st.text_input("ID Number", value=1130125766082, max_chars=13, key='idNo')
            email = st.text_input("Email", value="tebza.mre@gmail.com", key='mail')
            phone_no = st.text_input("Mobile number", value='+27', max_chars=12, key='fone')
            gender = st.selectbox("Gender", ('Male', 'Female','Transgender', 'Rather not say'), key='gender')
            reminder_date = st.date_input("reminder date", key='reminder').isoformat()
            selected_id_photo_method = st.radio('Do you wish to upload an existing photo of your ID? or take a picture using camera?', ('Upload existing', 'Take a picture'))
            if selected_id_photo_method == 'Upload existing':
                uploaded_id_photo = st.file_uploader('Upload ID photo', key='id_foto')
            if uploaded_id_photo is not None:
                id_photo = uploaded_id_photo
            else:
                taken_id_photo = st.camera_input(label='Take a picture of the ID photo', key=None, help='picture must be clear, well lit and not cropped', on_change=None, args=None, kwargs=None, disabled=False)
            if taken_id_photo is not None:
                id_photo = taken_id_photo
            race = st.selectbox("Ethnecity", ('African', 'Colored', 'Indian', 'Asian', 'Other' 'White'), key='race')
            pay_date = st.date_input("Payment date", key='payDate').isoformat()
            st.markdown('---')
            beneficiary_names = st.text_input("Beneficiary's First and Last Names", value="kgomotso selepe")
            beneficiary_phone = st.text_input("Beneficiary's contact number", value='+27', max_chars=12)
            policy_type = st.radio("Policy type", ('Gold', 'Silver', 'Platinum'), horizontal=False)
            policy_cover = st.radio("Policy cover", ('single', 'family'))
            num_dependents = 0
            payment_method = st.radio("Payment method", ('Cash', 'SASSA','Direct-Bank'), horizontal=False)
            if policy_cover == 'family':
                num_dependents = st.slider("Number of Dependents", min_value=1, step=1, max_value=3, help='minimum of 1, maximum of 3 dependants')
            # st.markdown('---')
                dependents = []
                for i in range(num_dependents):
                    dependent_names = st.text_input(f"Dependent {i+1} Full Name")
                    dependent_id = st.text_input(f"Dependent {i+1} ID number", max_chars=13)
                    relation = st.text_input(f"Relation with member", key={i+1})
                    dependent_dob = st.date_input(f"Dependent {i+1} Date of Birth")
                    dependent_age = calculate_age(dependent_dob)
                    dependents.append({"name" : dependent_names ,"id" : dependent_id , "age" : dependent_age})
            policy_premium = calculate_policy_premium(policy_type, num_dependents)
                    
                    
            
        btn_submit = st.button('submit')
        if btn_submit:
            if insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,id_photo,payment_method,beneficiary_names,beneficiary_phone,policy_type,policy_cover,policy_premium,pay_date,reminder_date,dependents):
                st.success('success')
                st.balloons()
            else:
                st.warning('fail')
        with tab3:
            
            st.dataframe(filter_dataframe(df))
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
if __name__ == "__main__":
    main()