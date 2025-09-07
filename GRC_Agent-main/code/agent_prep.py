# docker run -d -p 6333:6333 -p 6334:6334 -v "C:/Users/mokar/KAUST Camp/project/OURPROJ/qdrant_storage:/qdrant/storage:z" qdrant/qdrant

import os
import re
import arabic_reshaper
from bidi.algorithm import get_display

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.schema import BaseRetriever
from langchain.chat_models import init_chat_model


from langchain.schema import BaseRetriever
from pydantic import Field
from typing import Any

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, FieldCondition, MatchAny
import certifi

from langgraph.graph import MessagesState, StateGraph
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.graph import END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv


import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
load_dotenv()  # This populates os.environ with environment variables from a .env file


## A helper for reshaping Arabic text for correct display.
reshaper = arabic_reshaper.ArabicReshaper()

## Set the SSL certificate path to use certifi's default certificate
os.environ['SSL_CERT_FILE'] = certifi.where()


# Define auxiliary functions
## A function to extract contol IDs
def extract_control_ids(query: str):
    return re.findall(r'\b\d+(?:.\d+){0,3}\b', query)


## A function to normalize IDs
def normalize_control_id(raw_id):
    # Arabic-Indic to Western numerals
    arabic_to_western = str.maketrans("٠١٢٣٤٥٦٧٨٩۱۲۳۷۸", "012345678912378")
    normalized = raw_id.translate(arabic_to_western)
    
    # Replace separators to standard format
    normalized = normalized.replace('.', '-').replace(',', '-').strip()
    
    return normalized


class HybridRetriever(BaseRetriever):
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
                                key="metadata.relevant_ids",
                                match=MatchAny(any=control_ids)
                            ),
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
            for doc, _ in candidate_docs[:self.top_k]:
                final_docs.append(doc)
            return final_docs

        # 3. No control IDs, fall back to unfiltered search.
        # This is the correct way to call the retriever's search method.
        # return self.retriever._get_relevant_documents(query) 
        candidate_docs = self.retriever.similarity_search(query, k=self.top_k)
        # print(f"inside HybridRetriever and no ids detected. got: \n {candidate_docs}")
        return candidate_docs

    async def _aget_relevant_documents(self, query: str):
        return self._get_relevant_documents(query)
    


def initialize_agent():
    
    # Load the pre-built Chroma vector store
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

    # Initialize the Gemini LLM.
    print("\nInitializing the chat model \n")


    # llm = init_chat_model("mistral-large-latest", model_provider="mistralai")
    llm = init_chat_model("deepseek-chat", model_provider="deepseek")

    print("Starting the graph building\n")
    graph_builder = StateGraph(MessagesState)

    hybrid_retriever = HybridRetriever(
        retriever=vector_store,
        embedding_model=embed_model,
        top_k=10
    )

    @tool(response_format="content_and_artifact")
    def retrieve(query: str):
        """
        Retrieve information from a knowledge base to answer questions.
        Use this tool when the user asks a question about a specific topic, concept, or control ID.
        If query contains an explicit control ID or IDS, this tool will provide that certain ID or 
        IDs with their predecessors and successors.
        If the query does not contain an explicit control ID, this tool will perform similarity search
        of the knowledge base based on the query and return relevant documents.
        """
        
        retrieved_docs = hybrid_retriever._get_relevant_documents(query)
        serialized = "\n\n".join(
            (f"metadata: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs



    # Step 1: Generate an AIMessage that may include a tool-call to be sent.
    def query_or_respond(state: MessagesState):
        """Generate tool call for retrieval or respond."""
        llm_with_tools = llm.bind_tools([retrieve])
        response = llm_with_tools.invoke(state["messages"])
        # MessagesState appends messages to state instead of overwriting
        return {"messages": [response]}


    # Step 2: Execute the retrieval.
    tools = ToolNode([retrieve])


    # Step 3: Generate a response using the retrieved content.
    def generate(state: MessagesState):
        """Generate answer."""
        # Get generated ToolMessages
        recent_tool_messages = []
        for message in reversed(state["messages"]):
            if message.type == "tool":
                recent_tool_messages.append(message)
            else:
                break
        tool_messages = recent_tool_messages[::-1]

        # Format into prompt
        docs_content = "\n\n".join(doc.content for doc in tool_messages)
        system_message_content = (
            "You are an assistant for question-answering tasks. "
            "Your name is 'GRC Agent', and your job is to answer GRC employees questions "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Answer in the same language the user asks,  "
            "whether it's Arabic or English, and keep your answer "
            "structured and concise."
            "\n\n"
            f"{docs_content}"
        )
        conversation_messages = [
            message
            for message in state["messages"]
            if message.type in ("human", "system")
            or (message.type == "ai" and not message.tool_calls)
        ]
        prompt = [SystemMessage(system_message_content)] + conversation_messages

        # Run
        response = llm.invoke(prompt)
        return {"messages": [response]}



    graph_builder.add_node(query_or_respond)
    graph_builder.add_node(tools)
    graph_builder.add_node(generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)


    memory = MemorySaver()
    graph = graph_builder.compile(checkpointer=memory)

    print("Graph built successfully")
    return graph, hybrid_retriever




def get_agent_response(query, graph, config):
    try:
        final_state = graph.invoke({"messages": [{"role": "user", "content": query}]}, config=config)
        final_response = final_state["messages"][-1]
        raw_answer = final_response.content

        return raw_answer
    
    except Exception as e:
        return (f"An error occurred: {e}")
