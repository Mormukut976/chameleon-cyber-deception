import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd

class AIDashboard:
    def __init__(self, deception_engine=None):
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("AIDashboard")
        
        self.app = dash.Dash(__name__, external_stylesheets=[
            'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'
        ])
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """AI-enhanced dashboard layout"""
        self.app.layout = html.Div([
            # Header with AI Status
            html.Div([
                html.H1("🦎 Chameleon AI-Powered Cyber Deception", 
                       style={'textAlign': 'center', 'color': 'white', 
                              'backgroundColor': '#2c3e50', 'padding': '20px', 
                              'marginBottom': '20px'}),
                html.P("Advanced Threat Intelligence & Automated Response", 
                      style={'textAlign': 'center', 'color': '#ecf0f1'})
            ]),
            
            # AI Status Card
            html.Div([
                html.Div([
                    html.H4("🤖 AI System Status", style={'color': '#2c3e50'}),
                    html.Div(id="ai-status", className="alert alert-success")
                ], className="card-body")
            ], className="card", style={'margin': '10px'}),
            
            # AI Insights Section
            html.Div([
                html.H3("🎯 AI Threat Insights", style={'marginTop': '20px'}),
                html.Div(id="ai-insights-container")
            ], className="row"),
            
            # Stats Cards with AI Enhancements
            html.Div([
                html.Div([
                    html.Div([
                        html.H2("0", id="total-attacks"),
                        html.P("Total Attacks"),
                        html.Small("AI Analyzed", style={'color': '#27ae60'})
                    ], className="card-body text-center")
                ], className="card border-primary m-2"),
                
                html.Div([
                    html.Div([
                        html.H2("0", id="ai-threats"),
                        html.P("AI-Classified Threats"),
                        html.Small("High Confidence", style={'color': '#e74c3c'})
                    ], className="card-body text-center")
                ], className="card border-danger m-2"),
                
                html.Div([
                    html.Div([
                        html.H2("0", id="attacker-profiles"),
                        html.P("Attacker Profiles"),
                        html.Small("Behavioral Analysis", style={'color': '#f39c12'})
                    ], className="card-body text-center")
                ], className="card border-warning m-2"),
                
                html.Div([
                    html.Div([
                        html.H2("0%", id="ai-accuracy"),
                        html.P("AI Prediction Rate"),
                        html.Small("Machine Learning", style={'color': '#9b59b6'})
                    ], className="card-body text-center")
                ], className="card border-info m-2"),
            ], className="row", style={'display': 'flex', 'justifyContent': 'center'}),
            
            # AI Analysis Charts
            html.Div([
                html.Div([
                    html.H4("AI Threat Level Analysis"),
                    dcc.Graph(id="ai-threat-timeline")
                ], className="col-md-6"),
                
                html.Div([
                    html.H4("Attacker Skill Distribution"),
                    dcc.Graph(id="attacker-skill-chart")
                ], className="col-md-6"),
            ], className="row mt-4"),
            
            # Advanced Attacker Profiles
            html.Div([
                html.H3("🔍 Advanced Attacker Profiles", className="mt-4"),
                html.Div(id="attacker-profiles-table")
            ]),
            
            # AI Recommendations
            html.Div([
                html.H3("💡 AI Security Recommendations", className="mt-4"),
                html.Div(id="ai-recommendations")
            ]),
            
            dcc.Interval(id='interval-component', interval=3000, n_intervals=0)
        ], className="container-fluid")
    
    def setup_callbacks(self):
        """AI-enhanced callbacks"""
        
        @self.app.callback(
            [Output('total-attacks', 'children'),
             Output('ai-threats', 'children'),
             Output('attacker-profiles', 'children'),
             Output('ai-accuracy', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_ai_stats(n):
            if not self.deception_engine:
                return "0", "0", "0", "0%"
            
            try:
                total_attacks = len(self.deception_engine.attack_log)
                
                # AI-enhanced stats
                ai_enhanced_attacks = sum(1 for a in self.deception_engine.attack_log 
                                        if a.get('ai_enhanced', False))
                attacker_profiles = len(self.deception_engine.attacker_profiles)
                
                # AI accuracy (simulated)
                ai_accuracy = (ai_enhanced_attacks / total_attacks * 100) if total_attacks > 0 else 0
                
                return str(total_attacks), str(ai_enhanced_attacks), str(attacker_profiles), f"{ai_accuracy:.1f}%"
                
            except Exception as e:
                self.logger.error(f"AI stats error: {e}")
                return "0", "0", "0", "0%"
        
        @self.app.callback(
            Output('ai-status', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_ai_status(n):
            if not hasattr(self.deception_engine, 'threat_analyzer'):
                return html.Div("⚠️ AI System: OFFLINE", className="alert alert-warning")
            
            try:
                status_msg = "✅ AI System: ACTIVE - Real-time threat analysis enabled"
                return html.Div(status_msg, className="alert alert-success")
            except:
                return html.Div("⚠️ AI System: INITIALIZING", className="alert alert-warning")
        
        @self.app.callback(
            Output('ai-insights-container', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_ai_insights(n):
            if not self.deception_engine or not hasattr(self.deception_engine, 'ai_insights'):
                return html.P("No AI insights available yet.", className="text-muted")
            
            try:
                insights = self.deception_engine.ai_insights
                if not insights:
                    return html.P("AI is analyzing attack patterns...", className="text-muted")
                
                insight_elements = []
                for insight in insights[-3:]:  # Show last 3 insights
                    alert_class = "alert-danger" if insight.get('priority') == 'high' else "alert-warning"
                    insight_elements.append(
                        html.Div([
                            html.Strong(f"{insight['type'].replace('_', ' ').title()}"),
                            html.Br(),
                            html.Span(insight['message']),
                            html.Br(),
                            html.Small(insight['timestamp'], className="text-muted")
                        ], className=f"alert {alert_class}", style={'margin': '5px'})
                    )
                
                return insight_elements
            except Exception as e:
                return html.P(f"AI insights error: {e}", className="text-danger")
        
        @self.app.callback(
            Output('attacker-profiles-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_attacker_profiles(n):
            if not self.deception_engine or not self.deception_engine.attacker_profiles:
                return html.P("No attacker profiles generated yet.", className="text-muted")
            
            try:
                profiles = self.deception_engine.attacker_profiles
                
                table_header = [
                    html.Thead(html.Tr([
                        html.Th("IP Address"),
                        html.Th("Threat Level"),
                        html.Th("Skill Level"),
                        html.Th("Techniques"),
                        html.Th("AI Prediction")
                    ]))
                ]
                
                table_rows = []
                for ip, profile in list(profiles.items())[-5:]:  # Last 5 profiles
                    threat_level = profile['threat_level']
                    skill_level = profile['attacker_skill_level']
                    techniques = ", ".join(profile['techniques_used'][:2])  # First 2 techniques
                    prediction = profile['predicted_next_attack']
                    
                    # Color coding
                    threat_color = "danger" if threat_level > 0.7 else "warning" if threat_level > 0.4 else "info"
                    skill_color = "danger" if skill_level > 7 else "warning" if skill_level > 4 else "info"
                    
                    table_rows.append(html.Tr([
                        html.Td(ip),
                        html.Td(f"{threat_level:.2f}", className=f"text-{threat_color}"),
                        html.Td(f"{skill_level}/10", className=f"text-{skill_color}"),
                        html.Td(techniques),
                        html.Td(prediction.replace('_', ' ').title())
                    ]))
                
                return html.Table(table_header + [html.Tbody(table_rows)], 
                                className="table table-striped table-hover")
                
            except Exception as e:
                return html.P(f"Error loading profiles: {e}", className="text-danger")
        
        @self.app.callback(
            Output('ai-recommendations', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_ai_recommendations(n):
            if not self.deception_engine or not self.deception_engine.attacker_profiles:
                return html.P("AI is analyzing patterns to provide recommendations...", 
                            className="text-muted")
            
            try:
                profiles = self.deception_engine.attacker_profiles
                high_threat = any(p['threat_level'] > 0.7 for p in profiles.values())
                skilled_attackers = any(p['attacker_skill_level'] > 7 for p in profiles.values())
                
                recommendations = []
                
                if high_threat:
                    recommendations.append(
                        html.Li("🚨 Enable enhanced logging and monitoring for high-threat IPs")
                    )
                
                if skilled_attackers:
                    recommendations.append(
                        html.Li("🎯 Deploy advanced deception tactics for skilled attackers")
                    )
                
                if len(profiles) > 5:
                    recommendations.append(
                        html.Li("📈 Consider increasing honeypot capacity - multiple attackers detected")
                    )
                
                if not recommendations:
                    recommendations.append(
                        html.Li("✅ Current deception levels are appropriate for detected threats")
                    )
                
                return html.Ul(recommendations, className="list-group")
                
            except Exception as e:
                return html.P(f"Recommendations error: {e}", className="text-danger")

# Update dashboard start function
async def start_ai_dashboard(deception_engine=None):
    """Start the AI-enhanced dashboard"""
    try:
        dashboard = AIDashboard(deception_engine)
        
        import threading
        def run_dashboard():
            dashboard.app.run_server(host='0.0.0.0', port=8050, debug=False)
        
        thread = threading.Thread(target=run_dashboard, daemon=True)
        thread.start()
        
        print("✅ AI Dashboard started at http://localhost:8050")
        return True
    except Exception as e:
        print(f"❌ AI Dashboard failed: {e}")
        return False
