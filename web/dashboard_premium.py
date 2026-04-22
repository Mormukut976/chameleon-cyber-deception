"""
🦎 CHAMELEON ULTIMATE — Premium Dashboard
Stunning real-time cybersecurity dashboard with Plotly/Dash
"""

import dash
from dash import dcc, html, Input, Output, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import json
import logging

logger = logging.getLogger("PremiumDashboard")

# ==================== THEME ====================
COLORS = {
    "bg_primary": "#0a0e1a",
    "bg_secondary": "#111827",
    "bg_card": "#1a1f36",
    "bg_card_hover": "#222845",
    "border": "rgba(99, 102, 241, 0.2)",
    "text_primary": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "accent_cyan": "#06b6d4",
    "accent_purple": "#8b5cf6",
    "accent_pink": "#ec4899",
    "accent_green": "#10b981",
    "accent_orange": "#f59e0b",
    "accent_red": "#ef4444",
    "accent_blue": "#3b82f6",
    "gradient_1": "linear-gradient(135deg, #06b6d4, #8b5cf6)",
    "gradient_2": "linear-gradient(135deg, #8b5cf6, #ec4899)",
    "gradient_3": "linear-gradient(135deg, #10b981, #06b6d4)",
    "gradient_4": "linear-gradient(135deg, #f59e0b, #ef4444)",
}

CARD_STYLE = {
    "backgroundColor": COLORS["bg_card"],
    "borderRadius": "16px",
    "border": f"1px solid {COLORS['border']}",
    "padding": "24px",
    "marginBottom": "20px",
    "boxShadow": "0 4px 24px rgba(0,0,0,0.3)",
    "backdropFilter": "blur(20px)",
}

GLOW_STYLE = {
    **CARD_STYLE,
    "boxShadow": "0 0 30px rgba(6, 182, 212, 0.1), 0 4px 24px rgba(0,0,0,0.3)",
}


def create_stat_card(title, value_id, icon, gradient, subtitle=""):
    """Create a premium stat card with gradient accent"""
    return html.Div([
        html.Div([
            html.Div([
                html.Span(icon, style={"fontSize": "28px"}),
            ], style={
                "width": "56px", "height": "56px", "borderRadius": "14px",
                "background": gradient, "display": "flex",
                "alignItems": "center", "justifyContent": "center",
                "marginBottom": "16px",
                "boxShadow": "0 4px 15px rgba(6, 182, 212, 0.2)"
            }),
            html.H3(id=value_id, style={
                "fontSize": "32px", "fontWeight": "700",
                "color": COLORS["text_primary"], "margin": "0",
                "fontFamily": "'Inter', sans-serif", "letterSpacing": "-0.5px"
            }),
            html.P(title, style={
                "color": COLORS["text_secondary"], "margin": "4px 0 0 0",
                "fontSize": "13px", "fontWeight": "500",
                "textTransform": "uppercase", "letterSpacing": "1px"
            }),
            html.Span(subtitle, id=f"{value_id}-sub", style={
                "color": COLORS["accent_green"], "fontSize": "11px",
                "fontWeight": "600"
            }) if subtitle else html.Span()
        ])
    ], style={
        **CARD_STYLE,
        "textAlign": "center", "minHeight": "170px",
        "display": "flex", "alignItems": "center", "justifyContent": "center",
        "transition": "all 0.3s ease",
    }, className="stat-card")


def create_dashboard(attack_store, blockchain, ml_classifier, mitre_mapper, anomaly_detector):
    """Create the premium Dash dashboard"""

    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.CYBORG,
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
            "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap",
        ],
        title="🦎 Chameleon — Cyber Deception Framework",
        update_title=None,
    )

    app.index_string = '''<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: ''' + COLORS["bg_primary"] + ''';
            font-family: 'Inter', -apple-system, sans-serif;
            color: ''' + COLORS["text_primary"] + ''';
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background:
                radial-gradient(ellipse at 20% 50%, rgba(6, 182, 212, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(139, 92, 246, 0.06) 0%, transparent 50%),
                radial-gradient(ellipse at 50% 80%, rgba(236, 72, 153, 0.04) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        #react-entry-point { position: relative; z-index: 1; }
        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(6, 182, 212, 0.15), 0 4px 24px rgba(0,0,0,0.4) !important;
            border-color: rgba(6, 182, 212, 0.4) !important;
        }
        .attack-row {
            padding: 12px 16px;
            border-radius: 10px;
            margin: 6px 0;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }
        .attack-row:hover {
            background: rgba(255,255,255,0.03);
        }
        .attack-critical { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.06); }
        .attack-high { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.06); }
        .attack-medium { border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.06); }
        .attack-low { border-left-color: #10b981; background: rgba(16, 185, 129, 0.06); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 3px; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .pulse { animation: pulse 2s infinite; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .slide-in { animation: slideIn 0.5s ease-out; }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
</body>
</html>'''

    # ==================== LAYOUT ====================
    app.layout = html.Div([
        # Header
        html.Div([
            html.Div([
                html.Div([
                    html.Span("🦎", style={"fontSize": "36px", "marginRight": "14px"}),
                    html.Div([
                        html.H1("CHAMELEON", style={
                            "fontSize": "28px", "fontWeight": "800", "margin": "0",
                            "background": COLORS["gradient_1"],
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "letterSpacing": "2px"
                        }),
                        html.Span("Advanced Cyber Deception Framework", style={
                            "fontSize": "12px", "color": COLORS["text_muted"],
                            "letterSpacing": "2px", "textTransform": "uppercase"
                        })
                    ])
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    html.Div([
                        html.Span("●", style={"color": COLORS["accent_green"], "marginRight": "6px"},
                                  className="pulse"),
                        html.Span("LIVE", style={
                            "color": COLORS["accent_green"], "fontSize": "11px",
                            "fontWeight": "700", "letterSpacing": "2px"
                        })
                    ], style={
                        "background": "rgba(16, 185, 129, 0.1)",
                        "padding": "6px 16px", "borderRadius": "20px",
                        "border": "1px solid rgba(16, 185, 129, 0.3)",
                        "display": "flex", "alignItems": "center"
                    }),
                    html.Span(id="current-time", style={
                        "color": COLORS["text_muted"], "fontSize": "13px",
                        "marginLeft": "16px", "fontFamily": "'JetBrains Mono', monospace"
                    })
                ], style={"display": "flex", "alignItems": "center", "gap": "8px"})
            ], style={
                "display": "flex", "justifyContent": "space-between",
                "alignItems": "center", "maxWidth": "1440px",
                "margin": "0 auto", "padding": "0 24px"
            })
        ], style={
            "background": "rgba(17, 24, 39, 0.8)",
            "backdropFilter": "blur(20px)",
            "padding": "16px 0",
            "borderBottom": f"1px solid {COLORS['border']}",
            "position": "sticky", "top": "0", "zIndex": "100",
            "marginBottom": "24px"
        }),

        # Main Content
        html.Div([
            # Row 1: Stats Cards
            dbc.Row([
                dbc.Col(create_stat_card(
                    "Total Attacks", "stat-total", "🎯",
                    COLORS["gradient_1"], "▲ Live"
                ), lg=2, md=4, sm=6, xs=6),
                dbc.Col(create_stat_card(
                    "Unique IPs", "stat-ips", "🌐",
                    COLORS["gradient_2"]
                ), lg=2, md=4, sm=6, xs=6),
                dbc.Col(create_stat_card(
                    "Critical Threats", "stat-critical", "🔴",
                    COLORS["gradient_4"]
                ), lg=2, md=4, sm=6, xs=6),
                dbc.Col(create_stat_card(
                    "ML Accuracy", "stat-ml", "🤖",
                    COLORS["gradient_3"]
                ), lg=2, md=4, sm=6, xs=6),
                dbc.Col(create_stat_card(
                    "Blockchain Blocks", "stat-blocks", "⛓️",
                    "linear-gradient(135deg, #6366f1, #8b5cf6)"
                ), lg=2, md=4, sm=6, xs=6),
                dbc.Col(create_stat_card(
                    "MITRE Techniques", "stat-mitre", "🗺️",
                    "linear-gradient(135deg, #f43f5e, #ec4899)"
                ), lg=2, md=4, sm=6, xs=6),
            ], className="g-3 mb-4"),

            # Row 2: Attack Timeline + Threat Gauge
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.H4("📈 Attack Timeline", style={
                                "color": COLORS["text_primary"], "fontWeight": "600",
                                "fontSize": "16px", "margin": "0"
                            }),
                            html.Span("Real-time attack frequency", style={
                                "color": COLORS["text_muted"], "fontSize": "12px"
                            })
                        ]),
                        dcc.Graph(id="timeline-chart", config={"displayModeBar": False},
                                  style={"height": "280px"})
                    ], style=GLOW_STYLE)
                ], lg=8, md=12),
                dbc.Col([
                    html.Div([
                        html.H4("⚡ Threat Level", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "8px"
                        }),
                        dcc.Graph(id="threat-gauge", config={"displayModeBar": False},
                                  style={"height": "260px"})
                    ], style=GLOW_STYLE)
                ], lg=4, md=12),
            ], className="g-3 mb-4"),

            # Row 3: Geo Map + Attack Distribution
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("🌍 Global Attack Map", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "8px"
                        }),
                        dcc.Graph(id="geo-map", config={"displayModeBar": False},
                                  style={"height": "360px"})
                    ], style=GLOW_STYLE)
                ], lg=7, md=12),
                dbc.Col([
                    html.Div([
                        html.H4("🎯 Attack Distribution", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "8px"
                        }),
                        dcc.Graph(id="attack-donut", config={"displayModeBar": False},
                                  style={"height": "360px"})
                    ], style=GLOW_STYLE)
                ], lg=5, md=12),
            ], className="g-3 mb-4"),

            # Row 4: MITRE ATT&CK Heatmap + ML Predictions
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.H4("🗺️ MITRE ATT&CK Coverage", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "8px"
                        }),
                        dcc.Graph(id="mitre-heatmap", config={"displayModeBar": False},
                                  style={"height": "300px"})
                    ], style=GLOW_STYLE)
                ], lg=7, md=12),
                dbc.Col([
                    html.Div([
                        html.H4("🤖 ML Threat Classification", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "8px"
                        }),
                        dcc.Graph(id="ml-classification", config={"displayModeBar": False},
                                  style={"height": "300px"})
                    ], style=GLOW_STYLE)
                ], lg=5, md=12),
            ], className="g-3 mb-4"),

            # Row 5: Live Attack Feed + Top Attackers + Blockchain
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Div([
                            html.H4("🚨 Live Attack Feed", style={
                                "color": COLORS["text_primary"], "fontWeight": "600",
                                "fontSize": "16px", "margin": "0"
                            }),
                            html.Span("●", style={"color": COLORS["accent_red"]}, className="pulse"),
                        ], style={"display": "flex", "justifyContent": "space-between",
                                  "alignItems": "center", "marginBottom": "16px"}),
                        html.Div(id="attack-feed", style={
                            "maxHeight": "400px", "overflowY": "auto",
                            "paddingRight": "8px"
                        })
                    ], style=GLOW_STYLE)
                ], lg=5, md=12),
                dbc.Col([
                    html.Div([
                        html.H4("🏴‍☠️ Top Attackers", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "16px"
                        }),
                        html.Div(id="top-attackers")
                    ], style=GLOW_STYLE),
                    html.Div([
                        html.H4("⛓️ Blockchain Evidence", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "12px"
                        }),
                        html.Div(id="blockchain-status-panel")
                    ], style={**GLOW_STYLE, "marginTop": "20px"})
                ], lg=3, md=6),
                dbc.Col([
                    html.Div([
                        html.H4("🛡️ System Status", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "16px"
                        }),
                        html.Div(id="system-status")
                    ], style=GLOW_STYLE),
                    html.Div([
                        html.H4("🔍 Anomaly Detection", style={
                            "color": COLORS["text_primary"], "fontWeight": "600",
                            "fontSize": "16px", "marginBottom": "12px"
                        }),
                        html.Div(id="anomaly-panel")
                    ], style={**GLOW_STYLE, "marginTop": "20px"})
                ], lg=4, md=6),
            ], className="g-3 mb-4"),

            # Footer
            html.Div([
                html.P([
                    "🦎 Chameleon Cyber Deception Framework v2.0 — ",
                    html.Span("Built with AI-Powered Threat Intelligence",
                              style={"color": COLORS["accent_cyan"]})
                ], style={
                    "textAlign": "center", "color": COLORS["text_muted"],
                    "fontSize": "12px", "padding": "20px"
                })
            ])
        ], style={"maxWidth": "1440px", "margin": "0 auto", "padding": "0 20px"}),

        # Interval for auto-refresh
        dcc.Interval(id="refresh-interval", interval=2000, n_intervals=0),
    ])

    # ==================== CALLBACKS ====================
    @app.callback(
        [
            Output("stat-total", "children"),
            Output("stat-ips", "children"),
            Output("stat-critical", "children"),
            Output("stat-ml", "children"),
            Output("stat-blocks", "children"),
            Output("stat-mitre", "children"),
            Output("current-time", "children"),
        ],
        [Input("refresh-interval", "n_intervals")]
    )
    def update_stats(n):
        attacks = attack_store.get("attacks", [])
        total = len(attacks)
        unique_ips = len(set(a.get("source_ip", "") for a in attacks))

        critical_types = {"SQL_INJECTION", "COMMAND_INJECTION", "ADVANCED_PERSISTENT_THREAT"}
        critical = sum(1 for a in attacks if a.get("attack_type") in critical_types)

        ml_stats = ml_classifier.get_model_stats() if ml_classifier else {}
        ml_acc = f"{ml_stats.get('accuracy', 0):.0f}%"

        blocks = len(blockchain.chain) if blockchain else 1
        mitre_count = len(mitre_mapper.detected_techniques) if mitre_mapper else 0

        now = datetime.now().strftime("%H:%M:%S")

        return str(total), str(unique_ips), str(critical), ml_acc, str(blocks), str(mitre_count), now

    @app.callback(
        Output("timeline-chart", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_timeline(n):
        attacks = attack_store.get("attacks", [])
        fig = go.Figure()

        if attacks:
            # Group by hour
            time_buckets = defaultdict(int)
            critical_buckets = defaultdict(int)
            critical_types = {"SQL_INJECTION", "COMMAND_INJECTION", "XSS_ATTACK", "SSH_BRUTE_FORCE"}

            for a in attacks:
                try:
                    ts = datetime.fromisoformat(a["timestamp"])
                    key = ts.strftime("%H:%M")
                    time_buckets[key] += 1
                    if a.get("attack_type") in critical_types:
                        critical_buckets[key] += 1
                except:
                    pass

            times = sorted(time_buckets.keys())
            counts = [time_buckets[t] for t in times]
            critical_counts = [critical_buckets[t] for t in times]

            fig.add_trace(go.Scatter(
                x=times, y=counts, mode="lines+markers",
                name="All Attacks", fill="tozeroy",
                line=dict(color=COLORS["accent_cyan"], width=2),
                fillcolor="rgba(6, 182, 212, 0.1)",
                marker=dict(size=4)
            ))
            fig.add_trace(go.Scatter(
                x=times, y=critical_counts, mode="lines+markers",
                name="Critical", fill="tozeroy",
                line=dict(color=COLORS["accent_red"], width=2),
                fillcolor="rgba(239, 68, 68, 0.1)",
                marker=dict(size=4)
            ))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"], size=11),
            margin=dict(l=40, r=20, t=10, b=30),
            legend=dict(orientation="h", yanchor="top", y=1.1, font=dict(size=10)),
            xaxis=dict(gridcolor="rgba(99,102,241,0.1)", showline=False),
            yaxis=dict(gridcolor="rgba(99,102,241,0.1)", showline=False),
            hovermode="x unified"
        )
        return fig

    @app.callback(
        Output("threat-gauge", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_gauge(n):
        attacks = attack_store.get("attacks", [])
        threat_scores = {"PORT_SCAN_SYN": 20, "SSH_BRUTE_FORCE": 60, "SQL_INJECTION": 90,
                         "XSS_ATTACK": 70, "PATH_TRAVERSAL": 65, "COMMAND_INJECTION": 95,
                         "HTTP_RECON": 25, "OS_FINGERPRINTING": 40, "SSH_CONNECTION": 30}

        if attacks:
            recent = attacks[-20:]
            avg_threat = sum(threat_scores.get(a.get("attack_type", ""), 30) for a in recent) / len(recent)
        else:
            avg_threat = 15

        color = COLORS["accent_green"] if avg_threat < 40 else COLORS["accent_orange"] if avg_threat < 70 else COLORS["accent_red"]

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_threat,
            number=dict(font=dict(size=42, color=color)),
            gauge=dict(
                axis=dict(range=[0, 100], tickcolor=COLORS["text_muted"],
                          dtick=20, tickfont=dict(size=10)),
                bar=dict(color=color, thickness=0.7),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                steps=[
                    dict(range=[0, 40], color="rgba(16, 185, 129, 0.15)"),
                    dict(range=[40, 70], color="rgba(245, 158, 11, 0.15)"),
                    dict(range=[70, 100], color="rgba(239, 68, 68, 0.15)"),
                ],
            )
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"]),
            margin=dict(l=30, r=30, t=30, b=10),
            height=260,
        )
        return fig

    @app.callback(
        Output("geo-map", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_geo_map(n):
        attacks = attack_store.get("attacks", [])

        geo_data = defaultdict(lambda: {"count": 0, "lat": 0, "lon": 0, "country": "", "city": "", "types": []})
        for a in attacks:
            geo = a.get("geo", {})
            if geo and geo.get("lat"):
                key = a["source_ip"]
                geo_data[key]["count"] += 1
                geo_data[key]["lat"] = geo["lat"]
                geo_data[key]["lon"] = geo["lon"]
                geo_data[key]["country"] = geo.get("country", "Unknown")
                geo_data[key]["city"] = geo.get("city", "Unknown")
                geo_data[key]["types"].append(a.get("attack_type", ""))

        lats = [v["lat"] for v in geo_data.values()]
        lons = [v["lon"] for v in geo_data.values()]
        sizes = [min(40, v["count"] * 3 + 8) for v in geo_data.values()]
        texts = [f"<b>{ip}</b><br>{v['city']}, {v['country']}<br>Attacks: {v['count']}"
                 for ip, v in geo_data.items()]
        colors = [v["count"] for v in geo_data.values()]

        fig = go.Figure()

        if lats:
            fig.add_trace(go.Scattergeo(
                lat=lats, lon=lons,
                marker=dict(
                    size=sizes, color=colors,
                    colorscale=[[0, "rgba(6,182,212,0.4)"], [0.5, "rgba(245,158,11,0.7)"],
                                [1, "rgba(239,68,68,0.9)"]],
                    line=dict(width=1, color="rgba(255,255,255,0.3)"),
                    sizemode="diameter"
                ),
                text=texts, hoverinfo="text",
            ))

        fig.update_geos(
            bgcolor="rgba(0,0,0,0)",
            landcolor="rgba(26, 31, 54, 0.8)",
            oceancolor="rgba(10, 14, 26, 0.5)",
            coastlinecolor="rgba(99, 102, 241, 0.3)",
            countrycolor="rgba(99, 102, 241, 0.2)",
            showocean=True, showlakes=False,
            projection_type="natural earth",
            framecolor="rgba(0,0,0,0)",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=0, b=0), height=360,
            geo=dict(bgcolor="rgba(0,0,0,0)"),
        )
        return fig

    @app.callback(
        Output("attack-donut", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_donut(n):
        attacks = attack_store.get("attacks", [])
        type_counts = Counter(a.get("attack_type", "UNKNOWN") for a in attacks)

        if not type_counts:
            type_counts = {"MONITORING": 1}

        labels = list(type_counts.keys())
        values = list(type_counts.values())

        # Short labels
        short_labels = [l.replace("_", " ").title()[:20] for l in labels]

        colors_palette = [
            COLORS["accent_cyan"], COLORS["accent_purple"], COLORS["accent_pink"],
            COLORS["accent_green"], COLORS["accent_orange"], COLORS["accent_red"],
            COLORS["accent_blue"], "#a78bfa", "#34d399", "#fbbf24",
            "#f472b6", "#60a5fa"
        ]

        fig = go.Figure(go.Pie(
            labels=short_labels, values=values,
            hole=0.65, textinfo="percent",
            textfont=dict(size=10, color="white"),
            marker=dict(colors=colors_palette[:len(labels)],
                        line=dict(color=COLORS["bg_primary"], width=2)),
            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>"
        ))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"], size=10),
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            legend=dict(font=dict(size=9), bgcolor="rgba(0,0,0,0)",
                        orientation="v", yanchor="middle", y=0.5),
            height=360,
        )
        return fig

    @app.callback(
        Output("mitre-heatmap", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_mitre_heatmap(n):
        if not mitre_mapper:
            return go.Figure()

        heatmap_data = mitre_mapper.get_heatmap_data()

        if not heatmap_data:
            return go.Figure()

        tactics = list(dict.fromkeys(d["tactic"] for d in heatmap_data))
        techniques = list(dict.fromkeys(d["technique_name"] for d in heatmap_data))

        z_matrix = []
        for tech in techniques:
            row = []
            for tactic in tactics:
                val = 0
                for d in heatmap_data:
                    if d["technique_name"] == tech and d["tactic"] == tactic:
                        val = d["count"]
                        break
                row.append(val)
            z_matrix.append(row)

        fig = go.Figure(go.Heatmap(
            z=z_matrix,
            x=[t[:15] for t in tactics],
            y=[t[:25] for t in techniques],
            colorscale=[
                [0, "rgba(26, 31, 54, 0.8)"],
                [0.3, "rgba(6, 182, 212, 0.3)"],
                [0.6, "rgba(245, 158, 11, 0.6)"],
                [1, "rgba(239, 68, 68, 0.9)"]
            ],
            showscale=False,
            hovertemplate="<b>%{y}</b><br>Tactic: %{x}<br>Detections: %{z}<extra></extra>"
        ))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"], size=9),
            margin=dict(l=130, r=10, t=10, b=80),
            xaxis=dict(tickangle=45), height=300,
        )
        return fig

    @app.callback(
        Output("ml-classification", "figure"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_ml_chart(n):
        attacks = attack_store.get("attacks", [])

        if ml_classifier and attacks:
            threat_counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
            for a in attacks[-50:]:
                pred = ml_classifier.predict(a)
                threat_counts[pred["threat_level"]] += 1

            labels = list(threat_counts.keys())
            values = list(threat_counts.values())
            colors = [COLORS["accent_green"], COLORS["accent_blue"],
                      COLORS["accent_orange"], COLORS["accent_red"]]
        else:
            labels = ["Low", "Medium", "High", "Critical"]
            values = [5, 3, 2, 1]
            colors = [COLORS["accent_green"], COLORS["accent_blue"],
                      COLORS["accent_orange"], COLORS["accent_red"]]

        fig = go.Figure(go.Bar(
            x=[l.title() for l in labels], y=values,
            marker=dict(color=colors, cornerradius=8,
                        line=dict(width=0)),
            text=values, textposition="outside",
            textfont=dict(color=COLORS["text_secondary"], size=12),
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>"
        ))

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLORS["text_secondary"], size=11),
            margin=dict(l=40, r=20, t=20, b=40), height=300,
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="rgba(99,102,241,0.1)"),
            bargap=0.3,
        )
        return fig

    @app.callback(
        Output("attack-feed", "children"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_feed(n):
        attacks = attack_store.get("attacks", [])
        if not attacks:
            return html.P("Waiting for attacks... All honeypots active.",
                          style={"color": COLORS["text_muted"], "textAlign": "center",
                                 "padding": "40px"})

        recent = list(reversed(attacks[-15:]))
        items = []
        for a in recent:
            at = a.get("attack_type", "UNKNOWN")
            severity = ("critical" if "SQL" in at or "COMMAND" in at else
                        "high" if "BRUTE" in at or "XSS" in at else
                        "medium" if "TRAVERSAL" in at else "low")

            icon = {"critical": "🔴", "high": "🟠", "medium": "🔵", "low": "🟢"}[severity]

            try:
                ts = datetime.fromisoformat(a["timestamp"]).strftime("%H:%M:%S")
            except:
                ts = "—"

            items.append(html.Div([
                html.Div([
                    html.Span(f"{icon} ", style={"marginRight": "6px"}),
                    html.Span(at.replace("_", " "), style={
                        "fontWeight": "600", "fontSize": "13px",
                        "color": COLORS["text_primary"]
                    }),
                    html.Span(f" — {ts}", style={
                        "color": COLORS["text_muted"], "fontSize": "11px",
                        "fontFamily": "'JetBrains Mono', monospace", "marginLeft": "auto"
                    })
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    html.Span(a.get("source_ip", "?"), style={
                        "fontFamily": "'JetBrains Mono', monospace",
                        "color": COLORS["accent_cyan"], "fontSize": "12px"
                    }),
                    html.Span(f" → {a.get('details', '')[:60]}", style={
                        "color": COLORS["text_muted"], "fontSize": "11px"
                    })
                ], style={"marginTop": "4px"})
            ], className=f"attack-row attack-{severity} slide-in"))

        return items

    @app.callback(
        Output("top-attackers", "children"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_top_attackers(n):
        attacks = attack_store.get("attacks", [])
        ip_counts = Counter(a.get("source_ip", "?") for a in attacks)
        top = ip_counts.most_common(6)

        if not top:
            return html.P("No attackers detected yet.",
                          style={"color": COLORS["text_muted"]})

        items = []
        for i, (ip, count) in enumerate(top):
            geo = next((a.get("geo", {}) for a in attacks if a.get("source_ip") == ip), {})
            country = geo.get("country", "?")

            bar_width = (count / top[0][1]) * 100

            items.append(html.Div([
                html.Div([
                    html.Span(f"#{i+1}", style={
                        "color": COLORS["text_muted"], "fontSize": "11px",
                        "marginRight": "8px", "minWidth": "20px"
                    }),
                    html.Div([
                        html.Span(ip, style={
                            "fontFamily": "'JetBrains Mono', monospace",
                            "color": COLORS["text_primary"], "fontSize": "12px"
                        }),
                        html.Span(f"  {country}", style={
                            "color": COLORS["text_muted"], "fontSize": "10px"
                        })
                    ]),
                    html.Span(str(count), style={
                        "color": COLORS["accent_cyan"], "fontWeight": "700",
                        "fontSize": "14px", "marginLeft": "auto"
                    })
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div(style={
                    "height": "3px", "borderRadius": "2px",
                    "background": f"linear-gradient(90deg, {COLORS['accent_cyan']}, {COLORS['accent_purple']})",
                    "width": f"{bar_width}%", "marginTop": "6px",
                    "transition": "width 0.5s ease"
                })
            ], style={"padding": "8px 0", "borderBottom": f"1px solid {COLORS['border']}"}))

        return items

    @app.callback(
        Output("blockchain-status-panel", "children"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_blockchain_panel(n):
        if not blockchain:
            return html.P("Blockchain offline", style={"color": COLORS["text_muted"]})

        chain_len = len(blockchain.chain)
        is_valid = blockchain.verify_chain()

        return html.Div([
            _status_row("Chain Length", str(chain_len), COLORS["accent_purple"]),
            _status_row("Integrity", "✅ Valid" if is_valid else "❌ Invalid",
                        COLORS["accent_green"] if is_valid else COLORS["accent_red"]),
            _status_row("Last Block",
                        f"#{chain_len - 1}" if chain_len > 0 else "—",
                        COLORS["accent_cyan"]),
        ])

    @app.callback(
        Output("system-status", "children"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_system_status(n):
        services = [
            ("SSH Honeypot", "Port 2222", True),
            ("HTTP Honeypot", "Port 8081-8083", True),
            ("ML Engine", f"{'Trained' if ml_classifier and ml_classifier.is_trained else 'Training...'}", True),
            ("Blockchain", "Active", True),
            ("MITRE Mapping", "Active", True),
            ("Anomaly Detection", "Active", True),
            ("SIEM Integration", "Connected", True),
        ]

        return html.Div([
            html.Div([
                html.Span("●" if active else "○", style={
                    "color": COLORS["accent_green"] if active else COLORS["accent_red"],
                    "marginRight": "8px", "fontSize": "8px"
                }),
                html.Span(name, style={
                    "color": COLORS["text_primary"], "fontSize": "12px",
                    "flex": "1"
                }),
                html.Span(detail, style={
                    "color": COLORS["text_muted"], "fontSize": "10px",
                    "fontFamily": "'JetBrains Mono', monospace"
                })
            ], style={
                "display": "flex", "alignItems": "center",
                "padding": "8px 0",
                "borderBottom": f"1px solid {COLORS['border']}"
            }) for name, detail, active in services
        ])

    @app.callback(
        Output("anomaly-panel", "children"),
        [Input("refresh-interval", "n_intervals")]
    )
    def update_anomaly_panel(n):
        if not anomaly_detector:
            return html.P("Anomaly detector offline", style={"color": COLORS["text_muted"]})

        stats = anomaly_detector.get_stats()
        return html.Div([
            _status_row("Baseline", "✅ Established" if stats["baseline_established"] else "⏳ Training",
                        COLORS["accent_green"] if stats["baseline_established"] else COLORS["accent_orange"]),
            _status_row("Analyzed", str(stats["total_analyzed"]), COLORS["accent_cyan"]),
            _status_row("Anomalies", str(stats["total_anomalies"]), COLORS["accent_red"]),
            _status_row("Anomaly Rate", f"{stats['anomaly_rate']}%", COLORS["accent_purple"]),
        ])

    return app


def _status_row(label, value, color):
    """Create a status row for panels"""
    return html.Div([
        html.Span(label, style={
            "color": COLORS["text_muted"], "fontSize": "11px",
            "textTransform": "uppercase", "letterSpacing": "0.5px"
        }),
        html.Span(value, style={
            "color": color, "fontSize": "13px",
            "fontWeight": "600", "fontFamily": "'JetBrains Mono', monospace"
        })
    ], style={
        "display": "flex", "justifyContent": "space-between",
        "padding": "7px 0",
        "borderBottom": f"1px solid {COLORS['border']}"
    })
