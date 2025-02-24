"""
Business Exceptions Module

This module defines custom exceptions for handling business logic errors 
in a structured manner. Each exception is designed to be raised at the 
service layer and mapped to appropriate HTTP responses in the router layer.

Best Practices:
- Raise these exceptions in the service layer instead of HTTPException.
- Convert them to HTTP exceptions in the router/controller layer.
- Keep exceptions framework-agnostic for better reusability.

Author: Zafar Hussain Luni
Version: 1.0.0
"""


# ========================
# General Exceptions
# ========================

class ResourceNotFoundException(Exception):
    """
    Raised when a requested resource is not found.

    Args:
        resource_name (str): The name of the resource (e.g., "Category", "Agent").
        resource_id (int): The unique ID of the resource.

    Attributes:
        resource_name (str): The name of the resource.
        resource_id (int): The unique ID of the resource.
    """

    def __init__(self, resource_name: str, resource_id: int) -> None:
        super().__init__(f"{resource_name} with ID {resource_id} not found.")
        self.resource_name = resource_name
        self.resource_id = resource_id


class DuplicateResourceException(Exception):
    """
    Raised when trying to create a duplicate resource.

    Args:
        resource_name (str): The name of the resource (e.g., "Category", "Agent").
        identifier (str): The unique identifier (e.g., name or ID).

    Attributes:
        resource_name (str): The name of the resource.
        identifier (str): The unique identifier.
    """

    def __init__(self, resource_name: str, identifier: str) -> None:
        super().__init__(f"{resource_name} '{identifier}' already exists.")
        self.resource_name = resource_name
        self.identifier = identifier


class PermissionDeniedException(Exception):
    """
    Raised when a user tries to access a resource they do not have permission for.

    Args:
        message (str, optional): Custom error message. Defaults to a generic permission error.
    """

    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(message)


class InvalidInputException(Exception):
    """
    Raised when an invalid input is provided.

    Args:
        message (str, optional): Custom error message. Defaults to a generic input error.
    """

    def __init__(self, message: str = "Invalid input provided.") -> None:
        super().__init__(message)


# ========================
# Category-Specific Exceptions
# ========================

class CategoryNotFoundException(ResourceNotFoundException):
    """
    Raised when a category is not found in the database.

    Args:
        category_id (int): The unique ID of the category.
    """

    def __init__(self, category_id: int) -> None:
        super().__init__("Category", category_id)


class DuplicateCategoryException(DuplicateResourceException):
    """
    Raised when a category with the same name already exists.

    Args:
        name (str): The category name.
    """

    def __init__(self, name: str) -> None:
        super().__init__("Category", name)


# ========================
# Agent-Specific Exceptions
# ========================

class AgentNotFoundException(ResourceNotFoundException):
    """
    Raised when an agent is not found in the database.

    Args:
        agent_id (int): The unique ID of the agent.
    """

    def __init__(self, agent_id: int) -> None:
        super().__init__("Agent", agent_id)


class DuplicateAgentException(DuplicateResourceException):
    """
    Raised when an agent with the same name already exists.

    Args:
        name (str): The agent name.
    """

    def __init__(self, name: str) -> None:
        super().__init__("Agent", name)


class UnauthorizedAgentAccessException(PermissionDeniedException):
    """
    Raised when a user tries to access or modify an agent they do not own.
    """

    def __init__(self) -> None:
        super().__init__("You do not have permission to modify this agent.")


class AgentFileUploadException(Exception):
    """
    Raised when an error occurs during file upload.

    Args:
        message (str, optional): Custom error message. Defaults to "File upload failed."
    """

    def __init__(self, message: str = "File upload failed.") -> None:
        super().__init__(message)


# ========================
# File-Specific Exceptions
# ========================

class FileNotFoundException(ResourceNotFoundException):
    """
    Raised when a requested file is not found.

    Args:
        file_id (int): The unique ID of the file.
    """

    def __init__(self, file_id: int) -> None:
        super().__init__("File", file_id)


class FileUploadException(Exception):
    """
    Raised when a file upload fails.

    Args:
        message (str, optional): Custom error message. Defaults to "File upload failed."
    """

    def __init__(self, message: str = "File upload failed.") -> None:
        super().__init__(message)


class UnsupportedFileTypeException(Exception):
    """
    Raised when an unsupported file type is uploaded.

    Args:
        file_type (str): The file type that was rejected.
    """

    def __init__(self, file_type: str) -> None:
        super().__init__(f"Unsupported file type: {file_type}")


# ========================
# Chat & LLM-Specific Exceptions
# ========================

class LLMProviderNotFoundException(Exception):
    """
    Raised when an LLM provider is not found.

    Args:
        provider_name (str): The name of the missing provider.
    """

    def __init__(self, provider_name: str) -> None:
        super().__init__(f"LLM provider '{provider_name}' not found.")


class LLMResponseException(Exception):
    """
    Raised when an error occurs while generating a response from an LLM.

    Args:
        message (str, optional): Custom error message. Defaults to "Failed to generate response from LLM."
    """

    def __init__(self, message: str = "Failed to generate response from LLM.") -> None:
        super().__init__(message)


class InvalidPromptException(Exception):
    """
    Raised when an invalid prompt is sent to the LLM.

    Args:
        message (str, optional): Custom error message. Defaults to "Invalid prompt format."
    """

    def __init__(self, message: str = "Invalid prompt format.") -> None:
        super().__init__(message)


# ========================
# Database & Infrastructure Exceptions
# ========================

class DatabaseException(Exception):
    """
    Raised when a database error occurs.

    Args:
        message (str, optional): Custom error message. Defaults to "A database error occurred."
    """

    def __init__(self, message: str = "A database error occurred.") -> None:
        super().__init__(message)


class TransactionRollbackException(DatabaseException):
    """
    Raised when a transaction fails and is rolled back.
    """

    def __init__(self) -> None:
        super().__init__("Database transaction failed and was rolled back.")
