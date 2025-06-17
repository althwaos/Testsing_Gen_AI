import os
import streamlit as st
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load env vars (optional)
load_dotenv()

# Required environment variables (you can also hardcode them directly for quick tests)
endpoint = "https://group7project.openai.azure.com/"
deployment = "gpt-4o-mini"
openai_api_key = "7CqvJEXBe6eFMK18yVr9jB811IyfIGbw2FqxCZREkMmqwJWQNj4ZJQQJ99BEACYeBjFXJ3w3AAAAACOGSx58"   # Azure OpenAI API key
search_endpoint = "https://babycoachdata.search.windows.net"
search_index = "xxx"  # This must match your uploaded RAG index
search_api_key = "wA0JRiCLoFKrDLjAnm9Tx6SIfPEvG2quciS5NMCOgzAzSeBvjyd3"     # Azure Cognitive Search admin key


# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=openai_api_key,
    azure_endpoint=endpoint,
    api_version='2024-05-01-preview',
)

# UI
st.title("🍼 Baby Coach Chat (Azure OpenAI + RAG)")
st.markdown("Ask anything about babies aged 0–24 months.")

user_input = st.text_input("Ask your question:")

if st.button("Ask") and user_input:
    with st.spinner("Thinking..."):

        # Make LLM call with RAG
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are Baby Coach, a warm, medically-informed assistant for parents of babies aged 0–24 months. Your job is to give clear, empathetic, and accurate guidance based on trusted pediatric sources (AAP, CDC, WHO, Mayo Clinic). Always prioritize the baby’s safety and the parent’s peace of mind. If the query is potentially serious, calmly suggest speaking with a pediatrician. Avoid speculation or advice beyond established medical guidelines. Only use the RAG index to retrieve the data."
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            max_tokens=800,
            temperature=0.7,
            top_p=0.95,
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": search_endpoint,
                            "index_name": search_index,
                            "authentication": {
                                "type": "api_key",
                                "key": search_api_key
                            }
                        }
                    }
                ]
            }
        )

        # Display result
        st.success("Response:")
        st.write(response.choices[0].message.content)
