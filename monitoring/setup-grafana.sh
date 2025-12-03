#!/bin/bash

# Grafana setup script for Kubernetes deployment
# This script configures Prometheus data source and imports the FastAPI dashboard

GRAFANA_URL="http://34.88.175.32/grafana"
GRAFANA_USER="admin"
GRAFANA_PASSWORD="admin"

echo "Setting up Grafana at $GRAFANA_URL..."

# Wait for Grafana to be ready
echo "Waiting for Grafana to be ready..."
until curl -s "$GRAFANA_URL/api/health" > /dev/null 2>&1; do
    echo "Grafana not ready yet, waiting..."
    sleep 5
done
echo "Grafana is ready!"

# Add Prometheus data source
echo "Adding Prometheus data source..."
curl -X POST "$GRAFANA_URL/api/datasources" \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true,
    "jsonData": {
      "httpMethod": "POST"
    }
  }'

echo -e "\n"

# Import dashboard
echo "Importing FastAPI Metrics dashboard..."
DASHBOARD_JSON=$(cat "$(dirname "$0")/grafana/dashboards/fastapi_metrics.json")

# Wrap the dashboard in the import format
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
  -d "{
    \"dashboard\": $DASHBOARD_JSON,
    \"overwrite\": true,
    \"message\": \"Initial dashboard import\"
  }"

echo -e "\n"
echo "Setup complete!"
echo "Access Grafana at: $GRAFANA_URL"
echo "Username: $GRAFANA_USER"
echo "Password: $GRAFANA_PASSWORD"
echo ""
echo "The FastAPI Metrics dashboard should now be available."
