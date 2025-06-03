from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # Importe ambos do mesmo pacote
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.question_answering import load_qa_chain
import os
from dotenv import load_dotenv

load_dotenv()

#Load dos modelos (Embeddings e LLM)
embeddings_model = OpenAIEmbeddings()
llm = ChatOpenAI(model_name="gpt-3.5-turbo", max_tokens=200)

#Carregar PDF
pdf_link = "projeto.pdf"

loader = PyPDFLoader(pdf_link, extract_images=False)
pages = loader.load_and_split()

#Separar em Chunks (pedaços do documento)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 4000,
    chunk_overlap = 20,
    length_function = len,
    add_start_index = True,
)

chunks = text_splitter.split_documents(pages)

#Salvar no vector DB - Chroma
db = Chroma. from_documents(chunks, embedding=embeddings_model, persist_directory="text_index")
db.persist()

#Carregar DB

vectordb = Chroma(persist_directory="text_index", embedding_function=embeddings_model)

#Load Retriever
retriever = vectordb.as_retriever(search_kwargs={"k": 3})

#Construção da cadeia de Prompt para chamada do LLM
chain = load_qa_chain(llm, chain_type="stuff")

def ask(question):
    context = retriever.get_relevant_documents(question)
    answer = (chain({"input_documents": context, "question": question}, return_only_outputs=True))['output_text']
    return answer, context

user_question = input("User: ")
answer = ask(user_question)
print("Answer: ", answer)