import os
import io
import tempfile
import yaml
import pandas as pd

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from datetime import datetime
from PyPDF2 import PdfWriter, PdfReader

from .GraphCalib import GraphCalib

class Execute:
    def __init__(self, base_path, ref_file_path, chip_name, measure_date, process): #channel, #wavelength
        self.base_path = base_path
        self.ref_file_path = ref_file_path
        self.chip_name = chip_name
        self.measure_date = measure_date
        self.process = process

    def get_data(self, calib):
        # Analyze the data using GraphCalib's analyze_data method
        figures_df, loss_df = calib.analyze_data()

        # Get the directory above base_path
        base_dir = os.path.dirname(self.base_path)

        # Define the directory path where results will be saved
        results_directory = os.path.join(base_dir, 'analysis_results')

        # Ensure that the 'analysis_results' directory exists
        os.makedirs(results_directory, exist_ok=True)

        # Save the loss dataframe to a CSV file
        loss_csv_path = os.path.join(results_directory, 'loss_data.csv')
        loss_df.to_csv(loss_csv_path, index=False)
        print(f"Loss data saved to {loss_csv_path}")

        # Save figures to separate files
        for index, row in figures_df.iterrows():
            figure = row['Figure']
            name = row['Name']
            figure_path = os.path.join(results_directory, f"{name}.png")
            with open(figure_path, 'wb') as f:
                f.write(figure.getvalue())

        return figures_df, loss_df

    def pdfReport(self, results_directory, results_df, df_figures):
        if self.chip_name:
            chipname = self.chip_name
        else:
            chipname = input("Enter chip name: ")

        if self.measure_date:
            date = self.measure_date
        else:
            date_str = input("Enter measurement date (YYYY-MM-DD): ")

            try:
                date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%B %d, %Y")
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
                return

        if self.process:
            process = self.process
        else:
            process = input("Enter process: ")

        # Create the full path for the PDF file including the results_directory
        pdf_path = os.path.join(results_directory, f"{chipname}_analysis_report.pdf")

        doc = SimpleDocTemplate(pdf_path, pagesize=letter)

        # Create a story to add elements to the PDF
        story = []

        title = f"Analysis Report of {chipname}"
        title_style = getSampleStyleSheet()["Title"]
        title_style.fontName = 'Times-Bold'
        title_text = Paragraph(title, title_style)
        story.append(title_text)

        paragraph = (f"<br/>Measurement date: {date} <br/><br/>"
                     f"Process: {process}<br/><br/>")
        paragraph_style = getSampleStyleSheet()["Normal"]
        paragraph_style.fontName = 'Times-Roman'
        paragraph_style.fontSize = 12  # Change font size
        paragraph_text = Paragraph(paragraph, paragraph_style)
        story.append(paragraph_text)

        # Format the loss values to 2 decimal places for table
        results_df = results_df.round(2)
        results_df['Bond'] = results_df['Bond'].astype(int)

        table_data = [results_df.columns.tolist()] + results_df.values.tolist()
        col_widths = [1.5 * inch, 1.5 * inch] # table

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.ghostwhite),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),  # Title font size 14
            ('FONTSIZE', (0, 1), (-1, -1), 11),  # Table font size 12
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        story.append(table)
        story.append(PageBreak())

        figures_per_page = 2
        for i, row in df_figures.iterrows():
            figure = row['Figure']

            # Verify the type of figure to ensure it's a BytesIO object
            if isinstance(figure, io.BytesIO):
                # Save the BytesIO object to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(figure.getvalue())
                    tmp_file_path = tmp_file.name

                img = Image(tmp_file_path, width=7.2 * inch, height=4.32 * inch)
                story.append(img)

                if (i + 1) % figures_per_page == 0:
                    story.append(PageBreak())
            else:
                print(f"Unexpected type for figure: {type(figure)}")

        doc.build(story)

        return pdf_path

    def genReport(self):
        yaml_file = os.path.join(self.base_path, 'config.yaml')
        with open(yaml_file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        # Extract the wavelength and channel from the YAML file
        device = data['devices'][0]
        wavelength = device['wavelength']
        channel = device['channel']

        calib = GraphCalib(self.base_path, self.ref_file_path, channel, wavelength)
        figures_df, loss_df = self.get_data(calib)

        # Get the directory above base_path
        base_dir = os.path.dirname(self.base_path)

        # Define the results directory path
        results_directory = os.path.join(base_dir, 'analysis_results')

        # Check if the results directory exists, create it if it doesn't
        if not os.path.exists(results_directory):
            os.makedirs(results_directory)

        # Generate the PDF report
        pdf_path = self.pdfReport(results_directory, loss_df, figures_df)
        print(f"PDF report generated at {pdf_path}")
