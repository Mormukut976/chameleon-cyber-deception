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

class ChameleonDashboard:
    def __init__(self, deception_engine=None):
        self.deception_engine = deception_engine
        self.logger = logging.getLogger("Dashboard")
        
        try:
            self.app = dash.Dash(__name__, external_stylesheets=[
                'https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css'
            ])
            self.setup_layout()
            self.setup_callbacks()
            self.logger.info("✅ Dashboard initialized successfully")
        except Exception as e:
            self.logger.error(f"❌ Dashboard initialization failed: {e}")
            raise
    
    def setup_layout(self):
        """Setup the dashboard layout"""
        try:
            self.app.layout = html.Div([
                # Header
                html.Div([
                    html.H1("🦎 Chameleon Cyber Deception Framework", 
                           style={'textAlign': 'center', 'color': 'white', 'backgroundColor': 'black', 'padding': '20px', 'marginBottom': '20px'}),
                ]),
                
                # Stats Cards
                html.Div([
                    html.Div([
                        html.Div([
                            html.H2("0", id="total-attacks", style={'fontSize': '2.5rem', 'color': 'red'}),
                            html.P("Total Attacks", style={'fontSize': '1.2rem'})
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={'border': '2px solid red', 'margin': '10px', 'borderRadius': '10px'}),
                    
                    html.Div([
                        html.Div([
                            html.H2("0", id="unique-ips", style={'fontSize': '2.5rem', 'color': 'orange'}),
                            html.P("Unique IPs", style={'fontSize': '1.2rem'})
                        ], style={'textAlign': 'center', 'padding': '20px'})
                    ], style={'border': '2px solid orange', 'margin': '10px', 'borderRadius': '10px'}),
                ], style={'display': 'flex', 'justifyContent': 'center'}),
                
                # Recent Attacks
                html.Div([
                    html.H3("Recent Attacks", style={'marginTop': '30px', 'textAlign': 'center'}),
                    html.Div(id="recent-attacks", style={'margin': '20px', 'padding': '15px', 'border': '1px solid #ccc', 'borderRadius': '5px'})
                ]),
                
                # Auto-update component
                dcc.Interval(
                    id='interval-component',
                    interval=3000,  # Update every 3 seconds
                    n_intervals=0
                )
            ], style={'fontFamily': 'Arial, sans-serif'})
            
            self.logger.info("✅ Dashboard layout setup complete")
        except Exception as e:
            self.logger.error(f"❌ Layout setup failed: {e}")
            raise
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('total-attacks', 'children'),
             Output('unique-ips', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_stats(n):
            try:
                if not self.deception_engine:
                    return "0", "0"
                
                total_attacks = len(self.deception_engine.attack_log)
                unique_ips = len(set(attack['source_ip'] for attack in self.deception_engine.attack_log))
                
                return str(total_attacks), str(unique_ips)
            except Exception as e:
                self.logger.error(f"Error updating stats: {e}")
                return "0", "0"
        
        @self.app.callback(
            Output('recent-attacks', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_recent_attacks(n):
            try:
                if not self.deception_engine or not self.deception_engine.attack_log:
                    return html.P("No attacks recorded yet.", style={'color': 'gray'})
                
                # Get last 5 attacks
                recent_attacks = sorted(
                    self.deception_engine.attack_log,
                    key=lambda x: x['timestamp'],
                    reverse=True
                )[:5]
                
                attack_elements = []
                for attack in recent_attacks:
                    timestamp = datetime.fromisoformat(attack['timestamp']).strftime('%H:%M:%S')
                    attack_elements.append(html.Div([
                        html.Strong(f"{timestamp} - {attack['source_ip']}"),
                        html.Br(),
                        html.Span(f"Type: {attack['attack_type']}"),
                        html.Br(),
                        html.Span(f"Details: {attack['details'][:50]}...")
                    ], style={
                        'padding': '10px', 
                        'margin': '5px', 
                        'border': '1px solid #ddd',
                        'borderRadius': '5px',
                        'backgroundColor': '#f9f9f9'
                    }))
                
                return attack_elements
                
            except Exception as e:
                self.logger.error(f"Error updating attacks: {e}")
                return html.P(f"Error loading attacks: {e}", style={'color': 'red'})
    
    def start_server(self):
        """Start the dashboard server"""
        try:
            self.logger.info("🚀 Starting dashboard server on http://0.0.0.0:8050")
            self.app.run_server(
                host='0.0.0.0', 
                port=8050, 
                debug=False,
                dev_tools_ui=False,
                dev_tools_props_check=False
            )
        except Exception as e:
            self.logger.error(f"❌ Dashboard server failed: {e}")
            raise

# Function to be imported from main.py
async def start_dashboard(deception_engine=None):
    """Start the dashboard (called from main.py)"""
    try:
        dashboard = ChameleonDashboard(deception_engine)
        
        # Run in thread since Dash is blocking
        import threading
        def run_dashboard():
            dashboard.start_server()
        
        thread = threading.Thread(target=run_dashboard, daemon=True)
        thread.start()
        
        print("✅ Dashboard thread started successfully")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard failed to start: {e}")
        return False
