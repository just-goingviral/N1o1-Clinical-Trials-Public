
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
