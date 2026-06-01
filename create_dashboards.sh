#!/bin/bash
# -----------------------------------------------------------
# Script para crear dashboards en Grafana vía API
# Requiere: Grafana corriendo en http://localhost:3001
# -----------------------------------------------------------

GRAFANA_URL="http://localhost:3001"
GRAFANA_USER="admin"
GRAFANA_PASS="admin"

echo "🔍 Verificando conexión con Grafana..."
curl -s -o /dev/null -w "%{http_code}" -u ${GRAFANA_USER}:${GRAFANA_PASS} ${GRAFANA_URL}/api/dashboards/home | grep 200 > /dev/null
if [ $? -ne 0 ]; then
    echo "❌ No se puede conectar a Grafana. Asegúrate de que esté corriendo."
    exit 1
fi
echo "✅ Conexión exitosa"

# Función para crear un dashboard
create_dashboard() {
    local title="$1"
    local uid="$2"
    local payload="$3"
    
    echo "📊 Creando dashboard: ${title}..."
    response=$(curl -s -w "%{http_code}" -o /tmp/grafana_response.json \
        -u ${GRAFANA_USER}:${GRAFANA_PASS} \
        -H "Content-Type: application/json" \
        -d "${payload}" \
        ${GRAFANA_URL}/api/dashboards/db)
    
    http_code="${response: -3}"
    if [[ "$http_code" == "200" ]]; then
        echo "✅ Dashboard '${title}' creado correctamente"
    else
        echo "❌ Error al crear '${title}' (HTTP ${http_code})"
        cat /tmp/grafana_response.json
    fi
}

# =============================================
# Dashboard 1: Flight Operations Overview
# =============================================
DASH1_JSON=$(cat << 'EOF'
{
  "dashboard": {
    "title": "Flight Operations Overview",
    "uid": "flight-ops-overview",
    "panels": [
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "id": 1,
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"booking_service\", handler=\"/bookings\", method=\"POST\"}[1m])",
            "refId": "A"
          }
        ],
        "title": "Reservas por minuto",
        "type": "timeseries"
      },
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": { "unit": "percent", "thresholds": { "steps": [ { "color": "red", "value": null }, { "color": "green", "value": 95 } ] } } },
        "gridPos": { "h": 8, "w": 6, "x": 12, "y": 0 },
        "id": 2,
        "targets": [
          {
            "expr": "(sum(rate(http_requests_total{job=\"booking_service\", handler=\"/bookings\", method=\"POST\", status=\"201\"}[5m])) / sum(rate(http_requests_total{job=\"booking_service\", handler=\"/bookings\", method=\"POST\"}[5m]))) * 100",
            "refId": "A"
          }
        ],
        "title": "Tasa de exito de reservas",
        "type": "stat"
      },
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 6, "x": 18, "y": 0 },
        "id": 3,
        "targets": [
          {
            "expr": "rate(http_requests_total{job=\"notification_service\", handler=\"/notify\", method=\"POST\"}[1m])",
            "refId": "A"
          }
        ],
        "title": "Notificaciones por minuto",
        "type": "timeseries"
      }
    ],
    "schemaVersion": 38,
    "time": { "from": "now-1h", "to": "now" }
  },
  "overwrite": true
}
EOF
)

# =============================================
# Dashboard 2: Service Health & Performance
# =============================================
DASH2_JSON=$(cat << 'EOF'
{
  "dashboard": {
    "title": "Service Health & Performance",
    "uid": "service-health",
    "panels": [
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": { "thresholds": { "steps": [ { "color": "red", "value": null }, { "color": "green", "value": 1 } ] } } },
        "gridPos": { "h": 6, "w": 24, "x": 0, "y": 0 },
        "id": 1,
        "targets": [
          { "expr": "up", "refId": "A" }
        ],
        "title": "Estado de los servicios",
        "type": "stat"
      },
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 6 },
        "id": 2,
        "targets": [
          { "expr": "rate(http_requests_total{status=~\"5..\"}[5m])", "refId": "A" }
        ],
        "title": "Errores 5xx por segundo",
        "type": "timeseries"
      },
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 6 },
        "id": 3,
        "targets": [
          { "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))", "refId": "A" }
        ],
        "title": "Latencia p95",
        "type": "timeseries"
      }
    ],
    "schemaVersion": 38,
    "time": { "from": "now-1h", "to": "now" }
  },
  "overwrite": true
}
EOF
)

# =============================================
# Dashboard 3: Infrastructure Health
# =============================================
DASH3_JSON=$(cat << 'EOF'
{
  "dashboard": {
    "title": "Infrastructure Health",
    "uid": "infra-health",
    "panels": [
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
        "id": 1,
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{job}}",
            "refId": "A"
          }
        ],
        "title": "Errores 5xx por servicio",
        "type": "timeseries"
      },
      {
        "datasource": { "type": "prometheus", "uid": "Prometheus" },
        "fieldConfig": { "defaults": {} },
        "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
        "id": 2,
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}}",
            "refId": "A"
          }
        ],
        "title": "Peticiones por segundo (tráfico)",
        "type": "timeseries"
      }
    ],
    "schemaVersion": 38,
    "time": { "from": "now-1h", "to": "now" }
  },
  "overwrite": true
}
EOF
)

# Crear los tres dashboards
create_dashboard "Flight Operations Overview" "flight-ops-overview" "$DASH1_JSON"
create_dashboard "Service Health & Performance" "service-health" "$DASH2_JSON"
create_dashboard "Infrastructure Health" "infra-health" "$DASH3_JSON"

echo ""
echo "🚀 Proceso completado. Ve a ${GRAFANA_URL} y revisa tus dashboards."
