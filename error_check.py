
#!/usr/bin/env python
"""
N1O1 Clinical Trials - Error Checking Utility
This script checks for common configuration issues and errors
"""
import os
import sys
import requests
import socket
import json
from datetime import datetime

# ANSI colors for better readability
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}  {text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_success(text):
    """Print a success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print a warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    """Print an error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print an info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def check_port_config():
    """Check for port configuration consistency"""
    print_header("Checking Port Configuration")
    
    # Check environment variables
    port_env = os.environ.get('PORT')
    if port_env:
        print_success(f"PORT environment variable is set to {port_env}")
    else:
        print_warning("PORT environment variable is not set. Default port 5000 will be used.")
    
    # Check .replit file
    try:
        with open('.replit', 'r') as f:
            replit_content = f.read()
            if '--bind 0.0.0.0:$PORT' in replit_content:
                print_success(".replit file correctly uses $PORT environment variable")
            elif '--bind 0.0.0.0:5000' in replit_content:
                print_warning(".replit file uses hardcoded port 5000 instead of $PORT")
            else:
                print_info(".replit file doesn't contain port binding information or uses a different format")
    except FileNotFoundError:
        print_error(".replit file not found")
    
    # Check Procfile
    try:
        with open('Procfile', 'r') as f:
            procfile_content = f.read()
            if '--bind 0.0.0.0:$PORT' in procfile_content:
                print_success("Procfile correctly uses $PORT environment variable")
            elif '--bind 0.0.0.0:5000' in procfile_content:
                print_warning("Procfile uses hardcoded port 5000 instead of $PORT")
            else:
                print_info("Procfile doesn't contain port binding information or uses a different format")
    except FileNotFoundError:
        print_warning("Procfile not found")
    
    # Check main.py for proper port handling
    try:
        with open('main.py', 'r') as f:
            main_content = f.read()
            if "port = int(environ.get('PORT', 5000))" in main_content:
                print_success("main.py correctly handles PORT environment variable")
            elif "port = int(os.environ.get('PORT', 5000))" in main_content:
                print_success("main.py correctly handles PORT environment variable")
            elif "port = 5000" in main_content:
                print_warning("main.py uses hardcoded port 5000")
            else:
                print_info("main.py port configuration not found or uses a different format")
    except FileNotFoundError:
        print_error("main.py file not found")

def check_server_status():
    """Check if the server is running and responsive"""
    print_header("Checking Server Status")
    
    try:
        # Try to connect to the server
        port = int(os.environ.get('PORT', 5000))
        print_info(f"Attempting to connect to server on port {port}...")
        
        # Check if socket is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('0.0.0.0', port))
        if result == 0:
            print_success(f"Server is running on port {port}")
        else:
            print_warning(f"Server doesn't appear to be running on port {port}")
        sock.close()
        
        # Try HTTP request
        try:
            response = requests.get(f"http://localhost:{port}/ping", timeout=2)
            if response.status_code == 200:
                print_success(f"Server responded to ping: {response.text}")
            else:
                print_warning(f"Server responded with status code {response.status_code}")
        except requests.RequestException as e:
            print_warning(f"HTTP request failed: {str(e)}")
            
        # Try system health check
        try:
            response = requests.get(f"http://localhost:{port}/system/health", timeout=2)
            if response.status_code == 200:
                health_data = response.json()
                print_success(f"System health: {health_data.get('status', 'unknown')}")
                print_info(f"Database: {health_data.get('database', 'unknown')}")
                print_info(f"Session: {health_data.get('session', 'unknown')}")
            else:
                print_warning(f"Health check responded with status code {response.status_code}")
        except requests.RequestException as e:
            print_warning(f"Health check request failed: {str(e)}")
            
    except Exception as e:
        print_error(f"Error checking server status: {str(e)}")

def check_logs():
    """Check log files for errors"""
    print_header("Checking Log Files")
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        print_warning(f"Log directory '{log_dir}' not found")
        return
        
    log_files = [f for f in os.listdir(log_dir) if f.endswith('.log')]
    if not log_files:
        print_warning("No log files found")
        return
        
    # Get most recent log file
    today = datetime.now().strftime('%Y%m%d')
    today_log = f"nitrite_dynamics_{today}.log"
    
    if today_log in log_files:
        log_path = os.path.join(log_dir, today_log)
    else:
        # Use most recent log file
        log_files.sort(reverse=True)
        log_path = os.path.join(log_dir, log_files[0])
    
    print_info(f"Analyzing log file: {log_path}")
    
    try:
        with open(log_path, 'r') as f:
            log_content = f.readlines()
            
        # Count errors and warnings
        error_count = 0
        warning_count = 0
        
        errors = []
        for line in log_content:
            if " ERROR " in line:
                error_count += 1
                errors.append(line.strip())
            elif " WARNING " in line:
                warning_count += 1
                
        print_info(f"Found {error_count} errors and {warning_count} warnings")
        
        # Display recent errors (up to 5)
        if errors:
            print_header("Recent Errors")
            for error in errors[-5:]:
                print_error(error)
    except Exception as e:
        print_error(f"Error reading log file: {str(e)}")

def check_database():
    """Check database connectivity and health"""
    print_header("Checking Database")
    
    db_file = "no_dynamics.db"
    if os.path.exists(db_file):
        size_mb = os.path.getsize(db_file) / (1024 * 1024)
        print_success(f"Database file exists: {db_file} ({size_mb:.2f} MB)")
        
        # Check if SQLite database is valid
        try:
            import sqlite3
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Get table list
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print_success(f"Database contains {len(tables)} tables")
            
            # Check a few critical tables
            critical_tables = ['user', 'patient', 'simulation', 'chat_session']
            for table in critical_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print_success(f"Table '{table}' exists with {count} records")
                except sqlite3.OperationalError:
                    print_warning(f"Table '{table}' doesn't exist or cannot be accessed")
                    
            conn.close()
        except Exception as e:
            print_error(f"Error checking database: {str(e)}")
    else:
        print_warning(f"Database file not found: {db_file}")
        print_info("Database may be using PostgreSQL instead of SQLite")
        
        # Check PostgreSQL connection
        try:
            from sqlalchemy import create_engine
            from sqlalchemy.exc import SQLAlchemyError
            
            # Get database URL from environment or use default
            database_url = os.environ.get('DATABASE_URL')
            if database_url:
                try:
                    engine = create_engine(database_url)
                    connection = engine.connect()
                    connection.close()
                    print_success("Successfully connected to PostgreSQL database")
                except SQLAlchemyError as e:
                    print_error(f"Failed to connect to PostgreSQL: {str(e)}")
            else:
                print_warning("DATABASE_URL environment variable not set")
        except ImportError:
            print_info("SQLAlchemy not installed, skipping PostgreSQL check")

def main():
    """Main function to run all checks"""
    print_header("N1O1 Clinical Trials Error Check Utility")
    print(f"System time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    check_port_config()
    check_server_status()
    check_logs()
    check_database()
    
    print_header("Error Check Complete")

if __name__ == "__main__":
    main()
