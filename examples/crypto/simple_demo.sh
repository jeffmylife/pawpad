#!/bin/bash
echo "🔒 Simple PawPad Crypto Demo"
echo "==========================="

# Create a simple contract
echo "Contract: Payment of \$1000 to Alice" > contract.txt

echo
echo "1. Contract content:"
cat contract.txt
echo

echo "2. Generating keys..."
pawpad keygen --private-key demo_private.pem --public-key demo_public.pem

echo
echo "3. Signing the contract..."
pawpad sign --input-file contract.txt --output-file signed.txt --private-key demo_private.pem

echo
echo "4. Verifying the signature..."
pawpad verify --input-file signed.txt --private-key demo_private.pem

echo
echo "5. Extracting original text..."
pawpad extract --input-file signed.txt --output-file extracted.txt

echo
echo "6. Comparing original vs extracted:"
echo "Original:"
cat contract.txt
echo
echo "Extracted:"
cat extracted.txt

echo
echo "✅ Demo complete! Files created:"
echo "- contract.txt (original)"
echo "- signed.txt (cryptographically signed)"
echo "- extracted.txt (extracted from signed)"
echo "- demo_private.pem, demo_public.pem (keys)" 