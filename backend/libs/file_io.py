class FileIO:
    @staticmethod
    async def read(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    @staticmethod
    async def write(file_path, content):
        with open(file_path, "w", encoding="utf-8") as file:
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
