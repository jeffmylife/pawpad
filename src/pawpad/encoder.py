"""
Unicode variation selector encoder for hiding data in text.
"""

import secrets
import hashlib
from typing import List, Optional


def byte_to_variation_selector(byte: int) -> str:
    """Convert a byte (0-255) to a Unicode variation selector character.

    Uses the exact same mapping as Paul Butler's emoji-encoder:
    - VS1..=VS16 (0xFE00-0xFE0F) for bytes 0-15
    - VS17..=VS256 (0xE0100-0xE01EF) for bytes 16-255

    Args:
        byte: Integer between 0 and 255

    Returns:
        Unicode variation selector character
    """
    if 0 <= byte < 16:
        return chr(0xFE00 + byte)
    elif 16 <= byte < 256:
        return chr(0xE0100 + byte - 16)
    else:
        raise ValueError(f"Byte value {byte} out of range (0-255)")


def variation_selector_to_byte(char: str) -> Optional[int]:
    """Convert a Unicode variation selector character back to a byte.

    Uses the exact same mapping as Paul Butler's emoji-encoder.

    Args:
        char: Unicode variation selector character

    Returns:
        Byte value (0-255) or None if not a variation selector
    """
    code_point = ord(char)

    if 0xFE00 <= code_point <= 0xFE0F:
        return code_point - 0xFE00
    elif 0xE0100 <= code_point <= 0xE01EF:
        return code_point - 0xE0100 + 16
    else:
        return None


def is_variation_selector(char: str) -> bool:
    """Check if a character is a variation selector we use.

    Args:
        char: Character to check

    Returns:
        True if it's a variation selector in our ranges
    """
    code_point = ord(char)
    return (0xFE00 <= code_point <= 0xFE0F) or (0xE0100 <= code_point <= 0xE01EF)


def encode_bytes_in_char(base_char: str, data: bytes) -> str:
    """Encode bytes as variation selectors after a base character.

    Args:
        base_char: The base character to attach variation selectors to
        data: Bytes to encode

    Returns:
        String with base character followed by variation selectors
    """
    result = base_char
    for byte in data:
        result += byte_to_variation_selector(byte)
    return result


def decode_bytes_from_char(text: str) -> bytes:
    """Decode bytes from variation selectors in text.

    Args:
        text: Text containing variation selectors

    Returns:
        Decoded bytes
    """
    result = []
    found_first_vs = False
    base_char_found = False
    i = 0

    while i < len(text):
        char = text[i]

        if is_variation_selector(char):
            found_first_vs = True
            # Each variation selector represents one byte
            byte_val = variation_selector_to_byte(char)
            if byte_val is not None:
                result.append(byte_val)
            i += 1
        elif not base_char_found and not found_first_vs:
            # This is the base character, skip it
            base_char_found = True
            i += 1
        elif found_first_vs:
            # Stop at first non-variation selector after we've found some
            break
        else:
            i += 1

    return bytes(result)


def generate_fingerprint(length: int = 16) -> bytes:
    """Generate a random fingerprint.

    Args:
        length: Length of fingerprint in bytes

    Returns:
        Random bytes for fingerprint
    """
    return secrets.token_bytes(length)


def fingerprint_to_string(fingerprint: bytes) -> str:
    """Convert fingerprint bytes to a hex string.

    Args:
        fingerprint: Fingerprint bytes

    Returns:
        Hex string representation
    """
    return fingerprint.hex()


def string_to_fingerprint(hex_string: str) -> bytes:
    """Convert hex string back to fingerprint bytes.

    Args:
        hex_string: Hex string representation

    Returns:
        Fingerprint bytes
    """
    return bytes.fromhex(hex_string)


def encode_fingerprint_in_text(text: str, fingerprint: bytes) -> str:
    """Encode a fingerprint into every character of the text.

    Args:
        text: Original text
        fingerprint: Fingerprint bytes to encode

    Returns:
        Text with fingerprint encoded in each character
    """
    result = ""
    for char in text:
        result += encode_bytes_in_char(char, fingerprint)
    return result


def detect_fingerprint_in_text(text: str, expected_fingerprint: bytes) -> bool:
    """Detect if a specific fingerprint is present in the text.

    Args:
        text: Text to check
        expected_fingerprint: Fingerprint to look for

    Returns:
        True if fingerprint is detected, False otherwise
    """
    # We need to find sequences of base_char + variation_selectors
    i = 0
    while i < len(text):
        # Start from current position and look for variation selectors
        j = i + 1
        while j < len(text) and is_variation_selector(text[j]):
            j += 1

        # If we found variation selectors, decode this segment
        if j > i + 1:
            segment = text[i:j]
            decoded = decode_bytes_from_char(segment)
            if decoded == expected_fingerprint:
                return True

        i += 1

    return False


def extract_fingerprint_from_text(text: str) -> Optional[bytes]:
    """Extract the first fingerprint found in the text.

    Args:
        text: Text to extract fingerprint from

    Returns:
        First fingerprint found, or None if no fingerprint detected
    """
    # We need to find sequences of base_char + variation_selectors
    i = 0
    while i < len(text):
        # Start from current position and look for variation selectors
        j = i + 1
        while j < len(text) and is_variation_selector(text[j]):
            j += 1

        # If we found variation selectors, decode this segment
        if j > i + 1:
            segment = text[i:j]
            decoded = decode_bytes_from_char(segment)
            if decoded:
                return decoded

        i += 1

    return None


def encode_message_in_text(text: str, message: str) -> str:
    """Encode a secret message into text using Paul Butler's approach.

    Distributes the message bytes across the available characters in the text.
    Each character gets a portion of the message encoded as variation selectors.

    Args:
        text: Original text to encode message into
        message: Secret message to encode

    Returns:
        Text with secret message encoded
    """
    if not text:
        return text

    message_bytes = message.encode("utf-8")

    # If message is longer than available characters, we'll cycle through
    chars_list = list(text)
    result = []

    # Distribute message bytes across characters
    bytes_per_char = len(message_bytes) // len(chars_list)
    remaining_bytes = len(message_bytes) % len(chars_list)

    byte_index = 0
    for i, char in enumerate(chars_list):
        # Calculate how many bytes this character should get
        char_byte_count = bytes_per_char
        if i < remaining_bytes:
            char_byte_count += 1

        # Get the bytes for this character
        char_bytes = message_bytes[byte_index : byte_index + char_byte_count]
        byte_index += char_byte_count

        # Encode these bytes into this character
        encoded_char = encode_bytes_in_char(char, char_bytes)
        result.append(encoded_char)

    return "".join(result)


def decode_message_from_text(text: str) -> str:
    """Decode a secret message from text encoded with Paul Butler's approach.

    Args:
        text: Text containing encoded secret message

    Returns:
        Decoded secret message, or empty string if no message found
    """
    message_bytes = []

    # Extract bytes from each character group
    i = 0
    while i < len(text):
        # Find the next sequence of base_char + variation_selectors
        j = i + 1
        while j < len(text) and is_variation_selector(text[j]):
            j += 1

        # If we found variation selectors, decode this segment
        if j > i + 1:
            segment = text[i:j]
            decoded_bytes = decode_bytes_from_char(segment)
            message_bytes.extend(decoded_bytes)
            i = j
        else:
            i += 1

    if not message_bytes:
        return ""

    try:
        return bytes(message_bytes).decode("utf-8", errors="ignore")
    except:
        return ""


def encode_message_in_single_char(base_char: str, message: str) -> str:
    """Encode a secret message into a single character (Paul Butler's exact approach).

    Args:
        base_char: The base character to attach variation selectors to
        message: Secret message to encode

    Returns:
        Single character with message encoded as variation selectors
    """
    message_bytes = message.encode("utf-8")
    return encode_bytes_in_char(base_char, message_bytes)


def decode_message_from_single_char(encoded_char: str) -> str:
    """Decode a secret message from a single encoded character.

    Args:
        encoded_char: Character with encoded message

    Returns:
        Decoded secret message, or empty string if no message found
    """
    decoded_bytes = decode_bytes_from_char(encoded_char)
    if not decoded_bytes:
        return ""

    try:
        return decoded_bytes.decode("utf-8", errors="ignore")
    except:
        return ""
