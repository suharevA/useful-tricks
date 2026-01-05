import streamlit as st
import pandas as pd
import numpy as np
from streamlit_agraph import agraph, Node, Edge, Config
import time
from datetime import datetime, timedelta
import json

# --- НАСТРОЙКИ ---
st.set_page_config(layout="wide", page_title="InfraObserver AI", page_icon="🕵️")

# --- ПРЕМИУМ СТИЛЬ V2 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    * {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Основной фон - глубокий градиент */
    .stApp {
        background: radial-gradient(ellipse at top, #1a1f35 0%, #0a0e1a 50%, #000000 100%);
        color: #e2e8f0;
    }

    /* Сайдбар с glass effect */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(10, 14, 26, 0.98) 100%) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(100, 116, 139, 0.15);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.5);
    }
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {
        color: #e2e8f0 !important;
        font-weight: 500;
    }

    /* Селекторы с glow effect */
    [data-testid="stSidebar"] [data-baseweb="select"] {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid rgba(6, 182, 212, 0.2) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stSidebar"] [data-baseweb="select"]:hover {
        border-color: rgba(6, 182, 212, 0.5) !important;
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.2);
    }

    input[type="text"], input[type="number"] {
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(100, 116, 139, 0.3) !important;
        color: #e2e8f0 !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease;
    }
    input[type="text"]:focus, input[type="number"]:focus {
        border-color: rgba(6, 182, 212, 0.6) !important;
        box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.1), 0 0 20px rgba(6, 182, 212, 0.2) !important;
    }

    /* Заголовки с анимированным градиентом */
    h1 {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 36px !important;
        font-weight: 700;
        letter-spacing: -1px;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    h2 { color: #f1f5f9; font-weight: 600; font-size: 22px !important; }
    h3, h4 { color: #cbd5e1; font-weight: 600; }

    /* ===== НОВЫЕ КАРТОЧКИ МЕТРИК ===== */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin: 16px 0;
    }

    .metric-card-v2 {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%);
        border: 1px solid rgba(100, 116, 139, 0.15);
        border-radius: 20px;
        padding: 20px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .metric-card-v2::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-color), transparent);
        opacity: 0.8;
    }
    .metric-card-v2:hover {
        transform: translateY(-4px);
        border-color: var(--accent-color);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 30px color-mix(in srgb, var(--accent-color) 20%, transparent);
    }

    .metric-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        background: color-mix(in srgb, var(--accent-color) 15%, transparent);
        border: 1px solid color-mix(in srgb, var(--accent-color) 30%, transparent);
    }
    .metric-trend {
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
    }
    .metric-trend.up { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
    .metric-trend.down { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .metric-trend.neutral { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }

    .metric-value {
        font-size: 36px;
        font-weight: 700;
        color: #f1f5f9;
        line-height: 1;
        margin: 8px 0;
        font-variant-numeric: tabular-nums;
    }
    .metric-label {
        font-size: 13px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Sparkline */
    .sparkline-container {
        height: 40px;
        margin-top: 12px;
        position: relative;
    }
    .sparkline {
        width: 100%;
        height: 100%;
    }
    .sparkline-line {
        fill: none;
        stroke: var(--accent-color);
        stroke-width: 2;
        stroke-linecap: round;
        stroke-linejoin: round;
    }
    .sparkline-area {
        fill: url(#sparklineGradient);
        opacity: 0.3;
    }

    /* ===== УЛУЧШЕННЫЕ ЛОГИ ===== */
    .logs-container {
        background: rgba(10, 14, 26, 0.98);
        border: 1px solid rgba(6, 182, 212, 0.1);
        border-radius: 16px;
        overflow: hidden;
        box-shadow: inset 0 2px 12px rgba(0, 0, 0, 0.5);
    }

    .logs-toolbar {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: rgba(15, 23, 42, 0.6);
        border-bottom: 1px solid rgba(100, 116, 139, 0.1);
    }
    .logs-toolbar input {
        flex: 1;
        background: rgba(10, 14, 26, 0.8);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 8px;
        padding: 8px 12px;
        color: #e2e8f0;
        font-size: 13px;
    }
    .logs-toolbar input:focus {
        border-color: rgba(6, 182, 212, 0.5);
        outline: none;
    }

    .logs-filter-btn {
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        border: 1px solid transparent;
        transition: all 0.2s;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .logs-filter-btn.all { background: rgba(100, 116, 139, 0.2); color: #94a3b8; }
    .logs-filter-btn.info { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }
    .logs-filter-btn.warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .logs-filter-btn.error { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
    .logs-filter-btn.active { border-color: currentColor; }

    .logs-scroll {
        max-height: 400px;
        overflow-y: auto;
        padding: 8px 0;
    }
    .logs-scroll::-webkit-scrollbar {
        width: 8px;
    }
    .logs-scroll::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
    }
    .logs-scroll::-webkit-scrollbar-thumb {
        background: rgba(100, 116, 139, 0.3);
        border-radius: 4px;
    }
    .logs-scroll::-webkit-scrollbar-thumb:hover {
        background: rgba(100, 116, 139, 0.5);
    }

    .log-entry {
        display: grid;
        grid-template-columns: 80px 70px 90px 1fr auto;
        gap: 12px;
        align-items: start;
        padding: 10px 16px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        border-left: 3px solid transparent;
        transition: all 0.2s;
        cursor: pointer;
    }
    .log-entry:hover {
        background: rgba(6, 182, 212, 0.05);
    }
    .log-entry.info { border-left-color: #06b6d4; }
    .log-entry.warn { border-left-color: #fbbf24; }
    .log-entry.error { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.03); }

    .log-time {
        color: #475569;
        font-size: 11px;
    }
    .log-level {
        font-weight: 600;
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 4px;
        text-align: center;
    }
    .log-level.info { background: rgba(6, 182, 212, 0.15); color: #06b6d4; }
    .log-level.warn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .log-level.error { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

    .log-source {
        font-size: 10px;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    .log-source.systemd { background: rgba(139, 92, 246, 0.15); color: #a78bfa; }
    .log-source.app { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
    .log-source.netstat { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
    .log-source.disk { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
    .log-source.nginx { background: rgba(236, 72, 153, 0.15); color: #ec4899; }

    .log-message {
        color: #cbd5e1;
        word-break: break-word;
        line-height: 1.5;
    }
    .log-message.truncated {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .log-expand-btn {
        padding: 2px 8px;
        background: rgba(100, 116, 139, 0.2);
        border: none;
        border-radius: 4px;
        color: #64748b;
        font-size: 10px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .log-expand-btn:hover {
        background: rgba(6, 182, 212, 0.2);
        color: #06b6d4;
    }

    .log-details {
        grid-column: 1 / -1;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        font-size: 11px;
        color: #94a3b8;
        border: 1px solid rgba(100, 116, 139, 0.1);
    }
    .log-details pre {
        margin: 0;
        white-space: pre-wrap;
        word-break: break-all;
    }

    .logs-stats {
        display: flex;
        gap: 16px;
        padding: 12px 16px;
        background: rgba(15, 23, 42, 0.4);
        border-top: 1px solid rgba(100, 116, 139, 0.1);
        font-size: 12px;
    }
    .logs-stat {
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .logs-stat-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .logs-stat-dot.info { background: #06b6d4; }
    .logs-stat-dot.warn { background: #fbbf24; }
    .logs-stat-dot.error { background: #ef4444; }

    /* ===== УЛУЧШЕННЫЕ ГРАФИКИ ===== */
    .chart-container {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.6) 100%);
        border: 1px solid rgba(100, 116, 139, 0.15);
        border-radius: 16px;
        padding: 20px;
        margin: 16px 0;
    }
    .chart-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
    }
    .chart-title {
        font-size: 16px;
        font-weight: 600;
        color: #e2e8f0;
    }
    .chart-legend {
        display: flex;
        gap: 16px;
    }
    .chart-legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        color: #94a3b8;
    }
    .chart-legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
    }

    /* Вкладки */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(15, 23, 42, 0.6);
        border-bottom: 1px solid rgba(100, 116, 139, 0.2);
        gap: 8px;
        padding: 4px;
        border-radius: 12px 12px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        color: #94a3b8;
        border: none;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(59, 130, 246, 0.2)) !important;
        color: #06b6d4 !important;
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
    }

    /* Кнопки */
    .stButton > button {
        border-radius: 10px !important;
        border: none !important;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important;
        font-weight: 600;
        padding: 12px 24px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.3);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.5);
    }

    /* Статус бейджи */
    .status-badge {
        margin-left: 12px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .status-healthy {
        background: rgba(34, 197, 94, 0.2);
        color: #22c55e;
        border: 1px solid rgba(34, 197, 94, 0.4);
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.2);
    }
    .status-warning {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        animation: pulse-warning 2s infinite;
    }
    .status-critical {
        background: rgba(239, 68, 68, 0.2);
        color: #ff6b6b;
        border: 1px solid rgba(239, 68, 68, 0.4);
        animation: pulse-critical 1.5s infinite;
    }

    @keyframes pulse-warning {
        0%, 100% { box-shadow: 0 0 20px rgba(245, 158, 11, 0.2); }
        50% { box-shadow: 0 0 30px rgba(245, 158, 11, 0.4); }
    }
    @keyframes pulse-critical {
        0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.3); }
        50% { box-shadow: 0 0 40px rgba(239, 68, 68, 0.6); }
    }

    /* Sidebar metrics */
    .sidebar-metric-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .sidebar-metric-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(100, 116, 139, 0.1);
    }
    .sidebar-metric-row:last-child {
        border-bottom: none;
    }
    .sidebar-metric-label {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: #94a3b8;
    }
    .sidebar-metric-value {
        font-size: 15px;
        font-weight: 600;
    }
    .sidebar-metric-value.healthy { color: #22c55e; }
    .sidebar-metric-value.warning { color: #fbbf24; }
    .sidebar-metric-value.critical { color: #ef4444; }

    /* Source badges */
    .source-type {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        margin-right: 8px;
        text-transform: uppercase;
    }
    .source-systemd { background: rgba(139, 92, 246, 0.2); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.3); }
    .source-app { background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); }
    .source-network { background: rgba(59, 130, 246, 0.2); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
    .source-disk { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.3); }
    .source-nginx { background: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid rgba(236, 72, 153, 0.3); }

    /* Метрики streamlit */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%);
        border: 1px solid rgba(100, 116, 139, 0.2);
        border-radius: 12px;
        padding: 18px;
    }
    [data-testid="metric-value"] {
        color: #06b6d4 !important;
        font-size: 28px !important;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# --- СОСТОЯНИЕ ---
if 'selected_node' not in st.session_state:
    st.session_state['selected_node'] = None
if 'ai_chat_history' not in st.session_state:
    st.session_state['ai_chat_history'] = []
if 'search_query' not in st.session_state:
    st.session_state['search_query'] = ""
if 'filter_status' not in st.session_state:
    st.session_state['filter_status'] = "All"
if 'filter_source' not in st.session_state:
    st.session_state['filter_source'] = "Virtual Machines"
if 'log_filter' not in st.session_state:
    st.session_state['log_filter'] = "ALL"
if 'log_search' not in st.session_state:
    st.session_state['log_search'] = ""
if 'expanded_logs' not in st.session_state:
    st.session_state['expanded_logs'] = set()


# --- ДАННЫЕ ---
def get_all_services():
    return [
        {"id": "vm-app-01", "name": "App Server 01", "status": "HEALTHY", "type": "VM",
         "sources": ["systemd", "app", "netstat"]},
        {"id": "vm-app-02", "name": "App Server 02", "status": "WARNING", "type": "VM",
         "sources": ["systemd", "app", "netstat"]},
        {"id": "vm-lb-01", "name": "Load Balancer", "status": "HEALTHY", "type": "VM",
         "sources": ["nginx", "netstat", "systemd"]},
        {"id": "vm-pay-01", "name": "Payment Service", "status": "CRITICAL", "type": "VM",
         "sources": ["app", "netstat", "disk"]},
        {"id": "vm-db-01", "name": "Database Primary", "status": "HEALTHY", "type": "VM",
         "sources": ["systemd", "disk", "netstat"]},
        {"id": "vm-cache-01", "name": "Redis Cache", "status": "HEALTHY", "type": "VM",
         "sources": ["systemd", "netstat"]},
    ]


def get_graph_data(search_filter="", status_filter="All"):
    all_services = get_all_services()

    filtered = all_services
    if search_filter:
        filtered = [s for s in filtered if
                    search_filter.lower() in s['name'].lower() or search_filter.lower() in s['type'].lower()]
    if status_filter != "All":
        filtered = [s for s in filtered if s['status'] == status_filter]

    filtered_ids = {s['id'] for s in filtered}

    color_map = {"HEALTHY": "#22c55e", "WARNING": "#fbbf24", "CRITICAL": "#ff6b6b"}
    nodes = []
    for svc in all_services:
        if not search_filter and status_filter == "All":
            nodes.append(Node(
                id=svc['id'],
                label=svc['name'],
                size=35 if svc['status'] == "CRITICAL" else 28 if svc['status'] == "WARNING" else 22,
                color=color_map[svc['status']],
                symbolType="square" if "lb" in svc['id'] else "diamond" if "db" in svc['id'] else "circle"
            ))
        elif svc['id'] in filtered_ids:
            nodes.append(Node(
                id=svc['id'],
                label=svc['name'],
                size=35 if svc['status'] == "CRITICAL" else 28 if svc['status'] == "WARNING" else 22,
                color=color_map[svc['status']],
                symbolType="square" if "lb" in svc['id'] else "diamond" if "db" in svc['id'] else "circle"
            ))

    all_edges = [
        Edge(source="vm-lb-01", target="vm-app-01", label="HTTP/2"),
        Edge(source="vm-lb-01", target="vm-app-02", label="HTTP/2"),
        Edge(source="vm-app-01", target="vm-pay-01", label="gRPC"),
        Edge(source="vm-app-02", target="vm-pay-01", label="gRPC"),
        Edge(source="vm-pay-01", target="vm-db-01", label="TCP:5432"),
        Edge(source="vm-pay-01", target="vm-cache-01", label="TCP:6379"),
    ]

    node_ids = {n.id for n in nodes}
    edges = [e for e in all_edges if e.source in node_ids and e.to in node_ids]

    return nodes, edges, filtered


def generate_live_logs(node_id, source_type, count=10):
    now = datetime.now()

    logs_by_source = {
        "systemd": [
            ("INFO", "systemd[1]: Started application.service", {"unit": "application.service", "pid": 1234}),
            ("INFO", "systemd[1]: Reloading configuration",
             {"action": "reload", "config": "/etc/systemd/system/app.service"}),
            ("WARN", "systemd[1]: Unit state changed: active -> degraded",
             {"previous": "active", "current": "degraded", "reason": "dependency failed"}),
            ("INFO", "systemd[1]: Finished system-update-cleanup.service", {"duration": "2.5s"}),
            ("ERROR", "systemd[1]: Failed to start networking.service",
             {"exit_code": 1, "stderr": "Network interface eth0 not found"}),
        ],
        "app": [
            ("ERROR", "RuntimeError: Database connection pool exhausted", {"pool_size": 20, "active": 20, "waiting": 15,
                                                                           "trace": "at ConnectionPool.acquire() line 142\nat DatabaseClient.query() line 89\nat PaymentService.process() line 234"}),
            ("WARN", "High memory allocation detected: 1.8GB/2GB",
             {"heap_used": "1.8GB", "heap_total": "2GB", "gc_runs": 45}),
            (
            "INFO", "Request processing time: 245ms", {"endpoint": "/api/v1/payment", "method": "POST", "status": 200}),
            ("ERROR", "Timeout waiting for downstream service",
             {"service": "inventory-api", "timeout_ms": 5000, "attempt": 3}),
            ("WARN", "Slow query detected: 2.3s", {"query": "SELECT * FROM orders WHERE...", "rows_examined": 1500000}),
            ("INFO", "Health check passed", {"checks": ["db", "cache", "queue"], "latency_ms": 12}),
        ],
        "netstat": [
            ("WARN", "TCP retransmit rate: 2.3% (threshold: 1%)",
             {"interface": "eth0", "packets_sent": 150000, "retransmits": 3450}),
            ("INFO", "Active connections: 1247/2000", {"established": 1247, "time_wait": 523, "close_wait": 12}),
            ("ERROR", "Connection refused on port 5432",
             {"target": "10.0.1.50:5432", "attempts": 3, "last_error": "ECONNREFUSED"}),
            ("WARN", "High TIME_WAIT sockets: 1823",
             {"threshold": 1000, "recommendation": "Consider enabling tcp_tw_reuse"}),
            ("INFO", "Network throughput: 125 MB/s", {"rx_bytes": "65MB/s", "tx_bytes": "60MB/s"}),
        ],
        "disk": [
            ("ERROR", "I/O error on /dev/sda: sector 12847261",
             {"device": "/dev/sda", "error_type": "read_error", "smart_status": "degraded"}),
            ("WARN", "Disk usage at 87% on /var/lib",
             {"path": "/var/lib", "used": "174GB", "total": "200GB", "inodes_free": "2.1M"}),
            ("ERROR", "Write latency spike: 450ms",
             {"device": "/dev/nvme0n1", "avg_latency": "5ms", "spike_duration": "3s"}),
            ("INFO", "SMART self-test completed", {"device": "/dev/sda", "result": "PASSED", "runtime": "120s"}),
            ("WARN", "High I/O wait: 35%", {"device": "/dev/sda", "iowait_threshold": "20%"}),
        ],
        "nginx": [
            ("ERROR", "upstream timed out (110: Connection timed out)",
             {"upstream": "backend_pool", "server": "10.0.1.10:8080", "request": "GET /api/data"}),
            ("WARN", "499 Client closed connection (upstream)",
             {"client": "203.0.113.50", "request_time": "30.5s", "bytes_sent": 0}),
            ("INFO", "SSL handshake completed: TLSv1.3",
             {"cipher": "TLS_AES_256_GCM_SHA384", "client": "203.0.113.100"}),
            ("WARN", "Rate limit exceeded: 1000 req/s",
             {"zone": "api_limit", "client": "203.0.113.75", "rejected": 150}),
            ("ERROR", "502 Bad Gateway", {"upstream": "payment_service", "response_time": "-", "status": 502}),
            ("INFO", "Cache HIT ratio: 78%", {"hits": 78000, "misses": 22000, "expired": 5000}),
        ]
    }

    messages = logs_by_source.get(source_type, [
        ("INFO", "Service health check passed", {}),
        ("INFO", "Metrics collected successfully", {}),
    ])

    logs = []
    for i in range(count):
        msg = messages[np.random.randint(0, len(messages))]
        timestamp = (now - timedelta(seconds=i * np.random.randint(3, 15))).strftime(
            "%H:%M:%S.") + f"{np.random.randint(0, 999):03d}"
        log_id = f"{source_type}-{i}-{timestamp}"
        logs.append({
            "id": log_id,
            "time": timestamp,
            "level": msg[0],
            "msg": msg[1],
            "source": source_type,
            "details": msg[2] if len(msg) > 2 else {}
        })

    return logs


def get_node_details(node_id):
    # Генерация данных для графиков с временными метками
    timestamps = pd.date_range(end=datetime.now(), periods=30, freq='1min')
    chart_data = pd.DataFrame({
        'timestamp': timestamps,
        'CPU %': np.clip(np.random.randn(30).cumsum() + 65, 20, 95),
        'Memory MB': np.clip(np.random.randn(30).cumsum() * 50 + 1200, 500, 1900),
        'Network KB/s': np.clip(np.random.randn(30).cumsum() * 100 + 850, 100, 2000),
    })
    chart_data.set_index('timestamp', inplace=True)

    services = [s for s in get_all_services() if s['id'] == node_id]
    sources = services[0]['sources'] if services else ["app"]

    all_logs = []
    for source in sources:
        all_logs.extend(generate_live_logs(node_id, source, count=8))

    all_logs.sort(key=lambda x: x['time'], reverse=True)

    if node_id == "vm-pay-01":
        status = "CRITICAL"
    elif node_id == "vm-app-02":
        status = "WARNING"
    else:
        status = "HEALTHY"

    return status, chart_data, all_logs[:20], sources


def generate_sparkline_svg(values, color, width=120, height=35):
    """Генерация SVG sparkline графика"""
    if not values or len(values) < 2:
        return ""

    # Нормализация значений
    min_val, max_val = min(values), max(values)
    if max_val == min_val:
        normalized = [0.5] * len(values)
    else:
        normalized = [(v - min_val) / (max_val - min_val) for v in values]

    # Создание точек пути
    points = []
    step = width / (len(values) - 1)
    for i, v in enumerate(normalized):
        x = i * step
        y = height - (v * (height - 4)) - 2  # Отступ сверху и снизу
        points.append(f"{x},{y}")

    path_d = "M " + " L ".join(points)
    area_d = f"M 0,{height} L " + " L ".join(points) + f" L {width},{height} Z"

    return f'''
    <svg width="{width}" height="{height}" class="sparkline">
        <defs>
            <linearGradient id="sparkGrad_{color.replace('#', '')}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:{color};stop-opacity:0" />
            </linearGradient>
        </defs>
        <path d="{area_d}" fill="url(#sparkGrad_{color.replace('#', '')})" />
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    '''


def render_metric_card(icon, label, value, unit, trend_value, trend_direction, color, sparkline_data=None):
    """Рендер красивой карточки метрики"""
    trend_class = "up" if trend_direction == "up" else "down" if trend_direction == "down" else "neutral"
    trend_symbol = "↑" if trend_direction == "up" else "↓" if trend_direction == "down" else "→"

    sparkline_html = ""
    if sparkline_data:
        sparkline_html = f'<div class="sparkline-container">{generate_sparkline_svg(sparkline_data, color)}</div>'

    return f'''
    <div class="metric-card-v2" style="--accent-color: {color};">
        <div class="metric-header">
            <div class="metric-icon">{icon}</div>
            <div class="metric-trend {trend_class}">{trend_symbol} {trend_value}</div>
        </div>
        <div class="metric-value">{value}<span style="font-size: 16px; color: #64748b; margin-left: 4px;">{unit}</span></div>
        <div class="metric-label">{label}</div>
        {sparkline_html}
    </div>
    '''


def render_logs_panel(logs, log_filter="ALL", log_search=""):
    """Рендер улучшенной панели логов"""

    # Фильтрация
    filtered_logs = logs
    if log_filter != "ALL":
        filtered_logs = [l for l in logs if l['level'] == log_filter]
    if log_search:
        filtered_logs = [l for l in filtered_logs if log_search.lower() in l['msg'].lower()]

    # Подсчёт статистики
    info_count = len([l for l in logs if l['level'] == 'INFO'])
    warn_count = len([l for l in logs if l['level'] == 'WARN'])
    error_count = len([l for l in logs if l['level'] == 'ERROR'])

    # Генерация HTML для логов
    logs_html = ""
    for log in filtered_logs:
        level_class = log['level'].lower()
        source_class = log['source']
        is_long = len(log['msg']) > 60
        is_expanded = log['id'] in st.session_state.get('expanded_logs', set())

        msg_class = "" if is_expanded or not is_long else "truncated"
        expand_btn = f'<button class="log-expand-btn" onclick="this.closest(\'.log-entry\').classList.toggle(\'expanded\')">{("▼" if is_expanded else "▶") if is_long else ""}</button>' if is_long else ""

        details_html = ""
        if log.get('details') and is_expanded:
            details_html = f'<div class="log-details"><pre>{json.dumps(log["details"], indent=2)}</pre></div>'

        logs_html += f'''
        <div class="log-entry {level_class}">
            <span class="log-time">{log['time']}</span>
            <span class="log-level {level_class}">{log['level']}</span>
            <span class="log-source {source_class}">{log['source']}</span>
            <span class="log-message {msg_class}">{log['msg']}</span>
            {expand_btn}
            {details_html}
        </div>
        '''

    return f'''
    <div class="logs-container">
        <div class="logs-scroll">
            {logs_html if logs_html else '<div style="padding: 20px; text-align: center; color: #64748b;">No logs matching filters</div>'}
        </div>
        <div class="logs-stats">
            <div class="logs-stat">
                <span class="logs-stat-dot info"></span>
                <span>{info_count} Info</span>
            </div>
            <div class="logs-stat">
                <span class="logs-stat-dot warn"></span>
                <span>{warn_count} Warnings</span>
            </div>
            <div class="logs-stat">
                <span class="logs-stat-dot error"></span>
                <span>{error_count} Errors</span>
            </div>
        </div>
    </div>
    '''


# --- ИНТЕРФЕЙС ---

# САЙДБАР
with st.sidebar:
    st.markdown("### 🎯 Analysis Scope")

    st.session_state['filter_source'] = st.selectbox(
        "Select area first",
        ["— Select Area —", "VM", "NGINX", "Network", "Storage", "Virtualization"],
        index=0,
        help="Analysis won't start without selecting an area"
    )

    # Показываем предупреждение если область не выбрана
    if st.session_state['filter_source'] == "— Select Area —":
        st.warning("⚠️ Select area to start analysis", icon="🎯")

    st.session_state['filter_status'] = st.selectbox(
        "Service Status",
        ["All", "HEALTHY", "WARNING", "CRITICAL"],
        index=0
    )

    st.markdown("### ⏱️ Time Period")

    time_mode = st.radio(
        "Time selection mode",
        ["Quick Select", "Custom Range"],
        horizontal=True,
        label_visibility="collapsed"
    )

    if time_mode == "Quick Select":
        time_period = st.selectbox(
            "Select time range",
            ["Last 5 minutes", "Last 15 minutes", "Last 30 minutes", "Last 1 hour",
             "Last 6 hours", "Last 24 hours", "Last 7 days", "Last 30 days"],
            index=1
        )
    else:
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input("From", value=datetime.now() - timedelta(days=7), max_value=datetime.now())
        with col_date2:
            end_date = st.date_input("To", value=datetime.now(), max_value=datetime.now())

    auto_refresh = st.checkbox("Auto-refresh data", value=False)

    st.divider()

    # Улучшенная статистика в сайдбаре
    st.markdown("### 📊 System Health")
    services = get_all_services()
    healthy = len([s for s in services if s['status'] == 'HEALTHY'])
    warning = len([s for s in services if s['status'] == 'WARNING'])
    critical = len([s for s in services if s['status'] == 'CRITICAL'])
    total = len(services)

    st.markdown(f"""
    <div class="sidebar-metric-card">
        <div class="sidebar-metric-row">
            <span class="sidebar-metric-label">✓ Healthy</span>
            <span class="sidebar-metric-value healthy">{healthy}/{total}</span>
        </div>
        <div class="sidebar-metric-row">
            <span class="sidebar-metric-label">⚠ Warnings</span>
            <span class="sidebar-metric-value warning">{warning}</span>
        </div>
        <div class="sidebar-metric-row">
            <span class="sidebar-metric-label">✕ Critical</span>
            <span class="sidebar-metric-value critical">{critical}</span>
        </div>
        <div style="margin-top: 12px; height: 6px; background: rgba(100,116,139,0.2); border-radius: 3px; overflow: hidden;">
            <div style="display: flex; height: 100%;">
                <div style="width: {healthy / total * 100}%; background: #22c55e;"></div>
                <div style="width: {warning / total * 100}%; background: #fbbf24;"></div>
                <div style="width: {critical / total * 100}%; background: #ef4444;"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 📡 Active Sources")
    st.markdown("""
    <div class="sidebar-metric-card" style="padding: 12px;">
        <p style="margin: 6px 0;"><span class="source-type source-systemd">systemd</span></p>
        <p style="margin: 6px 0;"><span class="source-type source-app">app logs</span></p>
        <p style="margin: 6px 0;"><span class="source-type source-network">netstat</span></p>
        <p style="margin: 6px 0;"><span class="source-type source-disk">disk</span></p>
        <p style="margin: 6px 0;"><span class="source-type source-nginx">nginx</span></p>
    </div>
    """, unsafe_allow_html=True)

# HEADER
col1, col2 = st.columns([5, 1])
with col1:
    st.title("Infrastructure Observer")
    st.caption(f"🚀 Real-time observability platform • {st.session_state['filter_source']}")

with col2:
    if st.button("↻ Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# SEARCH
search_col1, search_col2 = st.columns([4, 1])
with search_col1:
    st.session_state['search_query'] = st.text_input(
        "Search",
        value=st.session_state['search_query'],
        placeholder="🔍 Search VMs, services, or infrastructure...",
        label_visibility="collapsed"
    )

with search_col2:
    if st.button("Clear", use_container_width=True):
        st.session_state['search_query'] = ""
        st.rerun()

st.divider()

# MAIN CONTENT
col_graph, col_details = st.columns([6, 4])

with col_graph:
    st.subheader("📡 Infrastructure Topology")

    nodes, edges, filtered_services = get_graph_data(
        st.session_state['search_query'],
        st.session_state['filter_status']
    )

    if not nodes:
        st.info("🔍 No services match your filters. Try adjusting the criteria.")
    else:
        if st.session_state['search_query'] or st.session_state['filter_status'] != "All":
            st.caption(f"Showing {len(nodes)} of {len(get_all_services())} virtual machines")

        config = Config(
            width=900,
            height=600,
            directed=True,
            physics=True,
            hierarchical=False,
            nodeHighlightBehavior=True,
            highlightColor="#06b6d4",
            collapsible=False
        )

        selected_node_id = agraph(nodes=nodes, edges=edges, config=config)

        if selected_node_id:
            st.session_state['selected_node'] = selected_node_id

# DETAILS PANEL
with col_details:
    current_node = st.session_state['selected_node']

    if not current_node:
        st.subheader("🎯 System Overview")

        # Красивые карточки метрик
        sparkline_cpu = list(np.random.randn(20).cumsum() + 65)
        sparkline_latency = list(np.random.randn(20).cumsum() + 45)
        sparkline_errors = list(np.clip(np.random.randn(20).cumsum() + 2, 0, 10))
        sparkline_uptime = list(np.clip(np.random.randn(20).cumsum() * 0.1 + 99.8, 99, 100))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(render_metric_card("📈", "Requests/sec", "12,543", "", "+5.2%", "up", "#06b6d4", sparkline_cpu),
                        unsafe_allow_html=True)
        with col2:
            st.markdown(
                render_metric_card("⚡", "Avg Latency", "45", "ms", "-2ms", "down", "#22c55e", sparkline_latency),
                unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown(
                render_metric_card("⚠️", "Error Rate", "2.1", "%", "-0.5%", "down", "#fbbf24", sparkline_errors),
                unsafe_allow_html=True)
        with col4:
            st.markdown(render_metric_card("✓", "Uptime", "99.8", "%", "+0.1%", "up", "#8b5cf6", sparkline_uptime),
                        unsafe_allow_html=True)

        st.warning("⚠️ Critical issues detected in vm-pay-01")

    else:
        status, chart_data, logs, sources = get_node_details(current_node)

        status_class = f"status-{status.lower()}"
        st.markdown(f'<h2>{current_node}<span class="status-badge {status_class}">{status}</span></h2>',
                    unsafe_allow_html=True)

        # Активные источники
        sources_html = '<div style="margin: 10px 0;">'
        source_class_map = {
            "systemd": "source-systemd", "app": "source-app", "netstat": "source-network",
            "disk": "source-disk", "nginx": "source-nginx"
        }
        for src in sources:
            sources_html += f'<span class="source-type {source_class_map.get(src, "source-app")}">{src}</span>'
        sources_html += '</div>'
        st.markdown(sources_html, unsafe_allow_html=True)

        # TABS
        tab1, tab2, tab3 = st.tabs(["📊 Metrics", "📄 Logs", "🤖 AI Analysis"])

        with tab1:
            st.caption("Resource usage and performance metrics")

            # Карточки метрик с sparkline
            cpu_values = list(chart_data['CPU %'].values)
            mem_values = list(chart_data['Memory MB'].values)
            net_values = list(chart_data['Network KB/s'].values)

            cpu_val = int(cpu_values[-1])
            mem_val = int(mem_values[-1])
            net_val = int(net_values[-1])

            col1, col2 = st.columns(2)
            with col1:
                cpu_trend = "up" if cpu_val > 65 else "down"
                st.markdown(render_metric_card("🔥", "CPU Usage", str(cpu_val), "%", f"{cpu_val - 65:+.0f}%", cpu_trend,
                                               "#06b6d4", cpu_values[-15:]), unsafe_allow_html=True)
            with col2:
                mem_trend = "up" if mem_val > 1200 else "down"
                st.markdown(render_metric_card("💾", "Memory", str(mem_val), "MB", f"{mem_val - 1200:+.0f}", mem_trend,
                                               "#8b5cf6", mem_values[-15:]), unsafe_allow_html=True)

            col3, col4 = st.columns(2)
            with col3:
                net_trend = "up" if net_val > 850 else "down"
                st.markdown(
                    render_metric_card("🌐", "Network I/O", str(net_val), "KB/s", f"{net_val - 850:+.0f}", net_trend,
                                       "#22c55e", net_values[-15:]), unsafe_allow_html=True)
            with col4:
                disk_io = np.random.randint(50, 150)
                st.markdown(render_metric_card("💿", "Disk I/O", str(disk_io), "MB/s", "+12%", "up", "#fbbf24",
                                               list(np.random.randn(15).cumsum() + disk_io)), unsafe_allow_html=True)

            # Основной график
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('''
            <div class="chart-header">
                <span class="chart-title">Performance Timeline (30 min)</span>
                <div class="chart-legend">
                    <div class="chart-legend-item"><div class="chart-legend-dot" style="background: #06b6d4;"></div>CPU</div>
                    <div class="chart-legend-item"><div class="chart-legend-dot" style="background: #8b5cf6;"></div>Memory</div>
                    <div class="chart-legend-item"><div class="chart-legend-dot" style="background: #22c55e;"></div>Network</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            st.line_chart(chart_data, height=200)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            # Компактные фильтры в одну строку
            filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
            with filter_col1:
                log_search = st.text_input("🔍", placeholder="grep pattern...", label_visibility="collapsed",
                                           key="log_search_input")
            with filter_col2:
                log_filter = st.selectbox("Level", ["ALL", "INFO", "WARN", "ERROR"], label_visibility="collapsed")
            with filter_col3:
                source_filter = st.selectbox("Source", ["All"] + sources, label_visibility="collapsed")

            # Фильтрация логов
            filtered_logs = logs
            if log_filter != "ALL":
                filtered_logs = [l for l in filtered_logs if l['level'] == log_filter]
            if log_search:
                filtered_logs = [l for l in filtered_logs if log_search.lower() in l['msg'].lower()]
            if source_filter != "All":
                filtered_logs = [l for l in filtered_logs if l['source'] == source_filter]

            # Статистика в одну строку
            info_count = len([l for l in logs if l['level'] == 'INFO'])
            warn_count = len([l for l in logs if l['level'] == 'WARN'])
            error_count = len([l for l in logs if l['level'] == 'ERROR'])

            st.markdown(f"""
            <div style="display: flex; gap: 16px; padding: 6px 12px; font-size: 11px; color: #64748b; background: rgba(15,23,42,0.5); border-radius: 6px 6px 0 0; border: 1px solid rgba(100,116,139,0.2); border-bottom: none; font-family: 'JetBrains Mono', monospace;">
                <span>$ tail -f /var/log/{current_node}.log</span>
                <span style="margin-left: auto;">lines: {len(filtered_logs)}</span>
                <span style="color: #06b6d4;">I:{info_count}</span>
                <span style="color: #fbbf24;">W:{warn_count}</span>
                <span style="color: #ef4444;">E:{error_count}</span>
            </div>
            """, unsafe_allow_html=True)

            # Терминальный вывод логов
            log_lines = []
            for log in filtered_logs:
                level = log['level']
                # Цвета ANSI-style
                if level == 'ERROR':
                    level_color = "#ef4444"
                    line_color = "#fca5a5"
                elif level == 'WARN':
                    level_color = "#fbbf24"
                    line_color = "#fde68a"
                else:
                    level_color = "#06b6d4"
                    line_color = "#94a3b8"

                # Цвета источников
                src_colors = {"systemd": "#a78bfa", "app": "#22c55e", "netstat": "#3b82f6", "disk": "#f97316",
                              "nginx": "#ec4899"}
                src_color = src_colors.get(log['source'], "#64748b")

                # Форматируем как tail -f
                time_str = log['time'][:8]  # HH:MM:SS
                src_padded = log['source'].ljust(7)
                level_padded = level.ljust(5)

                log_lines.append(
                    f'<span style="color:#475569">{time_str}</span> '
                    f'<span style="color:{src_color}">[{src_padded}]</span> '
                    f'<span style="color:{level_color};font-weight:600">{level_padded}</span> '
                    f'<span style="color:{line_color}">{log["msg"]}</span>'
                )

            terminal_content = "<br>".join(
                log_lines) if log_lines else '<span style="color:#64748b">No logs matching filter</span>'

            st.markdown(f"""
            <div style="
                background: #0a0e14;
                border: 1px solid rgba(100,116,139,0.2);
                border-radius: 0 0 8px 8px;
                padding: 12px;
                font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 12px;
                line-height: 1.6;
                height: 320px;
                overflow-y: auto;
                white-space: pre-wrap;
                word-break: break-word;
            ">
{terminal_content}
            </div>
            """, unsafe_allow_html=True)

            # Кнопки действий
            col1, col2, col3 = st.columns(3)
            if col1.button("↻ Refresh", use_container_width=True, key="logs_refresh_btn"):
                st.rerun()
            if col2.button("⏸ Pause", use_container_width=True, key="logs_pause_btn"):
                st.session_state['logs_paused'] = not st.session_state.get('logs_paused', False)
            col3.download_button(
                label="↓ Export",
                data="\n".join([f"{l['time']} [{l['source']}] {l['level']} {l['msg']}" for l in filtered_logs]),
                file_name=f"logs_{current_node}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                mime="text/plain",
                use_container_width=True,
                key="logs_export_btn"
            )

        with tab3:
            # Проверяем выбрана ли область
            area_selected = st.session_state.get('filter_source', "— Select Area —") != "— Select Area —"

            if not area_selected:
                st.error("🎯 **Select analysis area first** (sidebar)")
                st.markdown("""
                <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 20px; margin: 16px 0;">
                    <h4 style="color: #fca5a5; margin-top: 0;">Why area matters:</h4>
                    <ul style="color: #94a3b8; margin: 0; padding-left: 20px;">
                        <li>Reduces context dramatically</li>
                        <li>Excludes irrelevant data</li>
                        <li>LLM works stable with focused data</li>
                        <li>Results are reproducible</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                current_area = st.session_state['filter_source']

                st.markdown(f"""
                <div style="background: rgba(6,182,212,0.1); border: 1px solid rgba(6,182,212,0.3); border-radius: 8px; padding: 12px; margin-bottom: 16px;">
                    <span style="color: #06b6d4; font-weight: 600;">🎯 Area:</span> 
                    <span style="color: #e2e8f0;">{current_area}</span>
                    <span style="color: #64748b; margin-left: 12px;">→ Context reduced, ready for analysis</span>
                </div>
                """, unsafe_allow_html=True)

                # История чата
                for msg in st.session_state['ai_chat_history']:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                if not st.session_state['ai_chat_history']:
                    st.markdown("""
                    <div style="background: rgba(30,41,59,0.5); border: 1px solid rgba(100,116,139,0.2); border-radius: 12px; padding: 20px;">
                        <h4 style="color: #e2e8f0; margin-top: 0;">💡 Ask a specific question:</h4>
                        <div style="display: grid; gap: 8px; margin-top: 12px;">
                            <div style="background: rgba(6,182,212,0.1); padding: 10px 14px; border-radius: 8px; color: #94a3b8; font-size: 13px;">
                                ✅ "Why did TCP retransmits increase?"
                            </div>
                            <div style="background: rgba(6,182,212,0.1); padding: 10px 14px; border-radius: 8px; color: #94a3b8; font-size: 13px;">
                                ✅ "Are there signs of network issues?"
                            </div>
                            <div style="background: rgba(6,182,212,0.1); padding: 10px 14px; border-radius: 8px; color: #94a3b8; font-size: 13px;">
                                ✅ "Is this a VM or infrastructure problem?"
                            </div>
                            <div style="background: rgba(6,182,212,0.1); padding: 10px 14px; border-radius: 8px; color: #94a3b8; font-size: 13px;">
                                ✅ "Why is nginx returning 502?"
                            </div>
                            <div style="background: rgba(239,68,68,0.1); padding: 10px 14px; border-radius: 8px; color: #64748b; font-size: 13px;">
                                ❌ "What happened?" — too vague
                            </div>
                        </div>
                        <p style="color: #64748b; font-size: 12px; margin-top: 16px; margin-bottom: 0;">
                            Question types: <span style="color:#06b6d4">cause</span> • 
                            <span style="color:#22c55e">confirmation</span> • 
                            <span style="color:#fbbf24">exclusion</span> • 
                            <span style="color:#a78bfa">comparison</span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Поле ввода вопроса
                user_question = st.chat_input(f"Ask about {current_area}...")

                if user_question:
                    # Проверка на слишком общий вопрос
                    vague_patterns = ["что случилось", "what happened", "что не так", "what's wrong", "проблема",
                                      "помоги"]
                    is_vague = any(p in user_question.lower() for p in vague_patterns)

                    st.session_state['ai_chat_history'].append({"role": "user", "content": user_question})

                    with st.chat_message("assistant"):
                        if is_vague:
                            response = f"""⚠️ **Question too vague**

Please be more specific. Examples for **{current_area}**:
- "Why did [metric] increase/decrease?"
- "Is there a correlation between X and Y?"
- "What caused the spike at [time]?"

This helps me extract relevant facts before analysis."""
                            st.write(response)
                        else:
                            with st.spinner("📊 Extracting facts from logs..."):
                                time.sleep(1)
                            with st.spinner("🔍 Analyzing facts with LLM..."):
                                time.sleep(1.5)

                            # Симуляция ответа на основе области и вопроса
                            response = f"""**Analysis: {current_area}** → "{user_question}"

---

**📊 Facts extracted (pre-LLM):**
```
Area: {current_area}
Node: {current_node}
Time range: last 15 minutes
Sources analyzed: {', '.join(sources)}
Anomalies detected: 3
```

**🔍 Finding:**

Based on extracted facts from **{current_area}** logs:

1. **Root cause identified**: Network layer shows TCP retransmit rate 2.3% (threshold 1%)

2. **Correlation found**: 
   - T-10min: retransmits spike
   - T-7min: connection pool exhaustion  
   - T-5min: service degradation

3. **Evidence from logs**:
   - `netstat`: 3,450 retransmits / 150,000 packets
   - `app`: "Database connection pool exhausted"
   - `systemd`: state changed to "degraded"

**💡 Recommendation:**
Check network interface with `ethtool -S eth0` for packet drops

---
*Analysis scope: {current_area} only. Facts extracted before LLM.*"""
                            st.write(response)

                        st.session_state['ai_chat_history'].append({"role": "assistant", "content": response})
                    st.rerun()

                # Кнопка очистки
                if st.session_state['ai_chat_history']:
                    if st.button("🗑️ Clear conversation", use_container_width=True, key="clear_ai_chat"):
                        st.session_state['ai_chat_history'] = []
                        st.rerun()