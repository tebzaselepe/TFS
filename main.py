import streamlit as st
import yaml
from yaml.loader import SafeLoader
from hasher import Hasher
from datetime import datetime
from authenticate import Authenticate
from streamlit_option_menu import option_menu
import plotly.express as px
from send_email import *
from db_fxn import *
    



def main():
    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    local_css("style.css")
    
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

        # st.title(f'Welcome back *{name}*')
        header_left,header_mid,header_right = st.columns([1,2,1],gap='large')
        
        with st.container():
            st.title('Thoho Admin Dashboard')

        selected = option_menu(
        menu_title=None,
        options=["Data Entry", "Data Visualization", "Edit Data"],
        icons=["pencil-fill", "bar-chart-fill", "bar-chart"],
        orientation="horizontal",
        )

        # --- REGISTER NEW CLIENT --- #
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
            address = st.text_area('Physical address', height=50)
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
                    insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,address,id_photo,payment_method,beneficiary_names,beneficiary_phone,ben_relation,policy_type,policy_cover,policy_premium,payment_date,reminder_date,age,has_paid,dependents)
                    st.success('success')
                    st.balloons()
            else:
                submit_button = st.button('submit', disabled=True, key='submit_client')
        # --- VIEW DATA --- #
        elif selected == "Data Visualization":
            selected_data = st.sidebar.selectbox('Selelct which data to filter', ('📈 Existing Data', '🗃 New Data'))
            if selected_data == '📈 Existing Data':  
                df = db_to_pd()
                with st.sidebar:
                    Policy_filter = st.multiselect(label= 'Select The Policy Type',
                                                options=df['POLICY_TYPE'].unique(),
                                                default=df['POLICY_TYPE'].unique())

                    Policy_Status_filter = st.multiselect(label='Select Policy Status',
                                            options=df['POLICY_STATUS'].unique(),
                                            default=df['POLICY_STATUS'].unique())

                    Payment_Method_filter = st.multiselect(label='Select Policy Method',
                                            options=df['PAY_METHOD'].unique(),
                                            default=df['PAY_METHOD'].unique())
                    
                    Gender_filter = st.multiselect(label='Select Gender Group',
                                            options=df['GENDER'].unique(),
                                            default=df['GENDER'].unique())
                    
                    Has_Paid_filter = st.multiselect(label='Select has paid filter',
                                            options=df['HAS_PAID'].unique(),
                                            default=df['HAS_PAID'].unique())

                df1 = df.query('HAS_PAID == @Has_Paid_filter & GENDER == @Gender_filter & PAY_METHOD == @Payment_Method_filter & POLICY_STATUS == @Policy_Status_filter & POLICY_TYPE == @Policy_filter')    
                    
                
                total_premuims = float(df1['MONTHLY_PREMIUM'].sum())
                total_clients = int(df1['POLICY_TYPE'].count())
                total_active = df1['POLICY_STATUS'].value_counts().get('active', 0)
                total_inactive = df1['POLICY_STATUS'].value_counts().get('canceled', 0)
                total_unkown = total_clients - total_active - total_inactive
                
                total1,total2,total3 = st.columns(3,gap='large')

                with total1:
                    st.image('images/hand.png',use_column_width='Auto')
                    st.metric(label = 'Total Premiums', value= (f"R{total_premuims}"))
                
                with total2:
                    st.image('images/conversion.png',use_column_width='Auto')
                    st.metric(label = 'Total Clients', value= (total_clients))
                
                with total3:
                    st.image('images/impression.png',use_column_width='Auto')
                    st.metric(label = 'Total Active', value= (total_active))
                    st.metric(label = 'Total inactive', value= (total_inactive))
                    st.metric(label = 'Total unkown', value= (total_unkown))
                    
                df_selection = df.query(
                    " POLICY_TYPE == @Policy_filter "
                )

                sales_by_product_line = (
                    df_selection.groupby(by=["POLICY_TYPE"]).sum()[["MONTHLY_PREMIUM"]].sort_values(by="MONTHLY_PREMIUM")
                )
                
                # # TOP KPI's
                total_sales = int(df_selection["MONTHLY_PREMIUM"].sum())
                st.subheader("Estimated Total Premiums:")
                st.subheader(f"R {total_sales:,}")
                
                with st.expander('selection'):
                    st.dataframe(sales_by_product_line)
                    st.dataframe(df1)
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
                
                
            elif selected_data == '🗃 New Data':
                new_data = get_new_data()
                df = pd.DataFrame(new_data)
                with st.sidebar:
                    df['policy_type'] = df['policy'].apply(lambda x: x['type'])
                    df['policy_status'] = df['policy'].apply(lambda x: x['status'])

                    Age_filter = st.multiselect(label='Select age',
                                            options=df['age'].unique(),
                                            default=df['age'].unique())
                    
                    Policy_Type_filter = st.multiselect(label='Select Policy Status',
                                            options=df['policy_type'].unique(),
                                            default=df['policy_type'].unique())

                    Policy_Status_filter = st.multiselect(label='Select Policy Status',
                                            options=df['policy_status'].unique(),
                                            default=df['policy_status'].unique())

                    Payment_Method_filter = st.multiselect(label='Select Policy Method',
                                            options=df['payment_method'].unique(),
                                            default=df['payment_method'].unique())
                    
                    Gender_filter = st.multiselect(label='Select Gender Group',
                                            options=df['gender'].unique(),
                                            default=df['gender'].unique())
                    
                    Has_Paid_filter = st.multiselect(label='Select has paid filter',
                                            options=df['has_paid'].unique(),
                                            default=df['has_paid'].unique())

                df1 = df.query('has_paid == @Has_Paid_filter & gender == @Gender_filter & payment_method == @Payment_Method_filter & policy_status == @Policy_Status_filter & policy_type == @Policy_Type_filter & age == @Age_filter')    
                    
                st.write(df1)
                total_premuims = float(df1['premium'].sum())
                total_clients = int(df1['policy_type'].count())
                total_active = df1['policy_status'].value_counts().get('active', 0)
                total_new = df1['policy_status'].value_counts().get('new', 0)
                total_canceled = df1['policy_status'].value_counts().get('canceled', 0)
                # total_unkown = total_clients - total_active - total_inactive
                
                total1,total2,total3 = st.columns(3,gap='large')

                with total1:
                    st.image('images/hand.png',use_column_width='Auto')
                    st.metric(label = 'Total Premiums', value= (f"R{total_premuims}"))
                
                with total2:
                    st.image('images/conversion.png',use_column_width='Auto')
                    st.metric(label = 'Total Clients', value= (total_clients))
                
                with total3:
                    st.image('images/impression.png',use_column_width='Auto')
                    st.metric(label = 'Total Active', value= (total_active))
                    st.metric(label = 'Total New', value= (total_new))
                    st.metric(label = 'Total Canceled', value= (total_canceled))
                    
                # df_selection = df.query(
                #     " POLICY_TYPE == @Policy_filter "
                # )

                # sales_by_product_line = (
                #     df_selection.groupby(by=["POLICY_TYPE"]).sum()[["MONTHLY_PREMIUM"]].sort_values(by="MONTHLY_PREMIUM")
                # )
                
                # # # TOP KPI's
                # total_sales = int(df_selection["MONTHLY_PREMIUM"].sum())
                # st.subheader("Estimated Total Premiums:")
                # st.subheader(f"R {total_sales:,}")
                
                # with st.expander('selection'):
                #     st.dataframe(sales_by_product_line)
                #     st.dataframe(df1)
                # fig_product_sales = px.bar(
                #     sales_by_product_line,
                #     x="MONTHLY_PREMIUM",
                #     y=sales_by_product_line.index,
                #     orientation="h",
                #     title="<b>Sales by Policy Type</b>",
                #     color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
                #     template="plotly_white",
                # )
                # fig_product_sales.update_layout(
                #     plot_bgcolor="rgba(0,0,0,0)",
                #     xaxis=(dict(showgrid=True))
                # )

                # left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
                # st.plotly_chart(fig_product_sales, use_container_width=True)
                with st.expander('Details'):
                    for doc in new_data:
                        st.write("## Document ID: ", doc["_id"])
                        st.write("First Name: ", doc["first_name"])
                        st.write("Last Name: ", doc["last_name"])
                        st.write("Email: ", doc["email"])
                        st.write("Phone Number: ", doc["phone_no"])
                        st.write("Gender: ", doc["gender"])
                        st.write("Race: ", doc["race"])
                        st.write("ID Number: ", doc["id_no"])
                        st.write("Date of Birth: ", doc["date_of_birth"])
                        st.write("Age: ", doc["age"])
                        st.write("Reminder Date: ", doc["reminder_date"])
                        st.write("Premium: ", doc["premium"])
                        st.write("Payment Date: ", doc["payment_date"])
                        st.write("Payment Method: ", doc["payment_method"])
                        st.write("Has Paid: ", doc["has_paid"])

                        st.write("### Beneficiary Information")
                        st.write("Full Names: ", doc["beneficiary"]["full_names"])
                        st.write("Contact Phone: ", doc["beneficiary"]["contact_phone"])
                        st.write("Relation: ", doc["beneficiary"]["relation"])

                        st.write("### Policy Information")
                        st.write("Policy Number: ", doc["policy"]["policy_number"])
                        st.write("Type: ", doc["policy"]["type"])
                        st.write("Cover: ", doc["policy"]["cover"])
                        st.write("Status: ", doc["policy"]["status"])

                        st.write("### Dependents Information")
                        for dependent in doc["dependents"]:
                            st.write("Name: ", dependent["name"])
                            st.write("ID Number: ", dependent["id"])
                            st.write("Age: ", dependent["age"])
                            st.write("Relation: ", dependent["relation"])
        # --- EDIT DATA --- #
        elif selected == "Edit Data":
            st.title("Insurance Customer Management System")

                # Display search bar
            policy_number = st.text_input("Enter Policy Number to Search")
            if policy_number:
                customer = search_customer(policy_number)
                if customer:
                    display_customer_info(customer)

                    # Display update form
                    st.subheader("Update Customer Information")
                    field = st.selectbox("Field to Update", ["first_name", "last_name", "email", "phone_no", "gender", "race",
                                                            "id_no", "date_of_birth", "beneficiary.full_names",
                                                            "policy.policy_number", "policy.type", "policy.cover",
                                                            "policy.status", "dependents", "premium", "payment_date",
                                                            "payment_method", "has_paid"])
                    value = st.text_input("New Value")
                    if st.button("Update"):
                        update_customer(str(customer["_id"]), field, value)
                        st.success("Customer information updated successfully.")
                else:
                    st.warning("No customer found with that policy number.")        
                # st.write(new_data)
                # st.dataframe(new_data)
                # st.dataframe(sales_by_product_line)
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
        
if __name__ == "__main__":
    main()