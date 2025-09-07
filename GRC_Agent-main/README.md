# GRC_Agent 
This project focuses on developing the GRC Agent Website, a corporate AI assistant designed to support Governance, Risk, and Compliance (GRC) specialists in both Arabic and English. In alignment with Saudi Arabia’s vision for digital transformation and robust cybersecurity frameworks, the agent leverages Retrieval-Augmented Generation (RAG) to provide accurate, context-driven answers based on regulatory documents issued by the National Cybersecurity Authority (NCA). The bilingual interface ensures accessibility, while advanced retrieval and memory mechanisms allow for continuous, conversational interaction. The project not only reduces manual workload for GRC professionals but also contributes to building stronger cybersecurity practices across organizations in Saudi Arabia.

# Steps to successfully run the system:
1. Initialize your enviroment
run this python -m venv .venv and activate it if have not done that already

2. Install required libraries
run pip install -r requirements.txt Note: I tried to include all necessary libraries in the requirements.txt file. But in case I missed some and you got errors, please inspect the error message you got, install the missing library, and kindly add it to the requirements.txt to eliminate future problems

3. Prepare docker
ensure you have docker installed
ensure that docker desktop is active
run docker run -d -p 6333:6333 -p 6334:6334 -v "($pwd)/qdrant_storage:/qdrant/storage:z" qdrant/qdrant, replacing ($pwd) with your actuall current working directory
4. Set up your google api key
in agent_prep.py, make sure to configure this line google_api_key = "YOUR GOOGLE API KEY"

5. Set up the Qdrant store
if this this the first time you run the system, run python db_prep.py. this step needs to only be run once at the start of the experiments.

6. Run the system
now you're all set. you can run streamlit run app.py and interact with the agent through the interface.
