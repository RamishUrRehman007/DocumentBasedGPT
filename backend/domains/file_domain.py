import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import List, Optional

import dto
from config import OPEN_AI_API_KEY, PINECONE_API_KEY
from constants import (
    FILE_STATUS_COMPLETED,
    FILE_STATUS_PROCESSING,
    MAX_UPLOAD_SIZE_LIMIT,
    SUPPORTED_FILE_EXTENSION,
)
from dependencies.llm_service import (
    DataLoader,
    DocumentGPTSystem,
    DocumentSplitter,
    EmbeddingsProvider,
    VectorStoreManager,
)
from domains.common import push_new_job
from exceptions import FileSizeError
from libs.file_io import FileIO

json_data_path = f"{os.getcwd()}/backend/uploads/meta_data/file_data.json"


async def create_file(
    files: dto.Any,
) -> dto.FileUploadResponse:
    files_data = []
    # for safe side delete existing files
    await FileIO.delete_all_files(f"{os.getcwd()}/backend/uploads/files/")
    await FileIO.delete_all_files(f"{os.getcwd()}/backend/uploads/meta_data/")

    for file in files:
        file_extension = file.filename.split(".")[-1].lower()
        contents = await file.read()

        file_size = len(contents)

        # Validate file size using Content-Length
        await _validate_file_size(file_size)
        file_hash = await _calculate_sha256(contents)

        file_path = f"{os.getcwd()}/backend/uploads/files/{file.filename}"

        # logging.info(f"File Contents: {contents}")

        if file_extension == "pdf":
            logging.info("PDF File")
            decoded_contents = contents
        else:
            logging.info("Not PDF File")
            decoded_contents = contents.decode("utf-8", errors="replace")

        await FileIO.write(file_path, decoded_contents)

        logging.info(
            f" File Creating in DB with file_name: {file.filename}, file_path: {file_path}"
        )

        files_data.append(
            dto.File(
                file_name=file.filename,
                mime_type=file_extension,
                file_size=file_size,
                file_path=file_path,
                file_hash=file_hash,
            )
        )

    file_upload_response = dto.FileUploadResponse(
        message="Files are Uploaded Successfully Now Being Processed for Embeddings",
        files=files_data,
        status=FILE_STATUS_PROCESSING,
    )

    # Writing Meta Data for a file, we could also utilize DB but for the Test Project I am using here json
    await FileIO.write(json_data_path, file_upload_response.model_dump_json())

    # Pushing Job to Redis Broker
    await push_new_job("process_files")

    return file_upload_response


async def file_status() -> Optional[dto.FileStatus]:
    """"""
    json_data = await FileIO.read(json_data_path)
    json_data = json.loads(json_data)

    if "status" in json_data:
        return dto.FileStatus(status=json_data["status"])

    return None


async def find_many() -> List[dto.File]:
    """"""
    json_data = await FileIO.read(json_data_path)
    json_data = json.loads(json_data)

    return json_data


# Helper to validate file size using Content-Length
async def _validate_file_size(content_length: int):
    if content_length == 0:
        logging.error("Uploaded file is empty. Please upload a valid file.")
        raise FileSizeError("Uploaded file is empty. Please upload a valid file.")

    if content_length > MAX_UPLOAD_SIZE_LIMIT:
        logging.error(
            f"File size exceeds the allowed limit: {content_length} > {MAX_UPLOAD_SIZE_LIMIT} bytes"
        )
        raise FileSizeError(
            f"File size exceeds the allowed limit: {content_length} > {MAX_UPLOAD_SIZE_LIMIT} bytes"
        )


async def _calculate_sha256(file_bytes):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(file_bytes)
    return sha256_hash.hexdigest()


async def _construct_path(file_name: str):
    today = datetime.now(tz=timezone.utc)
    current_date = today.strftime("%    Y-%m-%d")

    constructed_path = f"{current_date}/{file_name}"
    return constructed_path


async def process_files():
    """"""
    # nltk punkt lookup/download
    await _nltk_punkt_data()

    # calling all dependencies

    directory = f"{os.getcwd()}/uploads/files"
    json_data_path = f"{os.getcwd()}/uploads/meta_data/file_data.json"

    api_key_openai = OPEN_AI_API_KEY
    api_key_pinecone = PINECONE_API_KEY

    data_loader = DataLoader(directory)
    splitter = DocumentSplitter()
    embeddings_provider = EmbeddingsProvider(api_key=api_key_openai)
    vector_store_manager = VectorStoreManager(
        api_key=api_key_pinecone, index_name="ramishtest1"
    )

    file_processed = await DocumentGPTSystem(
        data_loader=data_loader,
        splitter=splitter,
        embeddings_provider=embeddings_provider,
        vector_store_manager=vector_store_manager,
    ).process_files()

    if file_processed:
        logging.info("Updating the Files Status")
        file_meta_data = await FileIO.read(json_data_path)
        file_meta_data = json.loads(file_meta_data)

        if "status" in file_meta_data:
            file_meta_data["status"] = FILE_STATUS_COMPLETED

        await FileIO.write(json_data_path, json.dumps(file_meta_data))


async def _nltk_punkt_data():
    import nltk

    # Set NLTK data path if necessary
    nltk.data.path.append("/usr/local/nltk_data")

    # Programmatically download both punkt and averaged_perceptron_tagger
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", download_dir="/usr/local/nltk_data")

    try:
        nltk.data.find("taggers/averaged_perceptron_tagger_eng")
    except LookupError:
        nltk.download(
            "averaged_perceptron_tagger_eng", download_dir="/usr/local/nltk_data"
        )
