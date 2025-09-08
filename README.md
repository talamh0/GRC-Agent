# GRC-Agent  

The **GRC Agent** is a bilingual (Arabic & English) AI assistant that helps organizations in **Governance, Risk, and Compliance (GRC)** by delivering **instant, reliable, and source-backed answers** from official **National Cybersecurity Authority (NCA)** regulations in Saudi Arabia.  

Using **Natural Language Processing (NLP)** and **Retrieval-Augmented Generation (RAG)**, the system simplifies access to lengthy cybersecurity guidelines, reduces manual effort, and enables quick compliance checks in both Arabic and English.  

By combining **AI-driven retrieval, multilingual embeddings, and a conversational interface**, the GRC Agent ensures regulatory knowledge is always **accessible, accurate, and aligned with Saudi Vision 2030** goals for digital transformation.  

Core objectives of the system:  
- Simplify access to official cybersecurity guidelines.  
- Support bilingual interaction (Arabic & English).  
- Provide fast, context-aware responses from NCA frameworks.  
- Strengthen governance, risk management, and compliance within organizations.  

## Screenshots  

###  English Interface  
![English UI](image/Screenshot%202025-09-08%20at%2012.25.07%20PM.png)  

###  Example Query (English)  
![English Query](image/Screenshot%202025-09-08%20at%2012.24.10%20PM.png)  

###  Arabic Interface  
![Arabic UI](image/Screenshot%202025-09-08%20at%2012.22.26%20PM.png)  

### Example Query (Arabic)  
![Arabic Query](image/Screenshot%202025-09-08%20at%2012.39.07%20PM.png) 


## 📊 Evaluation  

The GRC Agent was evaluated using a **custom bilingual dataset** (Arabic & English) built from the official NCA cybersecurity regulations (ECC & CSCC).  
The evaluation tested the system’s ability to retrieve and generate accurate answers across different query types.  

###  Datasets  
- **Final_ECC_CSCC_Evaluation_ENG_Dataset.xlsx** → English evaluation dataset  
- **Final_ECC_CSCC_Evaluation_AR_Dataset.xlsx** → Arabic evaluation dataset  
- **evaluation_dataset_full_xlsx.xlsx** → Combined bilingual dataset  
- **kaust_project_evaluation.ipynb** → Notebook for evaluation workflow and metrics  

### Metrics Used  
- **Recall** – ability to retrieve the correct regulatory content.  
- **Precision** – accuracy of retrieved responses.  
- **Accuracy** – overall correctness of generated answers.  
- **Groundness** – extent to which answers are grounded in the source documents.

## 📑 Project Report  

For a detailed explanation of the project design, methodology, evaluation, and results, please refer to the full report:  

[📄 GRC Agent – Final Report (PDF)](GRC%20Agent%20–%20Final%20Report.pdf)  

## 🔗 Team LinkedIn Profiles  

- [Tala Mohammed](https://www.linkedin.com/in/tala-mohammed) – Computer Science Student at King Saud University  
- [Jana Shata](https://www.linkedin.com/in/jana-shata) – Artificial Intelligence Student | Python Programmer | Data Analyst  


## 🛠 Built With  

- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)  
- ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)  
- ![LangChain](https://img.shields.io/badge/LangChain-000000?style=for-the-badge&logo=chainlink&logoColor=white)  
- ![Qdrant](https://img.shields.io/badge/Qdrant-FF6F00?style=for-the-badge&logo=q&logoColor=white)  
- ![DeepSeek](https://img.shields.io/badge/DeepSeek-AI-5D3FD3?style=for-the-badge&logo=OpenAI&logoColor=white)  

##  How to Run  

### 1️⃣ Clone the repository  
```bash
git clone https://github.com/your-username/GRC-Agent.git
cd GRC-Agent
```
### 2️⃣ Install dependencies 
```bash
pip install -r requirements.txt
```
### 3️⃣ Start Qdrant (Docker)
```bash
docker run -d -p 6333:6333 -p 6334:6334 \
-v "$(pwd)/qdrant_storage:/qdrant/storage:z" \
qdrant/qdrant
```
### 4️⃣ Run the application
```bash
streamlit run app.py
```
