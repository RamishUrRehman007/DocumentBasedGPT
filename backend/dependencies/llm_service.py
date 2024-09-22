import logging
import os
from typing import List, Optional

from langchain.chains.question_answering import load_qa_chain
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai.embeddings.base import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec


class DataLoader:
    def __init__(self, directory: str):
        self.directory = directory

    async def load_data(self) -> List:
        loader = DirectoryLoader(self.directory)
        loaded_docs = await loader.aload()
        return loaded_docs


class DocumentSplitter:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 20):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def split_documents(self, documents: List) -> List:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_documents(documents)


class EmbeddingsProvider:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.model = model

    def get_embeddings(self):
        return OpenAIEmbeddings(
            api_key=self.api_key,
            model=self.model,
        )


class VectorStoreManager:
    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int = 1536,
        env: str = "",
        region: str = "us-east-1",
    ):
        os.environ["PINECONE_API_KEY"] = api_key
        self.index_name = index_name
        self.dimension = dimension
        self.env = env
        self.region = region

    def create_index(self):
        Pinecone().create_index(
            name=self.index_name,
            dimension=self.dimension,
            spec=ServerlessSpec(cloud="aws", region=self.region),
        )

    def delete_existing_vectors(self):
        Pinecone().Index(self.index_name).delete(delete_all=True)

    async def load_vector_store(self, documents: List, embeddings):
        return await PineconeVectorStore.afrom_documents(
            index_name=self.index_name, documents=documents, embedding=embeddings
        )

    def load_existing_store(self, embeddings):
        return PineconeVectorStore.from_existing_index(
            index_name=self.index_name, embedding=embeddings
        )

    async def similarity_search(
        self, query: str, embeddings: List, k: int = 1, with_score: bool = False
    ):
        store = self.load_existing_store(embeddings)
        if with_score:
            return await store.asimilarity_search_with_score(query, k=k)
        else:
            return await store.asimilarity_search(query, k=k)


class QuestionAnsweringService:
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(api_key=api_key, model_name=model_name)
        self.chain = load_qa_chain(self.llm, chain_type="stuff")

    async def get_answer(self, query: str, similar_docs: List):
        return await self.chain.arun(input_documents=similar_docs, question=query)


# Dependency Injection: Decoupling dependencies for better testability and flexibility.
class DocumentGPTSystem:
    def __init__(
        self,
        embeddings_provider: EmbeddingsProvider,
        vector_store_manager: VectorStoreManager,
        data_loader: Optional[DataLoader] = None,
        splitter: Optional[DocumentSplitter] = None,
        qa_service: Optional[QuestionAnsweringService] = None,
    ):
        self.data_loader = data_loader
        self.splitter = splitter
        self.embeddings_provider = embeddings_provider
        self.vector_store_manager = vector_store_manager
        self.qa_service = qa_service

    async def process_files(self):
        logging.info(" === Processing Files === ")

        logging.info("Loading the Documents")
        documents = await self.data_loader.load_data()

        logging.info("Splitting the Documents")
        split_docs = await self.splitter.split_documents(documents)

        logging.info("Loading Embedding model from OpenAI")
        embeddings = self.embeddings_provider.get_embeddings()

        # logging.info("Loading Embedding model from OpenAI")
        self.vector_store_manager.delete_existing_vectors()

        logging.info("Uploading the Vectors to Pinecone")
        return await self.vector_store_manager.load_vector_store(split_docs, embeddings)

    async def process_query(self, query: str):
        embeddings = self.embeddings_provider.get_embeddings()

        self.vector_store_manager.load_existing_store(embeddings)

        similar_docs = await self.vector_store_manager.similarity_search(
            query, embeddings
        )

        answer = await self.qa_service.get_answer(query, similar_docs)

        return f"""

                {answer}
                \n\n
                File: {similar_docs[0].metadata if similar_docs and similar_docs[0].metadata else ""}
                Paragraph: {similar_docs[0].page_content if similar_docs and similar_docs[0].page_content else ""}
                """
