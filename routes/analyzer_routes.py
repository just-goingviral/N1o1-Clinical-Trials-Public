"""
Analyzer routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request, render_template, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import io
from io import BytesIO
import json
from fpdf import FPDF
from statistical_analysis import StatisticalAnalyzer

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
    """Upload and analyze CSV data"""
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('upload.html', error="No file part")

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return render_template('upload.html', error="No selected file")

        # Process the CSV file
        if file and file.filename.endswith('.csv'):
            try:
                # Read CSV file
                df = pd.read_csv(file)

                # Check for required columns
                time_col = None
                value_col = None

                # Try to identify time and value columns
                for col in df.columns:
                    col_lower = col.lower()
                    if 'time' in col_lower or 'min' in col_lower or 'hour' in col_lower:
                        time_col = col
                    elif 'no' in col_lower or 'nitric' in col_lower or 'nitrite' in col_lower or 'value' in col_lower or 'level' in col_lower:
                        value_col = col

                # If columns weren't identified, use the first two columns
                if time_col is None or value_col is None:
                    time_col = df.columns[0]
                    value_col = df.columns[1]

                # Analyze the data
                analyzer = StatisticalAnalyzer()

                # Prepare data for analysis
                time_values = df[time_col].values
                no_values = df[value_col].values

                # Calculate summary statistics
                summary = analyzer.calculate_summary_statistics(time_values, no_values)

                # Generate plot
                plot_url = analyzer.plot_data(time_values, no_values, time_col, value_col, return_base64=True)

                # Render the analysis template with results
                return render_template('analysis.html', summary=summary, plot_url=plot_url)

            except Exception as e:
                return render_template('upload.html', error=f"Error processing file: {str(e)}")
        else:
            return render_template('upload.html', error="Invalid file format. Please upload a CSV file.")

    # For GET requests, just show the upload form
    return render_template('upload.html')

@analyzer_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
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