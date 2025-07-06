#!/bin/bash
echo "🐾 PawPad Basic Fingerprinting Demo"
echo "=================================="

echo
echo "1. Original text:"
cat original.txt
echo

echo "2. Encoding fingerprint into text..."
pawpad encode --input-file original.txt --output-file encoded.txt --fingerprint "deadbeef"
echo

echo "3. Decoding fingerprint from text..."
pawpad decode --input-file encoded.txt --fingerprint "deadbeef"
echo

echo "4. Extracting any fingerprint present..."
pawpad decode --input-file encoded.txt
echo

echo "5. Analyzing text for hidden data..."
pawpad analyze --input-file encoded.txt
echo

echo "Demo complete! Check encoded.txt to see the fingerprinted version." 