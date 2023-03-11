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

from streamlit_login_auth_ui.widgets import __login__
import streamlit_book as stb

header_left,header_mid,header_right = st.columns([3,3,3],gap='large')
header_mid.subheader('Admin Board')


# with visual_tab:
selected_data = st.sidebar.selectbox('📊 Selelct which data to use', ('Existing Data', 'New Data'))
if selected_data == 'Existing Data':  
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

    # st.image('images/logo-trans.png',use_column_width='Auto')
    total1,total2,total3,total4,total5 = st.columns(5,gap='large')
    with total1:
        st.image('images/svgexport-17.png',use_column_width='Auto')
        st.metric(label = 'Total Premiums', value=numerize(total_premuims))

    with total2:
        st.image('images/svgexport-20.png',use_column_width='Auto')
        st.metric(label = 'Total Clients', value= (total_clients))

    with total3:
        st.image('images/svgexport-21.png',use_column_width='Auto')
        st.metric(label = 'Total Active', value= (total_active))
    
    with total4:
        st.image('images/svgexport-22.png',use_column_width='Auto')
        st.metric(label = 'Total inactive', value= (total_inactive))
        
    with total5:
        st.image('images/svgexport-23.png',use_column_width='Auto')
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

        # with st.expander('selection'):
            
        # with elements("dashboard"):

        #     # You can create a draggable and resizable dashboard using
        #     # any element available in Streamlit Elements.

        #     # from streamlit_elements import dashboard

        #     # First, build a default layout for every element you want to include in your dashboard

        #         layout = [
        #             # Parameters: element_identifier, x_pos, y_pos, width, height, [item properties...]
        #             dashboard.Item("first_item", 0, 0, 2, 2),
        #             dashboard.Item("second_item", 2, 0, 2, 2, isDraggable=False, moved=False),
        #             dashboard.Item("third_item", 0, 2, 1, 1, isResizable=False),
        #         ]

        #         # Next, create a dashboard layout using the 'with' syntax. It takes the layout
        #         # as first parameter, plus additional properties you can find in the GitHub links below.

        #         with dashboard.Grid(layout):
        #             mui.Paper("First item", key="first_item")
        #             mui.Paper("Second item (cannot drag)", key="second_item")
        #             mui.Paper("Third item (cannot resize)", key="third_item")

        #         # If you want to retrieve updated layout values as the user move or resize dashboard items,
        #         # you can pass a callback to the onLayoutChange event parameter.

        #         def handle_layout_change(updated_layout):
        #             # You can save the layout in a file, or do anything you want with it.
        #             # You can pass it back to dashboard.Grid() if you want to restore a saved layout.
        #             print(updated_layout)

        #         with dashboard.Grid(layout, onLayoutChange=handle_layout_change):
        #             mui.Paper("First item", key="first_item")
        #             mui.Paper("Second item (cannot drag)", key="second_item")
        #             mui.Paper("Third item (cannot resize)", key="third_item")
                
            # st.dataframe(sales_by_product_line)
            
            # st.dataframe(df1)
            
            # fig_product_sales = px.bar(
            # sales_by_product_line,
            # x="MONTHLY_PREMIUM",
            # y=sales_by_product_line.index,
            # orientation="h",
            # title="<b>Sales by Policy Type</b>",
            # color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
            # template="plotly_white",
            # )
            # fig_product_sales.update_layout(
            # plot_bgcolor="rgba(0,0,0,0)",
            # xaxis=(dict(showgrid=True))
            # )

            # left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
            # st.plotly_chart(fig_product_sales, use_container_width=True)

elif selected_data == 'New Data':
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
        # st.metric(label = 'Total Canceled', value= (total_unkown))

    
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

policy_number = st.text_input("Search by Policy")
# id_no = st.text_input("Search by ID number",max_chars=13 )
if policy_number:
    customer = search_customer(policy_number)
    old_customer = search_old_customer(policy_number)
    
    if old_customer:
        display_old_customer_info(old_customer)

        # Display update form
        st.subheader("Update Customer Information")
        field = st.selectbox("Field to Update", ["FIRST_NAME", "LAST_NAME", "ID_NO","MOBILE_NO",
                                                "POLICY_NO", "POLICY_TYPE", "POLICY_STATUS",
                                                "MONTHLY_PREMIUM", "DEBIT_DATE", "PAY_METHOD", "HAS_PAID"])
        value = st.text_input("New Value")
        if st.button("Update"):
            update_customer(str(customer["_id"]), field, value)
            st.success("Customer information updated successfully.")
    else:
        st.warning("No customer found with that policy number.")
    
    # if customer:
    #     display_customer_info(customer)

    #     # Display update form
    #     st.subheader("Update Customer Information")
    #     field = st.selectbox("Field to Update", ["first_name", "last_name", "email", "phone_no", "gender", "race",
    #                                             "id_no", "date_of_birth", "beneficiary.full_names",
    #                                             "policy.policy_number", "policy.type", "policy.cover",
    #                                             "policy.status", "dependents", "premium", "payment_date",
    #                                             "payment_method", "has_paid"])
    #     value = st.text_input("New Value")
    #     if st.button("Update"):
    #         update_customer(str(customer["_id"]), field, value)
    #         st.success("Customer information updated successfully.")
    # else:
    #     st.warning("No customer found with that policy number.")
