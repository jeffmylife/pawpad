"""
Unicode variation selector encoder for hiding data in text.
"""

import secrets
import hashlib
import hmac
import json
from typing import List, Optional, Tuple, Dict, Any
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os


def byte_to_variation_selector(byte: int) -> str:
    """Convert a byte (0-255) to a Unicode variation selector character.

    Uses a standard mapping for variation selectors:
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

    Uses a standard mapping for variation selectors.

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
    """Encode a secret message into text using variation selectors.

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
    """Decode a secret message from text encoded with variation selectors.

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
    """Encode a secret message into a single character using variation selectors.

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


# =============================================================================
# CRYPTOGRAPHIC TAMPERING DETECTION FUNCTIONS
# =============================================================================


def generate_key_pair() -> Tuple[bytes, bytes]:
    """Generate an RSA key pair for signing and verification.

    Returns:
        Tuple of (private_key_pem, public_key_pem) as bytes
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    return private_pem, public_pem


def save_key_pair(
    private_key_pem: bytes,
    public_key_pem: bytes,
    private_key_path: str,
    public_key_path: str,
) -> None:
    """Save key pair to files.

    Args:
        private_key_pem: Private key in PEM format
        public_key_pem: Public key in PEM format
        private_key_path: Path to save private key
        public_key_path: Path to save public key
    """
    with open(private_key_path, "wb") as f:
        f.write(private_key_pem)

    with open(public_key_path, "wb") as f:
        f.write(public_key_pem)


def load_private_key(private_key_path: str) -> bytes:
    """Load private key from file.

    Args:
        private_key_path: Path to private key file

    Returns:
        Private key PEM bytes
    """
    with open(private_key_path, "rb") as f:
        return f.read()


def load_public_key(public_key_path: str) -> bytes:
    """Load public key from file.

    Args:
        public_key_path: Path to public key file

    Returns:
        Public key PEM bytes
    """
    with open(public_key_path, "rb") as f:
        return f.read()


def compute_chained_fingerprint(
    char: str, position: int, previous_fingerprint: bytes, private_key_pem: bytes
) -> bytes:
    """Compute a chained fingerprint for a character.

    Each character's fingerprint depends on:
    - The character itself
    - Its position in the text
    - The previous character's fingerprint (creating the chain)
    - The private key (for authenticity)

    Args:
        char: The character to fingerprint
        position: Position of character in text (0-based)
        previous_fingerprint: Fingerprint of previous character (empty for first char)
        private_key_pem: Private key for signing

    Returns:
        HMAC fingerprint bytes (32 bytes)
    """
    # Create the message to sign
    message_parts = [
        char.encode("utf-8"),
        str(position).encode("utf-8"),
        previous_fingerprint,
    ]
    message = b"|".join(message_parts)

    # Use the private key as HMAC key (simplified approach)
    # In practice, you might derive a signing key from the private key
    return hmac.new(private_key_pem, message, hashlib.sha256).digest()


def sign_text_with_chained_fingerprints(text: str, private_key_pem: bytes) -> str:
    """Sign text using chained fingerprints for tampering detection.

    Each character gets a unique fingerprint that depends on:
    - The character itself
    - Its position in the text
    - The previous character's fingerprint (creating the chain)
    - The private key (for authenticity)

    Args:
        text: Original text to sign
        private_key_pem: Private key for signing

    Returns:
        Text with chained fingerprints encoded as variation selectors
    """
    if not text:
        return text

    result = ""
    previous_fingerprint = b""

    for position, char in enumerate(text):
        # Compute chained fingerprint for this character
        fingerprint = compute_chained_fingerprint(
            char, position, previous_fingerprint, private_key_pem
        )

        # Encode the fingerprint as variation selectors after the character
        signed_char = encode_bytes_in_char(char, fingerprint)
        result += signed_char

        # This fingerprint becomes the previous one for the next character
        previous_fingerprint = fingerprint

    return result


def verify_chained_fingerprints(
    signed_text: str, private_key_pem: bytes
) -> Dict[str, Any]:
    """Verify chained fingerprints and detect tampering.

    Note: This function requires the private key to re-compute expected fingerprints
    and compare them with the actual fingerprints in the text.

    Args:
        signed_text: Text with chained fingerprints
        private_key_pem: Private key used for signing (needed for verification)

    Returns:
        Dictionary with verification results:
        {
            'is_valid': bool,
            'original_text': str,
            'tampered_positions': List[int],
            'tampered_characters': List[str],
            'analysis': str
        }
    """
    # Extract characters and their fingerprints
    characters = []
    fingerprints = []

    i = 0
    while i < len(signed_text):
        # Find the base character
        base_char = signed_text[i]

        # Find all variation selectors following this character
        j = i + 1
        while j < len(signed_text) and is_variation_selector(signed_text[j]):
            j += 1

        if j > i + 1:
            # Extract the fingerprint from variation selectors
            segment = signed_text[i:j]
            fingerprint = decode_bytes_from_char(segment)
            characters.append(base_char)
            fingerprints.append(fingerprint)
        else:
            # Character without fingerprint - this is suspicious
            characters.append(base_char)
            fingerprints.append(b"")

        i = j if j > i + 1 else i + 1

    # Now verify the chain by re-computing expected fingerprints
    original_text = "".join(characters)
    tampered_positions = []
    tampered_characters = []

    previous_fingerprint = b""

    for position, (char, actual_fingerprint) in enumerate(
        zip(characters, fingerprints)
    ):
        if not actual_fingerprint:
            # Missing fingerprint
            tampered_positions.append(position)
            tampered_characters.append(char)
            continue

        # Compute what the fingerprint SHOULD be
        expected_fingerprint = compute_chained_fingerprint(
            char, position, previous_fingerprint, private_key_pem
        )

        # Compare with actual fingerprint
        if actual_fingerprint != expected_fingerprint:
            tampered_positions.append(position)
            tampered_characters.append(char)
            # Use the actual fingerprint for next iteration to continue chain
            previous_fingerprint = actual_fingerprint
        else:
            # Valid fingerprint - use it for next iteration
            previous_fingerprint = expected_fingerprint

    is_valid = len(tampered_positions) == 0

    if is_valid:
        analysis = f"✓ Text integrity verified. All {len(characters)} characters have valid signatures."
    else:
        analysis = f"✗ Tampering detected! {len(tampered_positions)} characters have invalid signatures at positions: {tampered_positions}"

    return {
        "is_valid": is_valid,
        "original_text": original_text,
        "tampered_positions": tampered_positions,
        "tampered_characters": tampered_characters,
        "analysis": analysis,
        "total_characters": len(characters),
        "signed_characters": len([f for f in fingerprints if f]),
    }


def extract_original_text_from_signed(signed_text: str) -> str:
    """Extract the original text from signed text by removing variation selectors.

    Args:
        signed_text: Text with chained fingerprints

    Returns:
        Original text without variation selectors
    """
    result = ""
    i = 0

    while i < len(signed_text):
        # Add the base character
        result += signed_text[i]

        # Skip all variation selectors
        i += 1
        while i < len(signed_text) and is_variation_selector(signed_text[i]):
            i += 1

    return result
