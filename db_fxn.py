import streamlit as st
import pandas as pd
import os
import pprint
import datetime
from datetime import date, timedelta
import uuid
import pymongo
from pymongo import MongoClient
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import random
import string

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    # return pymongo.MongoClient(**st.secrets["mongo"])
    return pymongo.MongoClient("mongodb://localhost:27017")
client = init_connection()

try:
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
    @st.experimental_memo(ttl=600)
    def get_data():
        db = client.tfs_db
        items = db.new_client_data.find()
        items = list(items)  # make hashable for st.experimental_memo
        return items
    items = get_data()
    
    # @st.experimental_memo(ttl=600)
    def get_client_collection():
        db = client.tfs_db
        # items = db.new_client_data.find()
        items = db['new_client_data']
        st.write(items)
        return items
    new_client_collection = get_client_collection()
    
    
except Exception:
    st.warning("Unable to connect to server.")

# st.write(items)
# query_df =  pd.DataFrame(items)
# st.dataframe(query_df)
# employees = db.emps

def generate_policy_number():
    digits = string.digits
    policy_number = "TFS_" + ''.join(random.choice(digits) for i in range(10))
    return policy_number

def generate_employee_id():
    letters = string.ascii_letters
    employee_id = ''.join(random.choice(letters + string.digits) for i in range(10))
    return employee_id

df = pd.read_csv( 
    "data.csv"
)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df
    df = df.copy()
    

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input, na=False)]
    return df

def insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,id_photo,payment_method,beneficiary_names,beneficiary_phone,ben_relation,policy_type,policy_cover,policy_premium,payment_date,reminder_date,age,has_paid,dependents):
    clients = get_client_collection()
    client_document = {
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email,
        "phone_no" : phone_no,
        "gender" : gender,
        "race" : race,
        "id_no" : id_no,
        "date_of_birth" : dob.isoformat(),
        "age" : age,
        "photo_id" : id_photo,
        "reminder_date" : reminder_date,
        "premium" : policy_premium,
        "payment_date" : payment_date,
        "payment_method": payment_method,
        "has_paid": has_paid,
        "beneficiary" : {
            "full_names" : beneficiary_names,
            "contact_phone" : beneficiary_phone,
            "relation" : ben_relation,
        },
        "policy" : {
            "policy_number": generate_policy_number(),
            "type" : policy_type,
            "cover" : policy_cover,
            "status" : determine_policy_status(),
        },
        "dependents" : dependents
    }
    clients.insert_one(client_document)
    
# def show_client_data():
#     items = client.find()
#     items = list(items)
#     return items

def determine_policy_status():
    status = 'new'
    return status

def insert_emp_doc(first_name,last_name,email,password,role,status):
    today = datetime.date.today()
    emp_doc = {
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email,
        "password" : password,
        "role" : role,
        "hire_date" : today,
        "status" : status
    }
    inserted_id =  employees.insert_one(emp_doc).inserted_id

def calculate_age(dob):
    today = datetime.datetime.today()
    age = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return age

def calculate_premiums(tier, members, dob):
    from datetime import datetime, timedelta
    
    # Function to calculate the age from the date of birth
    def calculate_age_(dob):
        today = datetime.now()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return age

def calculate_premium(tier, cover, age, members):
    # Dictionary to store the cost for each tier and cover
    tier_cost = {'silver': {'single': {'age_64': 70, 'age_65': 90}, 'family': 110},
                'gold': {'single': {'age_64': 100, 'age_65': 120}, 'family': 130},
                'platinum': {'single': {'age_64': 130, 'age_65': 150}, 'family': 160}}
    
    # Cost for each tier and cover
    cost = tier_cost.get(tier.lower(), {'single': {'age_64': 0, 'age_65': 0}, 'family': 0}).get(cover.lower(), 0)
    st.write(members)
    # Check age to determine the cost of single cover
    if cover.lower() == 'single':
        if age <= 64:
            cost = cost['age_64']
        else:
            cost = cost['age_65']
    
    # Additional cost for members
    if members > 3:
        cost += (members - 3) * 20
    # elif members <= 3:
    #     cost += (members * 500)
        
    return cost

# def show_existing_client_data():
#     items = clients.find()
#     items = list(items)
#     return items
