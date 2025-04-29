import ollama
import streamlit as st
import pprint

st.title("Ollama Python Chatbox")

#initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

#initialize model
if "model" not in st.session_state:
    st.session_state["model"] = []

list = ollama.list()
models = [model.get("name") or model.get("model") or model.get("id") or "Unnamed Model" 
          for model in list.get("models", [])]

st.session_state["model"] = st.selectbox("Choose your model", models)

# # optional: result generator
# def model_res_generator():
#     stream = ollama.chat(
#         model = st.session_state["model"]
#         messages = st.session_stae["messages"]
#         stream = True
#     )

#     for chunk in stream:
#         yield chunk["message"]["context"]

#display chat history on rerun
for message in st.session_state['messages']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    #add latest chat to history in format {role, content}
    st.session_state["messages"].append({'role': "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ollama.chat(
            model= 'llama2', messages = st.session_state["messages"], stream = False
        )

        message = response["message"]["content"]
        st.markdown(message)
        st.session_state["messages"].append({'role': "assistant", "content": message})
