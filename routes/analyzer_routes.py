
"""
Analyzer routes for Nitrite Dynamics application
"""
from flask import Blueprint, jsonify, request, render_template, send_file, current_app
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
    """Upload CSV and analyze data"""
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return render_template('upload.html', error="No file selected")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('upload.html', error="No file selected")
        
        # Check file extension
        if not file.filename.endswith('.csv'):
            return render_template('upload.html', error="File must be CSV format")
        
        try:
            # Read CSV
            df = pd.read_csv(file)
            
            # Generate plot
            plot_url = generate_plot(df)
            
            # Calculate summary statistics
            analyzer = StatisticalAnalyzer()
            summary = analyzer.analyze_time_series(df)
            
            return render_template('analysis.html', summary=summary, plot_url=plot_url)
            
        except Exception as e:
            current_app.logger.error(f"Error processing CSV: {str(e)}")
            return render_template('upload.html', error=f"Error processing CSV: {str(e)}")
    
    # GET request - show upload form
    return render_template('upload.html')

@analyzer_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    """Generate and download PDF report"""
    try:
        # Get data from request
        summary = json.loads(request.form.get('summary', '{}'))
        plot_url = request.form.get('plot_url', '')
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Nitric Oxide Analysis Report', 0, 1, 'C')
        pdf.ln(5)
        
        # Add plot
        if plot_url and plot_url.startswith('data:image/png;base64,'):
            plot_data = base64.b64decode(plot_url.split(',')[1])
            plot_file = BytesIO(plot_data)
            pdf.image(plot_file, x=10, y=pdf.get_y(), w=180)
            pdf.ln(120)  # Space after image
        
        # Add summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Summary Statistics', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        if summary:
            for key, value in summary.items():
                pdf.cell(60, 8, key, 1)
                pdf.cell(130, 8, str(value), 1)
                pdf.ln()
        
        # Output PDF
        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        
        # Return PDF file
        return send_file(
            pdf_output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='nitric_oxide_report.pdf'
        )
        
    except Exception as e:
        current_app.logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
