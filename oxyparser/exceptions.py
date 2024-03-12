class FailedOpenAIException(Exception):
    """
    Custom exception to indicate some failure after accessing OpenAI
    """


class FailedOxylabsRequestException(Exception):
    """
    Custom exception to indicate some failure after accessing Oxylabs
    """


class ValidationException(Exception):
    """
    Custom exception to indicate some failure in validation
    """


class EmptyBodyException(Exception):
    """
    Custom exception to indicate empty body
    """
