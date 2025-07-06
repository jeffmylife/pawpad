#!/bin/bash
echo "🕵️ PawPad Message Hiding Demo"
echo "============================="

echo
echo "1. Cover text:"
cat cover.txt
echo

echo "2. Hiding secret message in cover text..."
pawpad hide --input-file cover.txt --output-file hidden.txt --message "Meet at midnight"
echo

echo "3. The hidden text looks identical:"
cat hidden.txt
echo

echo "4. Revealing the hidden message..."
pawpad reveal --input-file hidden.txt
echo

echo "5. Hiding message in a single emoji (Paul Butler's approach)..."
echo "😊" > emoji.txt
pawpad hide --input-file emoji.txt --output-file hidden_emoji.txt --message "Secret data" --single-char
echo

echo "6. Revealing message from emoji..."
pawpad reveal --input-file hidden_emoji.txt --single-char
echo

echo "Demo complete!"
echo "Files created:"
echo "- hidden.txt (cover text with hidden message)"
echo "- hidden_emoji.txt (emoji with hidden message)" 