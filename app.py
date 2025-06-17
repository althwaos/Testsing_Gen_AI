import os
import streamlit as st
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Title
st.title("🍼 Baby Coach Chat (Azure OpenAI + RAG)")
st.markdown("Ask anything about babies aged 0–24 months.")

# User input
user_input = st.text_input("Ask your question:")

# Only set up the client when a question is entered
if user_input:
    if st.button("Ask"):
        with st.spinner("Thinking..."):

            # === Azure OpenAI Setup ===
            endpoint = os.getenv("ENDPOINT_URL", "https://group7project.openai.azure.com/")
            deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4o-mini")
            search_endpoint = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "https://babycoachdata.search.windows.net")
            search_index = os.getenv("AZURE_AI_SEARCH_INDEX", "your-index-name")
            cognitive_resource = os.getenv('AZURE_COGNITIVE_SERVICES_RESOURCE', 'group7project')

            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                f'{cognitive_resource}.default'
            )

            client = AzureOpenAI(
                azure_endpoint=endpoint,
                azure_ad_token_provider=token_provider,
                api_version='2024-05-01-preview',
            )

            # Call the model
            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are Baby Coach, a warm, medically-informed assistant for parents of babies aged 0–24 months..."
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
                                    "type": "system_assigned_managed_identity"
                                }
                            }
                        }
                    ]
                }
            )

            # Show result
            st.success("Response:")
            st.write(response.choices[0].message.content)
