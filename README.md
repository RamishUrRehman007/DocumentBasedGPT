# DocumentBasedGPT

**Please Note**: I have also uploaded a video for Project Setup and System Demo [https://drive.google.com/file/d/1n0Vts2JvijjkDr7PpaR4QXgMH_xbKeID/view?usp=sharing]. Do visit if you have any trouble. You could also contact me at ramish534@outlook.com. I have already added the API keys in the `.env` file, so you don't have to create accounts for them.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![LangChain](https://img.shields.io/badge/LangChain-008080?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai)
![Pinecone](https://img.shields.io/badge/Pinecone-00A9A5?style=for-the-badge&logo=pinecone)

DocumentBasedGPT is a document-based GPT system that answers questions based on internal documents. It provides short, precise, and well-sourced answers by linking users to the specific part of the document where the information was found. The system ensures relevancy by only answering questions related to the document content and includes guardrails to avoid irrelevant or inappropriate responses.

## 🏛 Architecture

This architecture facilitates a robust, scalable, document-based GPT system that can efficiently handle user queries, maintain context, and return relevant information from a vast collection of documents.

![DeploymentDiagram](images/localdeployment.png)

![FileUploadFlow](images/filesUpload.png)

![QAwithGPTFlow](images/QAwithGPT.png)


## 💻 Technologies

- **FastAPI**: Serves as the web framework for building the API.
- **Redis Queue and Pub/Sub**: Used for managing tasks and message brokering.
- **Sockets**: For real-time communication between the client and server.
- **Docker**: Containerizes the application for easy deployment.
- **LangChain**: Manages document embeddings and conversational context.
- **OpenAI LLM**: Powers the intelligence behind the system's document-based responses.
- **Pinecone Vector DB**: Stores document embeddings for efficient search and retrieval of relevant information.

## ⚙️ Few Challenges I Would Like to Mention

1) **Challenge Faced**: Chat handling with QA Agent. When the system scales, we will have more instances, so it becomes hard to deliver messages.
   - **Approach**: Implemented a Redis Pub/Sub to keep track of chat, no matter how many instances we have.

2) **Challenge Faced**: Embedding storage and searching. It's difficult to store and search vectors manually, and loading embeddings every time a user sends a query would be inefficient.
   - **Approach**: Used Pinecone index DB to store vectors and perform similarity search easily.

3) **Challenge Faced**: When uploading multiple large files via API, sometimes the API times out. This also happens during the QA process with GPT, as it can take time to process queries.
   - **Approach**: Implemented a Redis Message Broker to put a request in the queue. The broker sends the request to workers to process the query and upload the files. Once done, it notifies the user using Redis Pub/Sub.

## 🚀 Getting Started

To start using DocumentBasedGPT, follow these steps:

## ✅ Prerequisites

Before you begin, ensure you have installed:

- [Docker](https://www.docker.com/products/docker-desktop)
- [Git](https://git-scm.com/downloads)

## 🔧 Setup and Installation

### ➡️ Step 1: Clone the Repository

1. **Clone the Repository**:
   
    ```bash
    git clone https://[your_username]:[classic_token]@github.com/RamishUrRehman007/DocumentBasedGPT.git
    ```

### ▶️ Step 2: Running the Application


Navigate to the project directory and use Docker Compose to start the application:

1. **Build and Up All Containers**:

    ```
    docker-compose up
    ```
    - Now, review the resources you are about to create, update, or delete to ensure they are what you expect.
    ![Docker Containers](images/docker_containers.PNG)

## 🌐 Accessing the Application

    ```
    http://localhost:8090/
    ```

## File Upload
![File Upload 1](images/file_upload_1.PNG)
![File Upload 2](images/file_upload_2.PNG)
![File Upload 3](images/file_upload_3.PNG)
![File Upload 4](images/file_upload_4.PNG)


## QA
![Chat 1](images/chat_1.PNG)
![Chat 2](images/chat_2.PNG)


## ⏹ Stopping the Application

To stop the application, use `Ctrl+C` in the terminal where Docker Compose is running, or run `docker-compose down` in a separate terminal.

## 🚀 Future Improvements

1) Use PostgreSQL for better file data management and user management with authentication.
2) Implement AWS S3 for file uploading (unfortunately, I did not have my own account this time).
3) Frontend development on modern frameworks like Vue.js.
