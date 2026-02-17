# simple_rag_working.py - FINAL VERSION WITH CORRECT MODEL!
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

st.title("🏦 Banking Policy AI Assistant")
st.write("*Your first AI RAG project!* 🎉")

# Check and configure API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    st.error("⚠️ Add GOOGLE_API_KEY to .env file!")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_rag():
    # Load PDFs
    docs = []
    for pdf in ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']:
        if os.path.exists(pdf):
            st.info(f"📄 Loading {pdf}...")
            loader = PyPDFLoader(pdf)
            docs.extend(loader.load())
    
    if not docs:
        st.error("❌ No PDFs found! Add doc1.pdf to your project folder.")
        return None
    
    st.success(f"✅ Loaded {len(docs)} pages")
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    st.info(f"📄 Created {len(chunks)} chunks")
    
    # FREE local embeddings
    st.info("🔄 Loading embedding model (first time ~90MB download)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create vector store
    vectorstore = Chroma.from_documents(chunks, embeddings)
    
    st.success("✅ Knowledge base ready!")
    return vectorstore

# Load knowledge base
with st.spinner("🔄 Building your AI assistant..."):
    vectorstore = load_rag()

if vectorstore:
    st.write("---")
    
    # User input
    question = st.text_input("💬 Ask a question about the banking documents:", 
                            placeholder="e.g., What is this document about?")
    
    if question:
        with st.spinner("🤔 AI is thinking..."):
            try:
                # Search for relevant chunks
                docs = vectorstore.similarity_search(question, k=3)
                
                # Build context from retrieved docs
                context = "\n\n".join([doc.page_content for doc in docs])
                
                # Create prompt
                prompt = f"""Based on the following context from banking documents, answer the question accurately and concisely.

Context:
{context}

Question: {question}

Answer:"""
                
                # Use Gemini 2.5 Flash - THE CORRECT MODEL NAME!
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                answer = response.text
                
                # Display answer
                st.write("### 📝 Answer:")
                st.write(answer)
                
                # Display sources
                st.write("### 📚 Sources:")
                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('source', 'Unknown')
                    page = doc.metadata.get('page', 'N/A')
                    st.write(f"{i}. **{source}** (Page {page})")
                    
                    with st.expander(f"📄 View snippet {i}"):
                        st.write(doc.page_content[:400] + "...")
                
                st.success("✅ Your first AI answer! 🎉🎉🎉")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.write("Check your GOOGLE_API_KEY in .env file")

else:
    st.error("Failed to load knowledge base. Add PDF files!")

# Sidebar
with st.sidebar:
    st.write("## 🎯 Your First RAG System!")
    st.write("**RAG** = Retrieval Augmented Generation")
    
    st.write("## ✅ Status")
    st.write(f"**API Key:** ✅ Set")
    pdf_count = sum([os.path.exists(f'doc{i}.pdf') for i in range(1,4)])
    st.write(f"**PDFs Loaded:** {pdf_count}/3")
    
    st.write("## 🔧 How it works:")
    st.write("1. 📄 Load your PDFs")
    st.write("2. ✂️ Split into chunks")
    st.write("3. 🔢 Create embeddings")
    st.write("4. 🔍 Search for relevant chunks")
    st.write("5. 🤖 AI answers using context")
    
    st.write("---")
    st.write("**💪 Built by:** Krishnaveni Raji")
    st.write("**📅 Date:** February 2026")
    #st.write("**🎓 Course:** Proitbridge Week 3-4")
    st.write("**⭐ Project #1:** COMPLETE!")