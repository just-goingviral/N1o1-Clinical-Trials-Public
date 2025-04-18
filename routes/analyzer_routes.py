
from flask import Blueprint, render_template, request, send_file
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import base64
import json
from statistical_analysis import StatisticalAnalyzer

analyzer_bp = Blueprint("analyzer_bp", __name__)

def generate_plot(dataframe):
    fig, ax = plt.subplots(figsize=(10, 5))
    time_col = 'Time (minutes)' if 'Time (minutes)' in dataframe.columns else 'Time (hours)'
    x = dataframe[time_col]
    
    if 'Plasma NO2- (µM)' in dataframe.columns:
        ax.plot(x, dataframe['Plasma NO2- (µM)'], label='NO₂⁻', color='purple')
    if 'cGMP (a.u.)' in dataframe.columns:
        ax.plot(x, dataframe['cGMP (a.u.)'], label='cGMP', color='green', linestyle='--')
    if 'Vasodilation (%)' in dataframe.columns:
        ax.plot(x, dataframe['Vasodilation (%)'], label='Vasodilation', color='blue', linestyle=':')
    
    ax.set_xlabel(time_col)
    ax.set_ylabel('Response')
    ax.set_title('Nitric Oxide Simulation Results')
    ax.grid(True)
    ax.legend()
    
    # Convert plot to base64
    buffer = BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close(fig)
    return f"data:image/png;base64,{img_str}"

@analyzer_bp.route('/upload_csv', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            analyzer = StatisticalAnalyzer()
            analyzer.load_data(dataframe=df)
            summary = analyzer.create_summary_report()
            plot_url = generate_plot(df)
            return render_template('analysis.html', summary=summary, plot_url=plot_url)
    return render_template('upload.html')

@analyzer_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from fpdf import FPDF
    summary_data = json.loads(request.form['summary'])
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Nitrite Dynamics Report", ln=True, align='C')

    for key, value in summary_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')
"""
Analyzer routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request, render_template, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import io
import json
from fpdf import FPDF
from statistical_analysis import StatisticalAnalyzer
from io import BytesIO

analyzer_bp = Blueprint('analyzer', __name__, url_prefix='/analyzer')

def generate_plot(df):
    """Generate a plot from the CSV data"""
    plt.figure(figsize=(10, 6))
    
    # Detect time column
    time_col = None
    for col in df.columns:
        if 'time' in col.lower() or 'min' in col.lower():
            time_col = col
            break
    
    if time_col is None:
        time_col = df.columns[0]  # Use first column as default
    
    # Plot all numeric columns except the time column
    for col in df.columns:
        if col != time_col and pd.api.types.is_numeric_dtype(df[col]):
            plt.plot(df[time_col], df[col], label=col)
    
    plt.xlabel(time_col)
    plt.ylabel('Value')
    plt.title('Nitric Oxide Dynamics')
    plt.legend()
    plt.grid(True)
    
    # Convert plot to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    
    return f"data:image/png;base64,{plot_data}"

@analyzer_bp.route('/', methods=['GET', 'POST'])
def upload_csv():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.csv'):
            df = pd.read_csv(file)
            analyzer = StatisticalAnalyzer()
            analyzer.load_data(dataframe=df)
            summary = analyzer.create_summary_report()
            plot_url = generate_plot(df)
            return render_template('analysis.html', summary=summary, plot_url=plot_url)
    return render_template('upload.html')

@analyzer_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from fpdf import FPDF
    summary_data = json.loads(request.form['summary'])
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Nitrite Dynamics Report", ln=True, align='C')

    for key, value in summary_data.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')
