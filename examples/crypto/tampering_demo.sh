#!/bin/bash
echo "🚨 PawPad Tampering Detection Demo"
echo "=================================="

# Create a simple contract
echo "Contract: Payment of \$1000 to Alice" > contract.txt

echo
echo "1. Original contract:"
cat contract.txt
echo

echo "2. Generating keys and signing..."
pawpad keygen --private-key demo_private.pem --public-key demo_public.pem > /dev/null 2>&1
pawpad sign --input-file contract.txt --output-file signed.txt --private-key demo_private.pem > /dev/null 2>&1

echo "3. Verifying original signed contract..."
pawpad verify --input-file signed.txt --private-key demo_private.pem

echo
echo "4. Now simulating tampering by directly modifying the signed file..."
echo "   (This simulates someone trying to change the content after signing)"

# Create a tampered version by modifying the first character
python3 -c "
with open('signed.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Change the first character to break the signature
modified = content.replace('C', 'X', 1)

with open('tampered_signed.txt', 'w', encoding='utf-8') as f:
    f.write(modified)

print('   ✓ Tampered version created (changed first character C → X)')
"

echo
echo "5. Verifying the tampered signed file..."
echo "   This should detect tampering because the signatures no longer match:"
pawpad verify --input-file tampered_signed.txt --private-key demo_private.pem

echo
echo "6. Extracting text from both versions to compare:"
echo
echo "   Original signed version:"
pawpad extract --input-file signed.txt --output-file original_extracted.txt > /dev/null 2>&1
cat original_extracted.txt

echo
echo "   Tampered version:"
pawpad extract --input-file tampered_signed.txt --output-file tampered_extracted.txt > /dev/null 2>&1
cat tampered_extracted.txt

echo
echo "💡 Key insight: When someone modifies the signed text directly,"
echo "   the cryptographic chain is broken and tampering is immediately detected."
echo "   The signatures no longer match the content, proving modification occurred."

echo
echo "✅ Demo complete! Files created:"
echo "- contract.txt (original)"
echo "- signed.txt (original signed version)"
echo "- tampered_signed.txt (directly modified signed file)"
echo "- original_extracted.txt (original content)"
echo "- tampered_extracted.txt (tampered content)" 