class FileIO:
    @staticmethod
    async def read(file_path):
        # Get file extension
        import os

        _, file_extension = os.path.splitext(file_path)

        # Handle PDF files (binary mode)
        if file_extension.lower() == ".pdf":
            with open(file_path, "rb") as file:
                return file.read()  # Return binary content

        # Handle Text and DOC files (text mode)
        elif file_extension.lower() in [".txt", ".doc", ".docx", ".json"]:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()  # Return text content

        # Raise an error for unsupported file types
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    @staticmethod
    async def write(file_path, content):
        mode = "wb" if isinstance(content, bytes) else "w"
        with open(file_path, mode) as file:
            file.write(content)

    @staticmethod
    async def append(file_path, content):
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(content)

    @staticmethod
    async def delete(file_path):
        import os

        try:
            os.remove(file_path)
            print(f"File {file_path} deleted successfully.")
        except OSError as e:
            print(f"Error: {e.strerror}. File {file_path} could not be deleted.")

    @staticmethod
    async def delete_all_files(directory_path):
        import os
        import shutil

        # Check if the directory exists
        if os.path.exists(directory_path) and os.path.isdir(directory_path):
            # List all files and directories inside the directory
            for filename in os.listdir(directory_path):
                file_path = os.path.join(directory_path, filename)
                try:
                    # Check if it's a file and delete it
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    # If it's a directory, use shutil.rmtree() to delete it and its contents
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        else:
            print(
                f"The directory {directory_path} does not exist or is not a directory."
            )
