#!/usr/bin/env bash

if ! command -v curl &> /dev/null; then
    echo "Error: curl is not installed. Please install curl and try again."
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install jq and try again."
    exit 1
fi

read -s -p "Enter your GitHub personal access token: " GITHUB_TOKEN
echo

if [ -f "$HOME/.ssh/id_ed25519.pub" ]; then
    KEY_PATH="$HOME/.ssh/id_ed25519"
    echo "Found keys at $KEY_PATH"
elif [ -f "$HOME/.ssh/id_rsa.pub" ]; then
    KEY_PATH="$HOME/.ssh/id_rsa"
    echo "Found keys at $KEY_PATH"
else
    echo "No rsa or ed25519 keys found in $HOME/.ssh. Generating..."
    KEY_PATH="$HOME/.ssh/id_ed25519"
    ssh-keygen -t ed25519 -f "$KEY_PATH" -N ""
    echo "Successfully generated new ed25519 keys at $KEY_PATH"
fi

PUBKEY_PATH="${KEY_PATH}.pub"
PUBKEY_CONTENT=$(cat "$PUBKEY_PATH")

KEY_TITLE="Automated from $USER@$HOSTNAME"

JSON_PAYLOAD=$(jq -n \
  --arg title "$KEY_TITLE" \
  --arg key "$PUBKEY_CONTENT" \
  '{title: $title, key: $key}')

echo "Sending $PUBKEY_PATH to GitHub..."
RESPONSE=$(curl -s -w "%{http_code}" -o /tmp/github_response.txt \
  -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD" \
  https://api.github.com/user/keys)

HTTP_CODE="$RESPONSE"
BODY=$(cat /tmp/github_response.txt)

if [[ "$HTTP_CODE" -eq 201 ]]; then
    echo "SSH key added successfully to your GitHub account."
else
    ERROR_MESSAGE=$(jq -r '.errors[].message' /tmp/github_response.txt)
    if [[ "$ERROR_MESSAGE" == "key is already in use" ]]; then
        echo "Looks like you've already added this key to GitHub."
    else
        echo "Failed to add SSH key. Response code: $HTTP_CODE"
        echo "Response body:"
        echo "$BODY"
    fi
fi

rm -f /tmp/github_response.txt
