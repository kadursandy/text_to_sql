from langchain_community.llms.oci_generative_ai import OCIGenAI
from langchain_community.chat_models import ChatOCIGenAI

config_profile = "DEFAULT"
compartment_id = "<compartment_ocid_or_tenancy_ocid>"
model_id = "ocid1.generativeaimodel.oc1.us-chicago-1.amaaaaaask7dceyanrlpnq5ybfu5hnzarg7jomak3q6kyhkzjsl4qj24fyoq"
service_endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"
provider = "cohere"

# llm = OCIGenAI(
llm = ChatOCIGenAI(
    model_id=model_id,
    service_endpoint=service_endpoint,
    compartment_id=compartment_id,
    auth_type="API_KEY",
    auth_profile=config_profile,
    provider=provider,
    model_kwargs={"temperature": 0, "top_p": 0.75, "max_tokens": 500}
)

response = llm.invoke("Tell me one fact about earth", temperature=0.7)
print(response)