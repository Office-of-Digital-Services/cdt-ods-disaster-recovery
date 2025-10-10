#!/bin/bash

URL="http://host.docker.internal:7071/api/alert_to_slack"

echo "Sending test alert to: $URL"

curl -X POST \
     -H "Content-Type: application/json" \
     --data "@test_payload.json" \
     "$URL"

echo -e "\n\nRequest sent."
