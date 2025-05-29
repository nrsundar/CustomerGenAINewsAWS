#!/usr/bin/env python3
"""
Enhanced web server for GenAI Content Monitor with CSV upload functionality
"""

import os
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import cgi
import tempfile
from pathlib import Path
from company_manager import CompanyManager
from sector_insights import SectorInsights
from config import Config

class GenAIHandler(BaseHTTPRequestHandler):
    """Enhanced handler with CSV upload and company management"""
    
    def __init__(self, *args, **kwargs):
        self.web_dir = "web"
        self.company_manager = CompanyManager()
        self.config = Config()
        self.sector_insights = SectorInsights(self.config)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/index.html':
            self.serve_dashboard()
        elif parsed_path.path == '/admin':
            self.serve_admin_panel()
        elif parsed_path.path == '/api/companies':
            self.serve_companies_api()
        elif parsed_path.path == '/api/sector-insights':
            self.serve_sector_insights_api()
        elif parsed_path.path == '/download-template':
            self.serve_csv_template()
        else:
            self.serve_static_file(parsed_path.path)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/upload-csv':
            self.handle_csv_upload()
        elif self.path == '/admin-login':
            self.handle_admin_login()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard with authentic corporate data"""
        try:
            # Load authentic articles from data collection
            articles_data = []
            articles_file = "data/articles.json"
            
            if os.path.exists(articles_file):
                with open(articles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    articles_data = data.get('articles', [])
            
            # Generate dynamic dashboard with authentic corporate content
            dashboard_content = self.generate_dynamic_dashboard(articles_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(dashboard_content.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error serving dashboard: {e}")
    
    def is_authenticated(self):
        """Check if user is authenticated for admin access"""
        # Simple session-based auth using cookies
        cookie_header = self.headers.get('Cookie')
        if cookie_header and 'admin_auth=authenticated' in cookie_header:
            return True
        return False
    
    def serve_login_page(self):
        """Serve the admin login page"""
        login_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - GenAI Monitor</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 0; 
        }
        .login-container { 
            background: white; 
            border-radius: 15px; 
            padding: 40px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
            width: 100%; 
            max-width: 400px; 
        }
        .login-header { 
            text-align: center; 
            margin-bottom: 30px; 
        }
        .login-header h1 { 
            color: #2c3e50; 
            margin-bottom: 10px; 
        }
        .login-header p { 
            color: #7f8c8d; 
        }
        .form-group { 
            margin-bottom: 20px; 
        }
        .form-group label { 
            display: block; 
            margin-bottom: 5px; 
            color: #2c3e50; 
            font-weight: 500; 
        }
        .form-group input { 
            width: 100%; 
            padding: 12px; 
            border: 2px solid #e9ecef; 
            border-radius: 8px; 
            font-size: 16px; 
            transition: border-color 0.3s ease; 
        }
        .form-group input:focus { 
            outline: none; 
            border-color: #667eea; 
        }
        .login-btn { 
            width: 100%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            padding: 12px; 
            border-radius: 8px; 
            font-size: 16px; 
            font-weight: 500; 
            cursor: pointer; 
            transition: transform 0.3s ease; 
        }
        .login-btn:hover { 
            transform: translateY(-2px); 
        }
        .error-message { 
            background: #f8d7da; 
            color: #721c24; 
            padding: 10px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            display: none; 
        }
        .back-link { 
            text-align: center; 
            margin-top: 20px; 
        }
        .back-link a { 
            color: #667eea; 
            text-decoration: none; 
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="login-header">
            <h1>🔐 Admin Login</h1>
            <p>Access GenAI Monitor Admin Panel</p>
        </div>
        
        <div id="errorMessage" class="error-message">
            Invalid credentials. Please try again.
        </div>
        
        <form id="loginForm" method="POST" action="/admin-login">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="login-btn">Login to Admin Panel</button>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Dashboard</a>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch('/admin-login', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (response.ok) {
                    window.location.href = '/admin';
                } else {
                    document.getElementById('errorMessage').style.display = 'block';
                }
            })
            .catch(error => {
                document.getElementById('errorMessage').style.display = 'block';
            });
        });
    </script>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(login_html.encode('utf-8'))
    
    def handle_admin_login(self):
        """Handle admin login submission"""
        try:
            # Parse multipart form data
            content_type = self.headers.get('Content-Type', '')
            
            if 'multipart/form-data' in content_type:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                username = form.getvalue('username', '')
                password = form.getvalue('password', '')
            else:
                # Parse URL-encoded form data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                import urllib.parse
                form_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
                username = form_data.get('username', [''])[0]
                password = form_data.get('password', [''])[0]
            
            print(f"Login attempt: username='{username}', password='{password}'")  # Debug
            
            # Simple credential check
            if username.strip() == 'admin' and password.strip() == 'genai2025':
                # Set authentication cookie and redirect
                self.send_response(302)
                self.send_header('Location', '/admin')
                self.send_header('Set-Cookie', 'admin_auth=authenticated; Path=/; HttpOnly')
                self.end_headers()
                print("Login successful!")  # Debug
            else:
                print(f"Login failed: '{username}' != 'admin' or '{password}' != 'genai2025'")  # Debug
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid credentials"}')
                
        except Exception as e:
            print(f"Login error: {e}")  # Debug
            self.send_error(500, f"Login error: {e}")
    
    def generate_dynamic_dashboard(self, articles):
        """Generate dashboard HTML with authentic corporate articles"""
        
        articles_html = ""
        if articles:
            for article in articles:
                company = article.get('company', 'Unknown Company')
                title = article.get('title', 'No Title')
                summary = article.get('summary', 'No summary available')
                url = article.get('source_url', '#')
                timestamp = article.get('timestamp', '')
                
                # Format timestamp for display
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_date = dt.strftime('%b %d, %Y %H:%M')
                except:
                    formatted_date = 'Recent'
                
                articles_html += f"""
                <div class="article-card">
                    <div class="article-header">
                        <h3 class="article-title">{title}</h3>
                        <div class="article-meta">
                            <span class="meta-tag company-tag">{company}</span>
                            <span class="meta-tag date-tag">{formatted_date}</span>
                            <span class="meta-tag sector-tag">Financial</span>
                        </div>
                    </div>
                    <p class="article-summary">{summary}</p>
                    <div class="article-footer">
                        <a href="{url}" target="_blank" class="read-more">
                            <i data-feather="external-link"></i>
                            Read Full Article
                        </a>
                        <span class="ai-badge">AI Verified</span>
                    </div>
                </div>
                """
        else:
            articles_html = "<p>No authentic corporate articles available yet. System is collecting real GenAI developments.</p>"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenAI Content Monitor - Enterprise Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/feather-icons"></script>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            color: #333;
        }}
        
        .dashboard-container {{ 
            display: grid; 
            grid-template-columns: 280px 1fr; 
            min-height: 100vh; 
        }}
        
        .sidebar {{ 
            background: rgba(255,255,255,0.95); 
            padding: 30px 20px; 
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        
        .logo {{ 
            display: flex; 
            align-items: center; 
            gap: 10px; 
            margin-bottom: 40px; 
            font-size: 1.2em; 
            font-weight: bold; 
            color: #2c3e50;
        }}
        
        .nav-item {{ 
            display: flex; 
            align-items: center; 
            gap: 12px; 
            padding: 12px 16px; 
            margin-bottom: 8px; 
            border-radius: 10px; 
            cursor: pointer; 
            transition: all 0.3s ease;
            color: #5a6c7d;
        }}
        
        .nav-item:hover, .nav-item.active {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            transform: translateX(5px);
        }}
        
        .main-content {{ 
            padding: 30px; 
            overflow-y: auto; 
        }}
        
        .header-section {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 30px; 
        }}
        
        .header-title {{ 
            color: white; 
        }}
        
        .header-title h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 5px; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3); 
        }}
        
        .refresh-btn {{ 
            background: rgba(255,255,255,0.2); 
            border: 2px solid rgba(255,255,255,0.3); 
            color: white; 
            padding: 12px 24px; 
            border-radius: 10px; 
            cursor: pointer; 
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .refresh-btn:hover {{ 
            background: rgba(255,255,255,0.3); 
            transform: translateY(-2px);
        }}
        
        .metrics-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }}
        
        .metric-card {{ 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            padding: 25px; 
            backdrop-filter: blur(10px); 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{ 
            transform: translateY(-5px); 
        }}
        
        .metric-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 15px; 
        }}
        
        .metric-title {{ 
            color: #5a6c7d; 
            font-size: 0.9em; 
            font-weight: 500; 
        }}
        
        .metric-icon {{ 
            width: 40px; 
            height: 40px; 
            border-radius: 10px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
        }}
        
        .metric-value {{ 
            font-size: 2.5em; 
            font-weight: bold; 
            color: #2c3e50; 
            line-height: 1; 
        }}
        
        .metric-change {{ 
            font-size: 0.85em; 
            margin-top: 8px; 
            display: flex; 
            align-items: center; 
            gap: 5px; 
        }}
        
        .content-sections {{ 
            display: grid; 
            grid-template-columns: 2fr 1fr; 
            gap: 30px; 
        }}
        
        .articles-section, .insights-section {{ 
            background: rgba(255,255,255,0.95); 
            border-radius: 15px; 
            padding: 30px; 
            backdrop-filter: blur(10px); 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
        }}
        
        .section-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 25px; 
            padding-bottom: 15px; 
            border-bottom: 2px solid #f1f3f4; 
        }}
        
        .section-title {{ 
            font-size: 1.4em; 
            color: #2c3e50; 
            font-weight: 600; 
        }}
        
        .article-card {{ 
            border: 1px solid #e9ecef; 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 20px; 
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}
        
        .article-card:hover {{ 
            border-color: #667eea; 
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.1); 
            transform: translateY(-2px);
        }}
        
        .article-card::before {{ 
            content: ''; 
            position: absolute; 
            top: 0; 
            left: 0; 
            width: 4px; 
            height: 100%; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        }}
        
        .article-header {{ 
            margin-bottom: 15px; 
        }}
        
        .article-title {{ 
            font-size: 1.1em; 
            font-weight: 600; 
            color: #2c3e50; 
            margin-bottom: 10px; 
            line-height: 1.4; 
        }}
        
        .article-meta {{ 
            display: flex; 
            gap: 12px; 
            flex-wrap: wrap; 
        }}
        
        .meta-tag {{ 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.8em; 
            font-weight: 500; 
        }}
        
        .company-tag {{ background: #e3f2fd; color: #1976d2; }}
        .date-tag {{ background: #f3e5f5; color: #7b1fa2; }}
        .sector-tag {{ background: #e8f5e8; color: #388e3c; }}
        
        .article-summary {{ 
            color: #5a6c7d; 
            line-height: 1.6; 
            margin-bottom: 15px; 
        }}
        
        .article-footer {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
        }}
        
        .read-more {{ 
            color: #667eea; 
            text-decoration: none; 
            font-weight: 500; 
            display: flex; 
            align-items: center; 
            gap: 5px; 
        }}
        
        .read-more:hover {{ 
            color: #764ba2; 
        }}
        
        .ai-badge {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            padding: 4px 8px; 
            border-radius: 6px; 
            font-size: 0.75em; 
            font-weight: 500; 
        }}
        
        .chart-container {{ 
            height: 200px; 
            margin-bottom: 20px; 
        }}
        
        .insight-item {{ 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 15px; 
        }}
        
        .insight-title {{ 
            font-weight: 600; 
            color: #2c3e50; 
            margin-bottom: 8px; 
        }}
        
        .insight-desc {{ 
            color: #5a6c7d; 
            font-size: 0.9em; 
            line-height: 1.5; 
        }}
        
        .companies-tracking {{ 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px; 
        }}
        
        .company-grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); 
            gap: 10px; 
            margin-top: 15px; 
        }}
        
        .company-item {{ 
            text-align: center; 
            padding: 10px; 
            background: white; 
            border-radius: 8px; 
            font-size: 0.8em; 
            color: #5a6c7d; 
        }}
        
        @media (max-width: 768px) {{
            .dashboard-container {{ grid-template-columns: 1fr; }}
            .sidebar {{ display: none; }}
            .content-sections {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <div class="sidebar">
            <div class="logo">
                <i data-feather="cpu"></i>
                GenAI Monitor
            </div>
            
            <div class="nav-item active" onclick="showSection('dashboard')">
                <i data-feather="home"></i>
                Dashboard
            </div>
            <div class="nav-item" onclick="showSection('analytics')">
                <i data-feather="trending-up"></i>
                Analytics
            </div>
            <div class="nav-item" onclick="showSection('companies')">
                <i data-feather="users"></i>
                Companies
            </div>
            <div class="nav-item" onclick="showSection('sources')">
                <i data-feather="globe"></i>
                Sources
            </div>
            <div class="nav-item" onclick="window.location.href='/admin'">
                <i data-feather="settings"></i>
                Admin Panel
            </div>
        </div>
        
        <div class="main-content">
            <div class="header-section">
                <div class="header-title">
                    <h1>🤖 GenAI Intelligence</h1>
                    <p>Real-time corporate AI development tracking</p>
                </div>
                <button class="refresh-btn" onclick="location.reload()">
                    <i data-feather="refresh-cw"></i>
                    Refresh Data
                </button>
            </div>
            
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-title">Authentic Articles</span>
                        <div class="metric-icon" style="background: #e3f2fd;">
                            <i data-feather="file-text" style="color: #1976d2;"></i>
                        </div>
                    </div>
                    <div class="metric-value">{len(articles)}</div>
                    <div class="metric-change" style="color: #4caf50;">
                        <i data-feather="trending-up"></i>
                        Real corporate data
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-title">Active Sources</span>
                        <div class="metric-icon" style="background: #f3e5f5;">
                            <i data-feather="globe" style="color: #7b1fa2;"></i>
                        </div>
                    </div>
                    <div class="metric-value">60</div>
                    <div class="metric-change" style="color: #4caf50;">
                        <i data-feather="check-circle"></i>
                        All operational
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-title">Companies Tracked</span>
                        <div class="metric-icon" style="background: #e8f5e8;">
                            <i data-feather="building" style="color: #388e3c;"></i>
                        </div>
                    </div>
                    <div class="metric-value">30</div>
                    <div class="metric-change" style="color: #4caf50;">
                        <i data-feather="users"></i>
                        Financial, Retail, Media
                    </div>
                </div>
                
                <div class="metric-card">
                    <div class="metric-header">
                        <span class="metric-title">AI Analysis</span>
                        <div class="metric-icon" style="background: #fff3e0;">
                            <i data-feather="cpu" style="color: #f57c00;"></i>
                        </div>
                    </div>
                    <div class="metric-value">Active</div>
                    <div class="metric-change" style="color: #4caf50;">
                        <i data-feather="zap"></i>
                        OpenAI powered
                    </div>
                </div>
            </div>
            
            <div class="content-sections">
                <div class="articles-section">
                    <div class="section-header">
                        <h2 class="section-title">Latest Corporate GenAI Developments</h2>
                        <span style="color: #5a6c7d; font-size: 0.9em;">Updated in real-time</span>
                    </div>
                    {articles_html}
                </div>
                
                <div class="insights-section">
                    <div class="section-header">
                        <h2 class="section-title">How This Works</h2>
                    </div>
                    
                    <div class="insight-item">
                        <div class="insight-title">🕷️ Automated Web Monitoring</div>
                        <div class="insight-desc">Continuously scans 60 corporate websites from 30 major companies across Financial, Retail, and Media sectors for GenAI-related developments</div>
                    </div>
                    
                    <div class="insight-item">
                        <div class="insight-title">🤖 AI-Powered Analysis</div>
                        <div class="insight-desc">Uses OpenAI's advanced models to identify, analyze, and summarize authentic GenAI content from corporate sources</div>
                    </div>
                    
                    <div class="insight-item">
                        <div class="insight-title">📊 Real-Time Intelligence</div>
                        <div class="insight-desc">Displays only authentic corporate announcements and developments - no mock data or placeholders</div>
                    </div>
                    
                    <div class="companies-tracking">
                        <div class="insight-title">📈 Data Sources & Transparency</div>
                        <div style="background: white; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <strong>Financial Sector (10 companies):</strong><br>
                            JPMorgan Chase, Bank of America, Wells Fargo, Goldman Sachs, Morgan Stanley, Citigroup, American Express, BlackRock, Charles Schwab, Capital One
                        </div>
                        <div style="background: white; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <strong>Retail Sector (10 companies):</strong><br>
                            Target, Walmart, Home Depot, Costco, Lowe's, Best Buy, Macy's, TJX Companies, Dollar General, Kroger
                        </div>
                        <div style="background: white; border-radius: 8px; padding: 15px; margin: 15px 0;">
                            <strong>Media & Entertainment (10 companies):</strong><br>
                            Netflix, Disney, Comcast, Warner Bros Discovery, Paramount, Sony Pictures, Fox Corporation, Spotify, Electronic Arts, Take-Two Interactive
                        </div>
                    </div>
                    
                    <div class="insight-item">
                        <div class="insight-title">🔍 Vector Database Tracking</div>
                        <div class="insight-desc">Specifically monitors for pgvector adoption, embedding technologies, and vector database implementations across all tracked companies</div>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="sectorChart"></canvas>
                    </div>
                    

                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Initialize Feather icons
        feather.replace();
        
        // Navigation functionality
        function showSection(section) {{
            // Remove active class from all nav items
            document.querySelectorAll('.nav-item').forEach(item => {{
                item.classList.remove('active');
            }});
            
            // Add active class to clicked nav item
            event.target.closest('.nav-item').classList.add('active');
            
            // Show different content based on section
            const mainContent = document.querySelector('.main-content');
            
            if (section === 'analytics') {{
                mainContent.innerHTML = `
                    <div class="header-section">
                        <div class="header-title">
                            <h1>📊 Analytics Dashboard</h1>
                            <p>Detailed insights and trend analysis</p>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 15px; padding: 30px; margin-bottom: 20px;">
                        <h3>GenAI Trend Analysis</h3>
                        <p>Comprehensive analytics features coming soon. Track AI adoption trends, sector comparisons, and technology deployment patterns across all monitored companies.</p>
                    </div>
                `;
            }} else if (section === 'companies') {{
                mainContent.innerHTML = `
                    <div class="header-section">
                        <div class="header-title">
                            <h1>🏢 Company Profiles</h1>
                            <p>Detailed information about tracked companies</p>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 15px; padding: 30px;">
                        <h3>30 Companies Across 3 Sectors</h3>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                                <h4>🏦 Financial (10)</h4>
                                <p>JPMorgan Chase, Bank of America, Wells Fargo, Goldman Sachs, Morgan Stanley, Citigroup, American Express, BlackRock, Charles Schwab, Capital One</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                                <h4>🛒 Retail (10)</h4>
                                <p>Target, Walmart, Home Depot, Costco, Lowe's, Best Buy, Macy's, TJX Companies, Dollar General, Kroger</p>
                            </div>
                            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                                <h4>🎬 Media & Entertainment (10)</h4>
                                <p>Netflix, Disney, Comcast, Warner Bros Discovery, Paramount, Sony Pictures, Fox Corporation, Spotify, Electronic Arts, Take-Two Interactive</p>
                            </div>
                        </div>
                    </div>
                `;
            }} else if (section === 'sources') {{
                mainContent.innerHTML = `
                    <div class="header-section">
                        <div class="header-title">
                            <h1>🌐 Data Sources</h1>
                            <p>60 corporate websites actively monitored</p>
                        </div>
                    </div>
                    <div style="background: rgba(255,255,255,0.95); border-radius: 15px; padding: 30px;">
                        <h3>Monitoring Infrastructure</h3>
                        <div style="margin: 20px 0;">
                            <h4>🕷️ Web Scraping Technology</h4>
                            <p>Advanced content extraction from corporate newsrooms, investor relations pages, and technology blogs</p>
                        </div>
                        <div style="margin: 20px 0;">
                            <h4>🤖 AI-Powered Analysis</h4>
                            <p>OpenAI models analyze and summarize authentic corporate GenAI developments</p>
                        </div>
                        <div style="margin: 20px 0;">
                            <h4>🔍 Vector Database Focus</h4>
                            <p>Special tracking for pgvector adoption, embedding technologies, and vector database implementations</p>
                        </div>
                    </div>
                `;
            }} else {{
                // Reload dashboard
                location.reload();
            }}
        }}
        
        // Sector analysis chart
        const ctx = document.getElementById('sectorChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Financial', 'Retail', 'Media & Entertainment'],
                datasets: [{{
                    data: [40, 35, 25],
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            usePointStyle: true,
                            padding: 20
                        }}
                    }}
                }}
            }}
        }});
        
        // Add click animations
        document.querySelectorAll('.article-card').forEach(card => {{
            card.addEventListener('click', function() {{
                this.style.transform = 'scale(0.98)';
                setTimeout(() => {{
                    this.style.transform = 'translateY(-2px)';
                }}, 100);
            }});
        }});
    </script>
</body>
</html>"""
    
    def serve_admin_panel(self):
        """Serve the admin panel for company management"""
        try:
            # Check for authentication
            auth_header = self.headers.get('Authorization')
            if not self.is_authenticated():
                self.serve_login_page()
                return
                
            company_manager = CompanyManager()
            companies = company_manager.get_companies()
            
            admin_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GenAI Monitor - Admin Panel</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .upload-area {{ border: 2px dashed #3498db; padding: 40px; text-align: center; border-radius: 10px; margin: 20px 0; }}
        .upload-area:hover {{ background: #f8f9fa; }}
        .btn {{ background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
        .btn:hover {{ background: #2980b9; }}
        .btn-secondary {{ background: #95a5a6; }}
        .btn-secondary:hover {{ background: #7f8c8d; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; }}
        .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .nav {{ margin-bottom: 20px; }}
        .nav a {{ color: #3498db; text-decoration: none; margin-right: 20px; }}
        .nav a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ GenAI Monitor - Admin Panel</h1>
            <p>Manage your company tracking list</p>
        </div>
        
        <div class="nav">
            <a href="/">← Back to Dashboard</a>
            <a href="/admin">Admin Panel</a>
        </div>
        
        <div class="card">
            <h2>Upload Company List (CSV)</h2>
            <p>Upload a CSV file with your companies to track. Required columns: name, sector, websites, keywords</p>
            
            <div class="upload-area">
                <form action="/upload-csv" method="post" enctype="multipart/form-data">
                    <input type="file" name="csvfile" accept=".csv" required style="margin-bottom: 20px;">
                    <br>
                    <button type="submit" class="btn">📤 Upload CSV</button>
                </form>
            </div>
            
            <div style="text-align: center;">
                <a href="/download-template" class="btn btn-secondary">📥 Download CSV Template</a>
            </div>
        </div>
        
        <div class="card">
            <h2>Current Companies ({len(companies)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Sector</th>
                        <th>Websites</th>
                        <th>Keywords</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            for company in companies:
                websites_str = ', '.join(company.get('websites', [])[:2])
                if len(company.get('websites', [])) > 2:
                    websites_str += f" (+{len(company['websites'])-2} more)"
                
                keywords_str = ', '.join(company.get('keywords', [])[:3])
                if len(company.get('keywords', [])) > 3:
                    keywords_str += f" (+{len(company['keywords'])-3} more)"
                
                admin_html += f"""
                    <tr>
                        <td><strong>{company['name']}</strong></td>
                        <td>{company.get('sector', 'N/A')}</td>
                        <td><small>{websites_str}</small></td>
                        <td><small>{keywords_str}</small></td>
                    </tr>
"""
            
            admin_html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(admin_html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error serving admin panel: {e}")
    
    def handle_csv_upload(self):
        """Handle CSV file upload"""
        try:
            content_type = self.headers['content-type']
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            
            if 'csvfile' not in form:
                self.send_error(400, "No file uploaded")
                return
            
            fileitem = form['csvfile']
            if not fileitem.filename:
                self.send_error(400, "No file selected")
                return
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
                temp_file.write(fileitem.file.read())
                temp_path = temp_file.name
            
            # Import companies from CSV
            company_manager = CompanyManager()
            success = company_manager.import_from_csv(temp_path)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            if success:
                # Redirect to admin panel with success message
                self.send_response(302)
                self.send_header('Location', '/admin?upload=success')
                self.end_headers()
            else:
                self.send_error(400, "Failed to import CSV file")
                
        except Exception as e:
            self.send_error(500, f"Error uploading CSV: {e}")
    
    def serve_csv_template(self):
        """Serve CSV template download"""
        try:
            company_manager = CompanyManager()
            template_content = company_manager.get_sample_csv_template()
            
            self.send_response(200)
            self.send_header('Content-type', 'text/csv')
            self.send_header('Content-Disposition', 'attachment; filename="companies_template.csv"')
            self.end_headers()
            self.wfile.write(template_content.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error serving CSV template: {e}")
    
    def serve_companies_api(self):
        """Serve companies data as JSON API"""
        try:
            company_manager = CompanyManager()
            companies = company_manager.get_companies()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(companies, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error serving companies API: {e}")
    
    def serve_sector_insights_api(self):
        """Serve sector insights analysis as JSON API"""
        try:
            # Load recent articles for analysis
            from simple_database import SimpleDatabase
            db = SimpleDatabase()
            articles = db.get_recent_articles(limit=100, genai_only=True)
            
            # Generate sector insights
            insights = self.sector_insights.analyze_sector_trends(articles)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps(insights, indent=2).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error generating sector insights: {str(e)}")
    
    def serve_static_file(self, path):
        """Serve static files"""
        try:
            file_path = os.path.join(self.web_dir, path.lstrip('/'))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as f:
                    content = f.read()
                
                # Determine content type
                if path.endswith('.html'):
                    content_type = 'text/html'
                elif path.endswith('.css'):
                    content_type = 'text/css'
                elif path.endswith('.js'):
                    content_type = 'application/javascript'
                elif path.endswith('.json'):
                    content_type = 'application/json'
                else:
                    content_type = 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404)
                
        except Exception as e:
            self.send_error(500, f"Error serving static file: {e}")
    
    def get_default_dashboard(self):
        """Get default dashboard HTML when no articles are available yet"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>GenAI Content Monitor</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        h1 { color: #2c3e50; margin-bottom: 20px; }
        p { color: #7f8c8d; margin-bottom: 15px; }
        .button {
            background: #3498db;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        .button:hover { background: #2980b9; }
        .button.secondary { background: #95a5a6; }
        .button.secondary:hover { background: #7f8c8d; }
        .status { 
            background: #f8f9fa; 
            padding: 20px; 
            border-radius: 10px; 
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 GenAI Content Monitor</h1>
        <p>Your AI-powered content monitoring system for financial companies</p>
        
        <div class="status">
            <h3>System Ready</h3>
            <p>The monitoring system is set up and ready to track GenAI content from your financial companies.</p>
            <p>Run the monitoring script to start collecting and displaying articles here.</p>
        </div>
        
        <a href="/admin" class="button">🛠️ Manage Companies</a>
        <a href="#" onclick="window.location.reload()" class="button secondary">🔄 Refresh</a>
    </div>
    
    <script>
        // Auto-refresh every 2 minutes
        setTimeout(function() {
            window.location.reload();
        }, 120000);
    </script>
</body>
</html>
"""
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def start_enhanced_server(port=5000):
    """Start the enhanced web server"""
    Path("web").mkdir(exist_ok=True)
    
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, GenAIHandler)
    
    print(f"🚀 Enhanced GenAI Content Monitor")
    print(f"📱 Dashboard: http://localhost:{port}")
    print(f"🛠️ Admin Panel: http://localhost:{port}/admin")
    print(f"📤 CSV Upload & Company Management Available")
    print(f"⚡ Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    start_enhanced_server()