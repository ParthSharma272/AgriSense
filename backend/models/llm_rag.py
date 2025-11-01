"""
RAG (Retrieval-Augmented Generation) Pipeline Implementation
"""
import logging
from typing import List, Dict, Optional, Any
import pandas as pd
from pathlib import Path

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for AgriSense
    Combines vector search with LLM reasoning
    """
    
    def __init__(
        self,
        hf_token: str,
        hf_model: str = "mistralai/Mixtral-8x7B-Instruct-v0.1",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        chroma_persist_dir: str = "./chroma_db",
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ):
        """
        Initialize RAG pipeline
        
        Args:
            hf_token: Hugging Face API token
            hf_model: Model name for text generation
            embedding_model: Model for creating embeddings
            chroma_persist_dir: Directory to persist vector store
            top_k: Number of results to retrieve
            similarity_threshold: Minimum similarity score
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Initialize Chroma vector database
        logger.info(f"Initializing Chroma DB at {chroma_persist_dir}")
        self.chroma_client = chromadb.Client(Settings(
            persist_directory=chroma_persist_dir,
            anonymized_telemetry=False
        ))
        
        # Initialize Hugging Face Inference Client
        logger.info(f"Initializing HF Inference Client with model: {hf_model}")
        self.llm_client = InferenceClient(model=hf_model, token=hf_token)
        self.hf_model = hf_model
        
        # Collections
        self.collections = {}
    
    def create_collection(self, collection_name: str, recreate: bool = False):
        """
        Create or get a collection in the vector store
        
        Args:
            collection_name: Name of the collection
            recreate: If True, delete existing collection and create new
        """
        try:
            if recreate:
                try:
                    self.chroma_client.delete_collection(name=collection_name)
                    logger.info(f"Deleted existing collection: {collection_name}")
                except:
                    pass
            
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.collections[collection_name] = collection
            logger.info(f"Collection '{collection_name}' ready")
            return collection
            
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            raise
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict]] = None,
        collection_name: str = "gov_datasets",
        ids: Optional[List[str]] = None
    ):
        """
        Add documents to the vector store
        
        Args:
            documents: List of text documents
            metadatas: Optional metadata for each document
            collection_name: Name of collection to add to
            ids: Optional custom IDs for documents
        """
        try:
            # Get or create collection
            if collection_name not in self.collections:
                self.create_collection(collection_name)
            
            collection = self.collections[collection_name]
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(documents)} documents")
            embeddings = self.embedder.encode(documents, show_progress_bar=True)
            
            # Generate IDs if not provided
            if ids is None:
                existing_count = collection.count()
                ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
            
            # Add to collection
            collection.add(
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} documents to {collection_name}")
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def add_dataframe(
        self,
        df: pd.DataFrame,
        text_column: str,
        metadata_columns: Optional[List[str]] = None,
        collection_name: str = "gov_datasets",
        dataset_name: str = "unknown"
    ):
        """
        Add a DataFrame to the vector store
        
        Args:
            df: DataFrame to add
            text_column: Column containing text to embed
            metadata_columns: Additional columns to store as metadata
            collection_name: Name of collection
            dataset_name: Name of the dataset for metadata
        """
        documents = df[text_column].astype(str).tolist()
        
        metadatas = []
        for idx, row in df.iterrows():
            metadata = {"dataset": dataset_name, "row_id": str(idx)}
            
            if metadata_columns:
                for col in metadata_columns:
                    if col in df.columns:
                        metadata[col] = str(row[col])
            
            metadatas.append(metadata)
        
        self.add_documents(documents, metadatas, collection_name)
    
    def query(
        self,
        query_text: str,
        collection_name: str = "gov_datasets",
        n_results: Optional[int] = None,
        filter_dict: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Query the vector store
        
        Args:
            query_text: Query string
            collection_name: Collection to search
            n_results: Number of results (defaults to top_k)
            filter_dict: Optional metadata filters
            
        Returns:
            Dictionary with results
        """
        try:
            if collection_name not in self.collections:
                self.create_collection(collection_name)
            
            collection = self.collections[collection_name]
            n_results = n_results or self.top_k
            
            # Generate query embedding
            query_embedding = self.embedder.encode([query_text])[0]
            
            # Query collection
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=filter_dict
            )
            
            # Filter by similarity threshold
            filtered_results = {
                'documents': [],
                'metadatas': [],
                'distances': [],
                'ids': []
            }
            
            for i, distance in enumerate(results['distances'][0]):
                similarity = 1 - distance  # Convert distance to similarity
                
                if similarity >= self.similarity_threshold:
                    filtered_results['documents'].append(results['documents'][0][i])
                    filtered_results['metadatas'].append(results['metadatas'][0][i])
                    filtered_results['distances'].append(distance)
                    filtered_results['ids'].append(results['ids'][0][i])
            
            logger.info(f"Retrieved {len(filtered_results['documents'])} relevant documents")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error querying collection: {e}")
            return {'documents': [], 'metadatas': [], 'distances': [], 'ids': []}
    
    def generate_response(
        self,
        query: str,
        context: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        include_reasoning: bool = True
    ) -> str:
        """
        Generate response using LLM with context
        
        Args:
            query: User's question
            context: Retrieved context
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            include_reasoning: Whether to include reasoning chain
            
        Returns:
            Generated response
        """
        try:
            # Construct prompt
            if include_reasoning:
                prompt = f"""You are AgriSense 2.0, an intelligent agricultural analysis system for India.

Context from government datasets:
{context}

User Question: {query}

Instructions:
1. Answer the question using ONLY the data provided in the context
2. Show your reasoning process step by step
3. If the data shows trends or correlations, explain them
4. Cite specific data points (states, years, values) to support your answer
5. If the context doesn't contain enough information, say so clearly
6. Suggest policy insights if relevant

Answer with reasoning:"""
            else:
                prompt = f"""Context: {context}

Question: {query}

Answer clearly and concisely based only on the provided context:"""
            
            # Generate response
            response = self.llm_client.text_generation(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                return_full_text=False
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"Error generating response: {str(e)}"
    
    def rag_query(
        self,
        query: str,
        collection_name: str = "gov_datasets",
        include_reasoning: bool = True,
        n_results: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve context and generate response
        
        Args:
            query: User's question
            collection_name: Collection to search
            include_reasoning: Whether to include reasoning
            n_results: Number of documents to retrieve
            
        Returns:
            Dictionary with response and metadata
        """
        # Retrieve relevant documents
        retrieval_results = self.query(query, collection_name, n_results)
        
        if not retrieval_results['documents']:
            return {
                'answer': "I couldn't find relevant information in the available datasets to answer this question.",
                'sources': [],
                'context': '',
                'confidence': 0.0
            }
        
        # Combine retrieved documents into context
        context_parts = []
        for i, (doc, metadata) in enumerate(zip(
            retrieval_results['documents'],
            retrieval_results['metadatas']
        ), 1):
            dataset = metadata.get('dataset', 'Unknown')
            context_parts.append(f"[Source {i} - {dataset}]\n{doc}\n")
        
        context = "\n".join(context_parts)
        
        # Generate response
        answer = self.generate_response(query, context, include_reasoning=include_reasoning)
        
        # Calculate average confidence
        if retrieval_results['distances']:
            avg_distance = sum(retrieval_results['distances']) / len(retrieval_results['distances'])
            confidence = 1 - avg_distance
        else:
            confidence = 0.0
        
        return {
            'answer': answer,
            'sources': retrieval_results['metadatas'],
            'context': context,
            'confidence': float(confidence),
            'num_sources': len(retrieval_results['documents'])
        }
