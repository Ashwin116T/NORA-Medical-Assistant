from prompt_templates import memory_prompt_template
from langchain.chains import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Chroma
import chromadb
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def create_llm():
    return Ollama(
        model=config["ollama"]["model_name"],
        base_url=config["ollama"]["base_url"],
        temperature=config["model_config"]["temperature"],
        num_predict=config["model_config"]["num_predict"]
    )

def create_embeddings(embeddings_path = config["embeddings_path"]):
    return HuggingFaceInstructEmbeddings(model_name=embeddings_path)

def create_chat_memory(chat_history):
    return ConversationBufferWindowMemory(memory_key="history", chat_memory=chat_history, k=3)

def create_prompt_from_template(template):
    return PromptTemplate.from_template(template)

def create_llm_chain(llm, chat_prompt, memory):
    return LLMChain(llm=llm, prompt=chat_prompt, memory=memory)
    
def load_normal_chain(chat_history):
    return chatChain(chat_history)

def load_vectordb(embeddings):
    persistent_client = chromadb.PersistentClient("chroma_db")

    langchain_chroma = Chroma(
        client=persistent_client,
        collection_name="pdfs",
        embedding_function=embeddings,
    )

    return langchain_chroma

def load_pdf_chat_chain(chat_history):
    return pdfChatChain(chat_history)

def load_retrieval_chain(llm, memory, vector_db):
    return RetrievalQA.from_llm(llm=llm, memory=memory, retriever=vector_db.as_retriever(kwargs={"k": 3}))

class pdfChatChain:

    def __init__(self, chat_history):
        self.memory = create_chat_memory(chat_history)
        self.vector_db = load_vectordb(create_embeddings())
        llm = create_llm()
        #chat_prompt = create_prompt_from_template(memory_prompt_template)
        self.llm_chain = load_retrieval_chain(llm, self.memory, self.vector_db)

    def run(self, user_input):
        print("Pdf chat chain is running...")
        return self.llm_chain.run(query = user_input, history=self.memory.chat_memory.messages ,stop=["Human:"])

class chatChain:

    def __init__(self, chat_history):
        # Create memory from the chat history
        self.memory = create_chat_memory(chat_history)
        # Build the LLM
        llm = create_llm()
        # Create prompt from the memory_prompt_template
        chat_prompt = create_prompt_from_template(memory_prompt_template)
        # Create final LLM chain with memory
        self.llm_chain = create_llm_chain(llm, chat_prompt, self.memory)
        # Keep reference to the prompt template if needed
        self.prompt_template = chat_prompt

    def run(self, user_input):
        return self.llm_chain.run({
            "history": self.memory.buffer,  # Most recent conversation turns
            "human_input": user_input
        })
        return response.replace("[INST]", "").replace("[/INST]", "").replace("<s>", "").replace("</s>", "")