import streamlit as st
import yaml
from yaml.loader import SafeLoader
from hasher import Hasher
from datetime import datetime
from authenticate import Authenticate
from streamlit_option_menu import option_menu
import plotly.express as px
from db_fxn import *
    
# st.set_page_config(page_title="Thoho Funeral Services", page_icon="🐞", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
local_css("style.css")

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
        authenticator.logout('Logout', 'sidebar')

        st.title(f'Welcome back *{name}*')
        
        selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Visualization", "Data Manipulation"],
        icons=["pencil-fill", "bar-chart-fill", "bar-chart"],
        orientation="horizontal",
        )

# --- INPUT & SAVE PERIODS ---
        if selected == "Data Entry":
            # with st.expander('Principle member'):
            st.subheader('Principle member')
            col1,col2 = st.columns(2)
            id_photo = ""
            
            with col1:
                first_name = st.text_input("First name", value="Tebza")
                id_no = st.text_input("ID Number", value=1130125766082, max_chars=13)
                email = st.text_input("Email", value="tebza.mre@gmail.com")
                gender = st.selectbox("Gender", ('Male', 'Female','Transgender', 'Rather not say'))
                payment_date = st.date_input("Payment date").isoformat()
            
                
            with col2:
                last_name = st.text_input("last name", value="selepe")
                dob = st.date_input("Date of Birth")
                age = calculate_age(dob)
                phone_no = st.text_input("Mobile number", value='+27', max_chars=12)
                race = st.selectbox("Ethnecity", ('African', 'Colored', 'Indian', 'Asian', 'Other' 'White'))
                reminder_date = st.date_input("Reminder date").isoformat()
            st.markdown('---')
            st.subheader('Beneficiary/Next of kin')
            ben_col1,ben_col2, ben_col3 = st.columns(3)
            with ben_col1:
                beneficiary_names = st.text_input("Beneficiary's First and Last Names", value="kgomotso selepe")
            with ben_col2:
                beneficiary_phone = st.text_input("Beneficiary's contact number", value='+27', max_chars=12)
            with ben_col3:
                ben_relation = st.text_input(f"Relation with the principle member", key='beneficiary_relation')
        # with st.expander('Dependants & Beneficiaries'):
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

            if has_agreed is True:
                submit_button = st.button('submit', disabled=False, key='submit_client')
                if submit_button:
                    insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,id_photo,payment_method,beneficiary_names,beneficiary_phone,ben_relation,policy_type,policy_cover,policy_premium,payment_date,reminder_date,age,has_paid,dependents)
                    st.success('success')
                    st.balloons()
            else:
                submit_button = st.button('submit', disabled=True, key='submit_client')
        elif selected == "Data Visualization":
            selected_data = st.sidebar.selectbox('Selelct which data to filter', ('___', '📈 Existing Data', '🗃 New Data'))
            if selected_data == '📈 Existing Data':                
                city = st.sidebar.multiselect(
                    "Select the City:",
                    options=df["CITY"].unique(),
                    default=df["CITY"].unique()
                )

                policy_type = st.sidebar.multiselect(
                    "Select the Policy Type:",
                    options=df["POLICY_TYPE"].unique(),
                    default=df["POLICY_TYPE"].unique(),
                )

                policy_cover = st.sidebar.multiselect(
                    "Select the Policy Cover:",
                    options=df["POLICY_COVER"].unique(),
                    default=df["POLICY_COVER"].unique(),
                )

                gender = st.sidebar.multiselect(
                    "Select the Gender:",
                    options=df["GENDER"].unique(),
                    default=df["GENDER"].unique()
                )

                paid = st.sidebar.multiselect(
                    "Select the paid the month:",
                    options=df["HAS_PAID"].unique(),
                    default=df["HAS_PAID"].unique()
                )

                df_selection = df.query(
                    "HAS_PAID == @paid & POLICY_COVER == @policy_cover & POLICY_TYPE == @policy_type & GENDER == @gender"
                )
                
                st.title(":bar_chart: Existing Client Data")
                st.markdown("##")

                # TOP KPI's
                total_sales = int(df_selection["MONTHLY_PREMIUM"].sum())
                st.subheader("Estimated Total Premiums:")
                st.subheader(f"R {total_sales:,}")
                
                sales_by_product_line = (
                    df_selection.groupby(by=["POLICY_TYPE"]).sum()[["MONTHLY_PREMIUM"]].sort_values(by="MONTHLY_PREMIUM")
                )
                st.dataframe(sales_by_product_line)
                
                fig_product_sales = px.bar(
                    sales_by_product_line,
                    x="MONTHLY_PREMIUM",
                    y=sales_by_product_line.index,
                    orientation="h",
                    title="<b>Sales by Policy Type</b>",
                    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
                    template="plotly_white",
                )
                fig_product_sales.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=(dict(showgrid=True))
                )

                # left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
                st.plotly_chart(fig_product_sales, use_container_width=True)
                
                st.dataframe(sales_by_product_line)
                
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
if __name__ == "__main__":
    main()