import os
import streamlit as st
import uuid
import random
import string
import pprint
import datetime
import os
from bson.objectid import ObjectId
import pandas as pd
from numerize.numerize import numerize
from pymongo import MongoClient
from datetime import date, timedelta
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

@st.cache_resource
def init_connection():
    # return MongoClient(**st.secrets["mongo"])
    return MongoClient("mongodb://user-1:user1@ac-m55jkix-shard-00-00.f3t8izm.mongodb.net:27017/test?replicaSet=atlas-nx39y5-shard-0&tls=true&tlsAllowInvalidHostnames=true&tlsAllowInvalidCertificates=true&authSource=admin")
    # return MongoClient("mongodb://localhost:27017")
client = init_connection()

# @st.cache
# def get_data():
#     df = pd.read_csv('policy_data.csv')
#     # df['payment_date']= pd.to_datetime(df['payment_date'])
#     # df['reminder_date']= pd.to_datetime(df['reminder_date'])
#     return df


try:
    @st.cache_resource
    def get_old_data():
        db = client.tfs_db
        data =  db.old_data.find()
        data = list(data)  # make hashable for st.experimental_memo
        return data

    def get_new_data():
        db = client.tfs_db
        data = db.clients.find()
        data = list(data)
        return data

    def calculate_age(dob):
        today = datetime.datetime.today()
        age = today.year - dob.year
        if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
            age -= 1
        return age

except Exception:
    st.warning("Unable to connect to server")

def db_to_pd():
    data = get_old_data()
    df = pd.DataFrame(data)
    return df

def write_csv_file():
    with open("data.csv", "w") as file:
        df = db_to_pd()
        df.to_csv(file, index=False)

def read_csv():
    df = pd.read_csv(
        "data.csv"
    )
    return df

def insert_client_doc(first_name,last_name,email,phone_no,gender,race,id_no,dob,address, image_file,payment_method,beneficiary_names,beneficiary_phone,ben_relation,policy_type,policy_cover,policy_premium,payment_date,reminder_date,age,has_paid,dependents):
    db = client.tfs_db
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
        "photo_id" : image_file,
        "reminder_date" : reminder_date,
        "address" : address,
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
            "status" : init_policy_status(),
        },
        "dependents" : dependents
    }
    db['clients'].insert_one(client_document)

def generate_policy_number():
    digits = string.digits
    policy_number = "TFS_" + ''.join(random.choice(digits) for i in range(10))
    return policy_number

def generate_employee_id():
    letters = string.ascii_letters
    employee_id = ''.join(random.choice(letters + string.digits) for i in range(10))
    return employee_id

def check_if_cp_exists(cpp_collection, value):
    if cpp_collection.find_one({'policy_number': value}):
        return True
    else:
        return False

def enter_cpp(pol_no):
    db = client.tfs_db
    pn = pol_no
    cpp_collection = db.cpp
    chkpol = check_if_cp_exists(cpp_collection, pn)
    print("POLICY NUMBER")
    print(pn)
    print(pol_no)
    print(pn)
    print("=====")
    print("POLICY NUMBER CHECK")
    print(chkpol)
    if chkpol is False:
        print(chkpol)
        policy_no_doc = {
            "policy_number" : pol_no
        }
        st.write( " new entery successfull")
        cpp_collection.insert_one(policy_no_doc)
    elif chkpol is True: {
        st.write("policy number exists")
    }

def register_employee(emp_id,first_name,last_name,email,password,role,status):
    db = client.tfs_db
    employee_collection = db.employees
    today = datetime.date.today()

    employee_document = {
        "employee_Id" : emp_id,
        "first_name" : first_name,
        "last_name" : last_name,
        "email" : email,
        "password" : password,
        "role" : role,
        "hire_date" : today.isoformat(),
        "status" : status
    }
    inserted_id = employee_collection.insert_one(employee_document).inserted_id

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters", key='mod')

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

def determine_policy_status(member_registration_date, payment_dates, waiting_period_end, policy_cancelled):
    current_date = datetime.now().date()

    if policy_cancelled:
        return "cancelled"

    time_since_registration = current_date - member_registration_date
    if time_since_registration <= timedelta(days=60):
        return "new"

    missed_payments = 0
    for payment_date in payment_dates:
        time_since_payment = current_date - payment_date
        if time_since_payment > timedelta(days=30):
            missed_payments += 1

    if missed_payments >= 3:
        return "pending lapse"
    elif current_date >= waiting_period_end:
        return "newly active"

    return "unknown"

def init_policy_status():
    status = 'new'
    return status

def update_policy_status(policy_no):
    # TODO
    # find policy to be updated using passed policy_no
    # conditions that determine status i.e waiting periods etc
    status = 'new'
    return status

def calculate_premium(tier, cover, age, members):
    # Dictionary to store the cost for each tier and cover
    tier_cost = {'silver': {'single': {'age_64': 70, 'age_65': 90}, 'family': 110},
                'gold': {'single': {'age_64': 100, 'age_65': 120}, 'family': 130},
                'platinum': {'single': {'age_64': 130, 'age_65': 150}, 'family': 160}}

    # Cost for each tier and cover
    cost = tier_cost.get(tier.lower(), {'single': {'age_64': 0, 'age_65': 0}, 'family': 0}).get(cover.lower(), 0)

    # Check age to determine the cost of single cover
    if cover.lower() == 'single':
        if age <= 64:
            cost = cost['age_64']
        else:
            cost = cost['age_65']

    # Additional cost for members
    if members > 3:
        cost += (members - 3) * 20
    return cost

def show_client_data():
    items = client.find()
    items = list(items)
    return items

def show_existing_client_data():
    items = client.find()
    items = list(items)
    return items


def display_old_customer_info(customer):
    st.write("**Name:**", customer["FIRST_NAME"], customer["LAST_NAME"])
    st.write("**Phone Number:**", customer["MOBILE_NO"])
    st.write("**ID Number:**", customer["ID_NO"])
    st.write("**Date of Birth:**", customer["POLICY_NO"])
    st.write("**Policy Type:**", customer["POLICY_TYPE"])
    st.write("**Policy Status:**", customer["POLICY_STATUS"])
    st.write("**Premium:**", customer["MONTHLY_PREMIUM"])
    st.write("**Payment Date:**", customer["DEBIT_DATE"])
    st.write("**Payment Method:**", customer["PAY_METHOD"])
    st.write("**Has Paid:**", customer["HAS_PAID"])


# def display_customer_info(customer):
#     st.write("**Name:**", customer["first_name"], customer["last_name"])
#     st.write("**Email:**", customer["email"])
#     st.write("**Phone Number:**", customer["phone_no"])
#     st.write("**Gender:**", customer["gender"])
#     st.write("**Race:**", customer["race"])
#     st.write("**ID Number:**", customer["id_no"])
#     st.write("**Date of Birth:**", customer["date_of_birth"])
#     st.write("**Age:**", customer["age"])
#     st.write("**Beneficiary Name:**", customer["beneficiary"]["full_names"])
#     st.write("**Policy Number:**", customer["policy"]["policy_number"])
#     st.write("**Policy Type:**", customer["policy"]["type"])
#     st.write("**Policy Cover:**", customer["policy"]["cover"])
#     st.write("**Policy Status:**", customer["policy"]["status"])
#     st.write("**Dependents:**")
#     for dependent in customer["dependents"]:
#         st.write(f"- {dependent['name']}, {dependent['id']}, {dependent['age']}, {dependent['relation']}")
#     st.write("**Premium:**", customer["premium"])
#     st.write("**Payment Date:**", customer["payment_date"])
#     st.write("**Payment Method:**", customer["payment_method"])
#     st.write("**Has Paid:**", customer["has_paid"])

def search_client_by_ID(id_no):
    db = client.tfs_db
    client = db['clients'].find_one({"id_no": id_no})
    return client

def search_customer(policy_number):
    db = client.tfs_db
    customer = db['clients'].find_one({"policy.policy_number": policy_number})
    return customer

def search_old_customer(policy_number):
    db = client.tfs_db
    customer = db['old_data'].find_one({"POLICY_NO": policy_number})
    return customer
def update_customer(customer_id, field, value):
    db = client.tfs_db
    db['clients'].update_one({"_id": ObjectId(customer_id)}, {"$set": {field: value}})

