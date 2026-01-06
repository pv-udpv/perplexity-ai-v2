"""
UUID generation utilities
"""

from uuid import uuid4


def generate_uuid() -> str:
    """Generate random UUID v4

    Returns:
        UUID string
    """
    return str(uuid4())


def generate_device_id() -> str:
    """Generate iOS device ID

    Returns:
        Device ID in iOS format
    """
    return f"ios:{uuid4()}"
