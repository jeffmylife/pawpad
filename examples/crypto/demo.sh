#!/bin/bash
echo "🔒 PawPad Cryptographic Tampering Detection Demo"
echo "==============================================="

echo
echo "1. Original contract:"
echo "-------------------"
cat contract.txt
echo

echo "2. Generating cryptographic keys..."
pawpad keygen --private-key private_key.pem --public-key public_key.pem
echo

echo "3. Signing the contract with chained fingerprints..."
pawpad sign --input-file contract.txt --output-file signed.txt --private-key private_key.pem
echo

echo "4. Verifying the signed contract..."
pawpad verify --input-file signed.txt --private-key private_key.pem
echo

echo "5. Creating a tampered version..."
echo "   First, extracting the original text..."
pawpad extract --input-file signed.txt --output-file extracted_original.txt > /dev/null 2>&1

echo "   Then, modifying the payment amount..."
sed 's/\$50,000/\$99,000/' extracted_original.txt > tampered_content.txt

echo "   Now, creating a fake signed version (simulating document tampering)..."
# Generate a different key to simulate tampering
pawpad keygen --private-key fake_key.pem --public-key fake_public.pem > /dev/null 2>&1
pawpad sign --input-file tampered_content.txt --output-file tampered.txt --private-key fake_key.pem > /dev/null 2>&1

echo "   ✓ Tampered version created (payment changed from $50,000 to $99,000)"
echo

echo "6. Detecting tampering in the modified contract..."
pawpad verify --input-file tampered.txt --private-key private_key.pem
echo

echo "7. Extracting original text from signed version..."
pawpad extract --input-file signed.txt --output-file extracted.txt > /dev/null 2>&1
echo "✓ Original text extracted to extracted.txt"
echo

echo "8. Comparing original vs tampered content:"
echo "Original contract (from signed version):"
cat extracted.txt
echo
echo "Tampered content (what attacker tried to create):"
cat tampered_content.txt
echo

echo "Demo complete!"
echo "Files created:"
echo "- signed.txt (cryptographically signed contract)"
echo "- tampered.txt (modified version for testing)"
echo "- extracted.txt (original text extracted from signed version)"
echo "- tampered_content.txt (the modified content)"
echo "- private_key.pem, public_key.pem (legitimate cryptographic keys)"
echo "- fake_key.pem, fake_public.pem (attacker's keys - different signatures)"
echo
echo "Key insight: Even if an attacker modifies the content and re-signs it"
echo "with their own key, the original signature verification will fail,"
echo "proving the document has been tampered with!" 