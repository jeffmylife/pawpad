# 🐾 PawPad Examples

This folder contains example files demonstrating PawPad's capabilities.

## File-Based Workflow

PawPad supports file input/output to avoid copy-paste issues with Unicode variation selectors:

```bash
# Use files for input and output
pawpad encode --input-file examples/original.txt --output-file examples/encoded.txt
pawpad sign --input-file examples/contract.txt --output-file examples/signed.txt
pawpad verify --input-file examples/signed.txt
```

## Examples

### 1. Basic Fingerprinting (`basic/`)
- `original.txt` - Sample text
- `encoded.txt` - Text with fingerprint encoded
- `demo.sh` - Commands to run the demo

### 2. Cryptographic Signing (`crypto/`)
- `contract.txt` - Important document to sign
- `signed.txt` - Cryptographically signed version
- `simple_demo.sh` - Basic signing and verification demo
- `tampering_demo.sh` - Advanced tampering detection demo

### 3. Message Hiding (`messages/`)
- `cover.txt` - Cover text
- `hidden.txt` - Text with hidden message
- `demo.sh` - Commands to run the demo

## Running the Examples

Each example folder contains demo scripts that demonstrate the complete workflow:

```bash
# Basic fingerprinting
cd examples/basic && ./demo.sh

# Message hiding
cd examples/messages && ./demo.sh

# Cryptographic signing (simple)
cd examples/crypto && ./simple_demo.sh

# Tampering detection (advanced)
cd examples/crypto && ./tampering_demo.sh
```

This will:
1. Generate keys (if needed)
2. Sign the document
3. Verify the signature
4. Test tampering detection
5. Show forensic analysis

## Key Files

The examples use shared key files:
- `private_key.pem` - Private key for signing
- `public_key.pem` - Public key (not used in current implementation)

⚠️ **Note**: These are example keys only. In production, generate your own secure keys! 