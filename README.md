# 🛡️ GRC-Agent  

The **GRC Agent** is a bilingual (Arabic & English) AI assistant that helps organizations in **Governance, Risk, and Compliance (GRC)** by delivering **instant, reliable, and source-backed answers** from official **National Cybersecurity Authority (NCA)** regulations in Saudi Arabia.  

Using **Natural Language Processing (NLP)** and **Retrieval-Augmented Generation (RAG)**, the system simplifies access to lengthy cybersecurity guidelines, reduces manual effort, and enables quick compliance checks in both Arabic and English.  

By combining **AI-driven retrieval, multilingual embeddings, and a conversational interface**, the GRC Agent ensures regulatory knowledge is always **accessible, accurate, and aligned with Saudi Vision 2030** goals for digital transformation.  

Core objectives of the system:  
- Simplify access to official cybersecurity guidelines.  
- Support bilingual interaction (Arabic & English).  
- Provide fast, context-aware responses from NCA frameworks.  
- Strengthen governance, risk management, and compliance within organizations.  

## 📸 Screenshots  

### 🔹 English Interface  
![English UI](image/Screenshot%202025-09-08%20at%2012.30.48%20PM.png)  

### 🔹 Arabic Interface  
![Arabic UI](image/Screenshot%202025-09-08%20at%2012.22.26%20PM.png)  

### 🔹 Example Query (English)  
![English Query](image/Screenshot%202025-09-08%20at%2012.24.10%20PM.png)  

### 🔹 Example Query (Arabic)  
![Arabic Query](image/Screenshot%202025-09-08%20at%2012.21.36%20PM.png)  

### 🔹 Landing Page  
![Landing Page](image/Screenshot%202025-09-08%20at%2012.25.07%20PM.png)  

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

