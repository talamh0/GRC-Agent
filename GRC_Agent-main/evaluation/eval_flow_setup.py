import os
# import arabic_reshaper
# from bidi.algorithm import get_display

# from langchain.chains import RetrievalQA
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
from langchain.schema import BaseRetriever

import re
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.vectorstores import Chroma
# from langchain.schema.document import Document
# from typing import List

from langchain.schema import BaseRetriever
from pydantic import Field
from typing import Any

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
import certifi
import pandas as pd
from tqdm import tqdm

# import warnings

from ragas import EvaluationDataset
from ..code.agent_prep import get_agent_response, initialize_agent

os.environ['SSL_CERT_FILE'] = certifi.where()
# docker run -d -p 6333:6333 -p 6334:6334 -v "C:/Users/mokar/KAUST Camp/project/OURPROJ/qdrant_storage:/qdrant/storage:z" qdrant/qdrant


# define needed functions
def extract_control_ids(query: str):
    return re.findall(r'\b\d+(?:-\d+){0,3}\b', query)

def normalize_control_id(raw_id):
    # Arabic-Indic to Western numerals
    arabic_to_western = str.maketrans("٠١٢٣٤٥٦٧٨٩۱۲۳۷۸", "012345678912378")
    normalized = raw_id.translate(arabic_to_western)
    
    # Replace separators to standard format
    normalized = normalized.replace('.', '-').replace(',', '-').strip()
    
    return normalized



# read evaluation datasets
files = [
    "Final_ECC_CSCC_Evaluation_AR_Dataset.xlsx",
    "Final_ECC_CSCC_Evaluation_ENG_Dataset.xlsx",
]

paths =[]
for file in files:
    paths.append(os.path.join(os.path.dirname(__file__), 'evaluation datasets', file))

dfs = [pd.read_excel(path) for path in paths]




# build custom retrieval

class CustomRetriever(BaseRetriever):
    retriever: Any = Field() # This is the QdrantVectorStore
    embedding_model: Any = Field() # This is the HuggingFaceEmbeddings model
    top_k: int = Field(default=10)

    def _get_relevant_documents(self, query: str):
        # 1. Normalize and extract IDs
        raw_ids = extract_control_ids(query)
        control_ids = [normalize_control_id(cid) for cid in raw_ids]

        # 2. Re-run with the corrected filter logic
        if control_ids:
            # print(f"inside HybridRetriever and found control ids: {control_ids}")
            # filter_obj = control_id_filter(query)
            # The QdrantVectorStore `similarity_search` method correctly takes a filter.
            candidate_docs = self.retriever.similarity_search_with_score(
                query=query,
                k=50,  # Or a larger number to get a good pool
                # filter=filter_obj
                filter=Filter(
                        should=[
                            FieldCondition(
                                key="metadata.control_id",
                                match=MatchAny(any=control_ids)
                            )
                        ]
                    )
            )
            # print(f"finished filtered retrival. got: \n {candidate_docs}")
            # You don't need to re-rank by score here, as the k=50 query is already sorted by Qdrant.
            final_docs = []
            for doc, _ in candidate_docs:
                final_docs.append(doc.page_content)
            return final_docs

        # 3. No control IDs, retrun empty list
        return None

    async def _aget_relevant_documents(self, query: str):
        return self._get_relevant_documents(query)


print("\nLoading the embedding model...\n")
# Define the embedding model used to create the store. It must be the same one.
model_name = "intfloat/multilingual-e5-large"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embed_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)
print("\n✅ Embedding model loaded successfully!\n")

# Load the vector store from the specified directory.
print("\nLoading the Qdrant vector store...\n")
# client = QdrantClient(path="/langchain_qdrant")
client = QdrantClient(url="http://localhost:6333")
vector_store = QdrantVectorStore(
    client=client,
    collection_name="docs_collection",
    embedding=embed_model,
    # retrieval_mode=RetrievalMode.DENSE # default
)

print("\n✅ Qdrant store loaded successfully!\n")


# initialize the retriever
custom_retriever = CustomRetriever(
    retriever=vector_store,
    embedding_model=embed_model,
    top_k=10
)

agent, hybrid_retriever = initialize_agent()
config = {"configurable": {"thread_id": "evaluation_session"}}

eval_ds_list = []

print("\nProcessing the evaluation dataset...\n")

for i, df in enumerate(dfs):
    for index, row in tqdm(df.iterrows(), total=len(df)):
        cols = df.columns
        question = row[cols[0]]
        reference = row[cols[1]]
        query = row[cols[2]]

        if (i == 1) and (index > 9) and (index < 34):
            continue

        gt_docs = custom_retriever._get_relevant_documents(query)
        if not gt_docs:
            continue
        ret_docs = hybrid_retriever._get_relevant_documents(question)
        response = get_agent_response(question, agent, config)

        eval_ds_list.append(
            {
                "user_input":question,
                "reference control": query,
                "reference":reference,
                "reference_contexts":gt_docs,
                "response":response,
                "retrieved_contexts": [ret_doc.page_content for ret_doc in ret_docs],
                "source": files[i]
                
            }
        )

        # break



# Convert the list to a pandas DataFrame
eval_df = pd.DataFrame(eval_ds_list)

output_folder = "eval"

# Check if the folder exists, and create it if it doesn't
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Now, you can save the files inside the folder
# eval_df.to_csv(f"{output_folder}/evaluation_dataset_csv.csv", index=False)
# eval_df.to_excel(f"{output_folder}/evaluation_dataset_arabic_xlsx.xlsx", index=False)
eval_df.to_excel(f"{output_folder}/evaluation_dataset_full_xlsx.xlsx", index=False)


# print(f"\n\n {eval_ds_list} \n\n")

print("finished dataset processing and saving")

# print("\nTrying ragas dataset...\n")

# ragas_dataset = EvaluationDataset.from_pandas(eval_df.iloc[:, :-1]) # Exclude the 'source' column

# print("\n✅ Ragas dataset created successfully!\n")
# print(f"\n\n{ragas_dataset}\n\n")