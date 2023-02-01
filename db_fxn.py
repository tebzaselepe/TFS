import streamlit as st
import os
import pprint
import datetime
from datetime import date, timedelta
import pandas as pd
import datetime
import pymongo
from pymongo import MongoClient


# connection_str = f"mongodb+srv://cluster0.sfcysmi.mongodb.net/test?tls=true&tlsCertificateKeyFile=C%3A%5CUsers%5CPfunzo%5CDesktop%5Cstreamlit_mongo%5CX509-cert-3952646099818541177.pem&tlsAllowInvalidCertificates=true&tlsAllowInvalidHostnames=true&authMechanism=MONGODB-X509&authSource=%24external"
connection_str = "mongodb://localhost:27017"
client = MongoClient(connection_str)

db = client.tfs_db
clients = db.client_data
employees = db.emps

def show_existing_client_data():
    items = clients.find()
    items = list(items)
    return items
