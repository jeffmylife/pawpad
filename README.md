# 🐾 PawPad - Unicode Steganography Tool

PawPad is a Python tool that uses Unicode variation selectors to encode fingerprints (hidden data) into text. The encoded text looks identical to the original but contains invisible data that can be detected and extracted.

## How It Works

PawPad uses Unicode variation selectors (U+FE00-FE0F and U+E0100-E01EF) to encode data. These characters are invisible when rendered but are preserved during copy/paste operations. The tool supports two main modes:

### 1. **Fingerprinting Mode** (Basic)
- Encodes a fingerprint into every character of the input text
- Detects whether text contains a specific fingerprint  
- Extracts fingerprints from encoded text
- Analyzes text to show hidden data

### 2. **Cryptographic Tampering Detection** (Advanced) 🔒
- Uses chained cryptographic fingerprints for bulletproof tampering detection
- Each character gets a unique signature based on:
  - The character itself
  - Its position in the text
  - The previous character's fingerprint (creating an unbreakable chain)
  - Your private key (for authenticity)
- **Any change to ANY character breaks the entire chain**
- Provides forensic analysis of exactly what was tampered with

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pawpad

# Install using uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

## 🌐 Web UI

PawPad includes a modern web interface for interactive demonstrations:

```bash
# Install web UI dependencies
uv add fastapi uvicorn jinja2 python-multipart

# Start the web server
python web_ui.py

# Open http://localhost:8000 in your browser
```

The web UI provides:
- **Interactive demos** of all PawPad features
- **Real-time encoding/decoding** with visual feedback
- **Copy-paste workflow** that handles Unicode correctly
- **Tabbed interface** for easy navigation
- **Professional design** perfect for demonstrations

See [WEB_UI_DEMO.md](WEB_UI_DEMO.md) for detailed usage instructions.

## Examples

The `examples/` folder contains demonstration files for easy testing:

```bash
# Basic fingerprinting demo
cd examples/basic && ./demo.sh

# Message hiding demo  
cd examples/messages && ./demo.sh

# Cryptographic signing demo
cd examples/crypto && ./simple_demo.sh
```

All examples use file-based input/output to avoid Unicode copy-paste issues.

## Usage

### Basic Fingerprinting

```bash
# Encode text with a random fingerprint
pawpad encode --text "Hello, World"

# Encode with a specific fingerprint
pawpad encode --text "Hello, World" --fingerprint "deadbeef"

# File-based workflow (recommended to avoid copy/paste issues)
pawpad encode --input-file document.txt --output-file encoded.txt --fingerprint "deadbeef"

# Decode/extract fingerprint from text
pawpad decode --input-file encoded.txt --fingerprint "deadbeef"

# Generate a random fingerprint
pawpad generate --length 16

# Analyze text for hidden data
pawpad analyze --input-file suspicious.txt
```

### 🔒 Cryptographic Tampering Detection

```bash
# Generate RSA key pair for signing
pawpad keygen --private-key my_private.pem --public-key my_public.pem

# File-based workflow (recommended to avoid copy/paste issues)
pawpad sign --input-file contract.txt --output-file signed.txt --private-key my_private.pem

# Verify signed text and detect tampering
pawpad verify --input-file signed.txt --private-key my_private.pem

# Extract original text from signed text
pawpad extract --input-file signed.txt --output-file original.txt
```

### Message Hiding

```bash
# File-based workflow (recommended to avoid copy/paste issues)
pawpad hide --input-file cover.txt --output-file hidden.txt --message "secret data"

# Hide message in a single character
pawpad hide --text "😊" --output-file hidden_emoji.txt --message "secret data" --single-char

# Reveal hidden messages
pawpad reveal --input-file hidden.txt
pawpad reveal --input-file hidden_emoji.txt --single-char
```

### Python API

```python
from pawpad.encoder import (
    # Basic fingerprinting
    generate_fingerprint,
    encode_fingerprint_in_text,
    extract_fingerprint_from_text,
    detect_fingerprint_in_text,
    
    # Cryptographic tampering detection
    generate_key_pair,
    sign_text_with_chained_fingerprints,
    verify_chained_fingerprints,
    extract_original_text_from_signed,
)

# Basic fingerprinting
fingerprint = generate_fingerprint(16)
encoded_text = encode_fingerprint_in_text("Hello, World", fingerprint)
extracted = extract_fingerprint_from_text(encoded_text)
print(f"Match: {extracted == fingerprint}")

# Cryptographic tampering detection
private_key_pem, public_key_pem = generate_key_pair()
signed_text = sign_text_with_chained_fingerprints("Important document", private_key_pem)
result = verify_chained_fingerprints(signed_text, private_key_pem)
print(f"Valid: {result['is_valid']}")
print(f"Analysis: {result['analysis']}")
```

## Features

### Core Features
- **Invisible Encoding**: Text looks identical after encoding
- **Copy/Paste Safe**: Hidden data survives copy/paste operations
- **High Density**: Can encode 16+ bytes per character
- **CLI & API**: Both command-line and Python API available

### 🔒 Advanced Security Features
- **Unbreakable Chain**: Each character's signature depends on all previous characters
- **Tampering Detection**: ANY change to ANY character is immediately detected
- **Forensic Analysis**: Pinpoint exactly which characters were modified
- **Cryptographic Proof**: Only the private key holder can create valid signatures
- **Position Sensitivity**: Moving characters breaks the chain
- **Length Sensitivity**: Adding/removing characters breaks verification

## Examples

### Basic Fingerprinting
```bash
$ pawpad encode --text "Hello world"
╭─────────────────────── Encode Result ───────────────────────╮
│ Encoding successful!                                        │
│                                                             │
│ Original text: Hello world                                  │
│ Fingerprint: 28c079afaff28e9d3021ac31118b22f3               │
│ Encoded text: H󠄘󠆰󠅩󠆟󠆟󠇢󠅾󠆍󠄠󠄑󠆜󠄡󠄁󠅻󠄒󠇣e󠄘󠆰󠅩󠆟󠆟󠇢󠅾󠆍󠄠󠄑󠆜󠄡󠄁󠅻󠄒󠇣... │
╰─────────────────────────────────────────────────────────────╯
```

### 🔒 Cryptographic Signing
```bash
$ pawpad keygen
╭─────────────────── Key Generation Result ───────────────────╮
│ Key pair generated successfully!                            │
│                                                             │
│ Private key: pawpad_private.pem                             │
│ Public key: pawpad_public.pem                               │
│                                                             │
│ ⚠️  Keep your private key secure!                           │
╰─────────────────────────────────────────────────────────────╯

$ pawpad sign --text "Contract: Pay $1000 to Alice"
╭─────────────────────── Sign Result ─────────────────────────╮
│ Text signed successfully!                                   │
│                                                             │
│ Original text: Contract: Pay $1000 to Alice                │
│ Signed text: C󠇖󠆉︆󠅈󠄋󠆍󠄔󠆁󠅨󠆨󠆔󠄿󠅟󠄳︍󠇮󠅱󠆿󠅝󠄗󠄉󠅕󠆡󠅘󠇬󠅆󠇃󠄫󠄂󠅗󠇟︋o󠅆󠇋󠅔󠄸󠆐󠇊󠆊󠄳󠇗󠅕󠇂󠄭󠄇󠅚󠇝... │
│                                                             │
│ Each character now has a unique cryptographic fingerprint  │
╰─────────────────────────────────────────────────────────────╯

$ pawpad verify --text "C󠇖󠆉︆󠅈󠄋󠆍󠄔󠆁󠅨󠆨󠆔󠄿󠅟󠄳︍󠇮󠅱󠆿󠅝󠄗󠄉󠅕󠆡󠅘󠇬󠅆󠇃󠄫󠄂󠅗󠇟︋o󠅆󠇋󠅔󠄸󠆐󠇊󠆊󠄳󠇗5󠇂󠄭󠄇󠅚󠇝..."
╭─────────────────── Verification Result ────────────────────╮
│ ✓ Text integrity verified. All 28 characters have valid    │
│ signatures.                                                 │
╰─────────────────────────────────────────────────────────────╯
```

### Tampering Detection
```bash
# If someone changes "$1000" to "$9000":
$ pawpad verify --text "tampered_text"
╭─────────────────── Verification Result ────────────────────╮
│ ✗ Tampering detected! 5 characters have invalid signatures │
│ at positions: [15, 16, 17, 18, 19]                         │
│                                                             │
│ The text has been modified after signing.                  │
╰─────────────────────────────────────────────────────────────╯
```

## Use Cases

⚠️ **Warning**: This tool is for educational and legitimate purposes only.

**Legitimate Uses:**
- **Document Integrity**: Detect unauthorized modifications to contracts, agreements, or important documents
- **Digital Forensics**: Investigate whether text has been tampered with
- **Text Watermarking**: Mark documents to trace leaks with cryptographic proof
- **Content Authentication**: Verify that text came from a trusted source
- **Steganography Research**: Study Unicode-based hiding techniques
- **Chain of Custody**: Maintain cryptographic proof of document integrity

**Security Applications:**
- **Legal Documents**: Ensure contracts haven't been modified
- **Financial Records**: Detect tampering in transaction records
- **Medical Records**: Verify patient data integrity
- **Academic Papers**: Prevent unauthorized modifications
- **News Articles**: Detect fake news or quote manipulation

## Technical Details

### Basic Fingerprinting
- Uses Unicode variation selectors (256 available)
- Encodes 1 byte per variation selector
- Supports fingerprints up to 256 bytes
- Compatible with most Unicode-aware systems

### 🔒 Cryptographic Tampering Detection
- **Algorithm**: Chained HMAC-SHA256 with RSA key pairs
- **Chain Structure**: Each character's signature depends on all previous characters
- **Key Size**: 2048-bit RSA keys
- **Signature Size**: 32 bytes (256 bits) per character
- **Detection Rate**: 100% for any single character change
- **False Positive Rate**: Cryptographically negligible (~2^-256)

### Security Properties
- **Unforgeability**: Requires private key to create valid signatures
- **Tamper Evidence**: Any change breaks the cryptographic chain
- **Position Sensitivity**: Moving characters invalidates signatures
- **Length Sensitivity**: Adding/removing characters breaks verification
- **Non-Repudiation**: Only private key holder could have signed the text

## Requirements

- Python 3.8+
- click
- rich
- cryptography

## License

This project is provided for educational purposes. Use responsibly and in accordance with applicable laws and regulations.
