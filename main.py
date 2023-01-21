import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit.components.v1 as components

from hasher import Hasher
from authenticate import Authenticate

def main():
    # hashed_passwords = Hasher(['123', '123']).generate()
    # st.write(hashed_passwords)
    # Loading config file
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
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
if __name__ == "__main__":
    main()