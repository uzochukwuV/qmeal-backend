#!/bin/bash
# Add /api/* to Caddy backend routes so API endpoints return JSON instead of HTML
if ! grep -q '/api/\*' /etc/caddy/Caddyfile; then
    sed -i 's|@backend_routes path /_event|@backend_routes path /api /api/* /_event|' /etc/caddy/Caddyfile
    caddy reload --config /etc/caddy/Caddyfile 2>/dev/null || true
    echo "Caddy config updated: /api/* routes now forwarded to backend"
fi
