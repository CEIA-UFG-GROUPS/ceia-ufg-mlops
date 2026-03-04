import streamlit as st
import requests

st.title("Interface do Frontend")

if st.button("Fazer Requisição"):
    response = requests.get("http://localhost:8000/")  
    if response.status_code == 200:
        st.write(f"Resposta do backend: {response.json()}")
    else:
        st.write("Erro ao fazer a requisição")
