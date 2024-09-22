class DocumentBasedGPTError(Exception):
    def __init__(self, message: str = "", custom_error_code: str = ""):
        super().__init__(message)
        self.custom_error_code = custom_error_code
        self.message = message


class DuplicateEntityError(DocumentBasedGPTError):
    def __init__(self, message: str = ""):
        super().__init__(message, custom_error_code="entity-duplicate")


class EntityNotFoundError(DocumentBasedGPTError):
    def __init__(self, message: str = ""):
        super().__init__(message, custom_error_code="entity-not-found")


class BadRequestError(DocumentBasedGPTError):
    def __init__(self, message: str = ""):
        super().__init__(message, custom_error_code="bad-request")


class UnsupportedMediaTypeError(DocumentBasedGPTError):
    def __init__(self, message: str = ""):
        super().__init__(message, custom_error_code="unsupported-media-type")


class DuplicateFileError(DuplicateEntityError):
    def __init__(self, message: str = ""):
        super(DuplicateEntityError, self).__init__(
            message, custom_error_code="file-duplicate"
        )


class FileNotFoundError(EntityNotFoundError):
    def __init__(self, message: str = ""):
        super(EntityNotFoundError, self).__init__(
            message, custom_error_code="file-not-found"
        )


class FileSizeError(DocumentBasedGPTError):
    def __init__(self, message: str = ""):
        super(BadRequestError, self).__init__(
            message, custom_error_code="unsupported-file-size"
        )
