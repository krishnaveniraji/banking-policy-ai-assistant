# app.py - UPDATED FOR LANGCHAIN 2026
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.chains.retrieval_qa.base import RetrievalQA
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(page_title="Banking Policy AI", page_icon="🏦")

# Title
st.title("🏦 Banking Policy AI Assistant")
st.write("Ask questions about banking policies and get instant answers!")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ Please add OPENAI_API_KEY to your .env file!")
    st.stop()

# Load documents (cached)
@st.cache_resource
def load_knowledge_base():
    try:
        # Load PDFs
        docs = []
        pdf_files = ['doc1.pdf', 'doc2.pdf', 'doc3.pdf']
        
        for pdf in pdf_files:
            if os.path.exists(pdf):
                st.info(f"Loading {pdf}...")
                loader = PyPDFLoader(pdf)
                docs.extend(loader.load())
            else:
                st.warning(f"⚠️ {pdf} not found - skipping")
        
        if not docs:
            st.error("❌ No PDF files found! Please add at least one PDF file named doc1.pdf")
            return None
        
        st.success(f"✅ Loaded {len(docs)} pages from PDFs")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(docs)
        st.info(f"📄 Created {len(chunks)} text chunks")
        
        # Create embeddings and vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(chunks, embeddings)
        
        st.success("✅ Knowledge base ready!")
        return vectorstore
        
    except Exception as e:
        st.error(f"❌ Error loading knowledge base: {str(e)}")
        return None

# Load the knowledge base
with st.spinner("🔄 Loading knowledge base..."):
    vectorstore = load_knowledge_base()

if vectorstore:
    # Create QA chain
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    
    # User input
    st.write("---")
    question = st.text_input("💬 Your question:", placeholder="e.g., What is the capital requirement for banks?")
    
    if question:
        with st.spinner("🔍 Searching for answer..."):
            try:
                result = qa_chain({"query": question})
                
                # Display answer
                st.write("### 📝 Answer:")
                st.write(result['result'])
                
                # Display sources
                st.write("### 📚 Sources:")
                for i, doc in enumerate(result['source_documents'], 1):
                    source = doc.metadata.get('source', 'Unknown')
                    page = doc.metadata.get('page', 'N/A')
                    st.write(f"{i}. **{source}** (Page {page})")
                    with st.expander(f"View snippet {i}"):
                        st.write(doc.page_content[:300] + "...")
                
                st.success("✅ Answer generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating answer: {str(e)}")
    
    # Instructions in sidebar
    with st.sidebar:
        st.write("## 📖 Instructions")
        st.write("1. Place PDF files in project folder")
        st.write("2. Name them: doc1.pdf, doc2.pdf, doc3.pdf")
        st.write("3. Add OPENAI_API_KEY to .env file")
        st.write("4. Ask questions!")
        
        st.write("---")
        st.write("## 🔧 Status")
        st.write(f"✅ API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
        st.write(f"✅ PDFs Found: {sum([os.path.exists(f'doc{i}.pdf') for i in range(1,4)])}/3")

else:
    st.error("❌ Failed to load knowledge base. Check the errors above.")