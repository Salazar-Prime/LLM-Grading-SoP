from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.units import inch
import pandas as pd
import os
from datetime import datetime


class MyDocTemplate(SimpleDocTemplate):
    def __init__(self, filename, **kw):
        SimpleDocTemplate.__init__(self, filename, **kw)
        self.toc = TableOfContents()

        # Create more compact TOC style with dot leaders
        toc_style = ParagraphStyle(
            fontName="Helvetica",
            fontSize=10,
            name="TOCHeading0",
            leftIndent=20,
            firstLineIndent=-20,
            spaceBefore=1,
            spaceAfter=1,
            leading=16,
        )

        # Add dot leader pattern
        dot_pattern = " . " * 40  # Create a pattern of dots
        self.toc.dotsMinLevel = 0  # Enable dots from first level
        self.toc.levelStyles = [toc_style]
        # Override the default format to include dot leaders
        self.toc.format = {
            0: f"%s{dot_pattern}%s",
        }

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "Title":
                key = "h1-%s" % self.seq.nextf("heading1")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (0, text, self.page, key))


def create_student_report(pdf, row):
    styles = getSampleStyleSheet()

    # Title: Student Name and GUID
    title = f"{row['first_name']} {row['last_name']} - {row['guid']}"
    pdf.append(Paragraph(title, styles["Title"]))
    pdf.append(Spacer(1, 12))

    # Statement of Purpose
    sop_title = f"<b>Statement of Purpose | ({row['word_count']} words | {row['total_score']} out of 18)</b>"
    # Create justified body text style
    justified_style = ParagraphStyle(
        "Justified",
        parent=styles["BodyText"],
        alignment=4,  # 4 is for full justification
    )
    sop_text = Paragraph(row["cleaned_sop"], justified_style)
    pdf.append(Paragraph(sop_title, styles["Heading2"]))
    pdf.append(sop_text)
    pdf.append(Spacer(1, 12))

    # Evaluation Table
    table_data = [
        [
            Paragraph(
                f"<b>Metric & Score<br/>Total: {row['total_score']}</b>",
                styles["BodyText"],
            ),
            Paragraph("<b>Rationale</b>", styles["BodyText"]),
        ],  # Table Headers
    ]
    metrics = [
        (
            "Motivation for Scientific Research",
            "score_motivation",
            "rationale_motivation",
        ),
        ("Initiative", "score_initiative", "rationale_initiative"),
        (
            "Program Expectations",
            "score_program_expectations",
            "rationale_program_expectations",
        ),
        ("Future Alignment", "score_future_alignment", "rationale_future_alignment"),
        (
            "Learning Reflection",
            "score_learning_reflection",
            "rationale_learning_reflection",
        ),
        ("Problem Solving", "score_problem_solving", "rationale_problem_solving"),
    ]

    for metric_name, score_col, rationale_col in metrics:
        # Combine metric name and score, ensure score is integer
        metric_score = f"{metric_name}<br />{int(row[score_col])}/3"
        # Wrap both columns in Paragraph
        metric_score_text = Paragraph(metric_score, styles["BodyText"])
        rationale_text = Paragraph(str(row[rationale_col]), styles["BodyText"])
        table_data.append([metric_score_text, rationale_text])

    # Get total width available (letter page width minus margins)
    total_width = 510  # Approximate width in points for letter size with margins

    # Calculate column widths (20% and 80% of total width)
    col1_width = total_width * 0.20  # 20% for metric and score
    col2_width = total_width * 0.80  # 80% for rationale

    table = Table(table_data, colWidths=[col1_width, col2_width])  # 20-80 split
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ]
        )
    )
    pdf.append(table)
    pdf.append(Spacer(1, 12))
    
    # Add page break after each student
    pdf.append(PageBreak())


def generate_pdf_report():
    # Read the merged results
    df = pd.read_excel("outputs/High Priority Pool - Graded.xlsx")

    # Create output directory if it doesn't exist
    os.makedirs("outputs/pdf_reports", exist_ok=True)

    # Initialize PDF with custom document template
    output_file = "outputs/pdf_reports/SURF25-GradedSoP-HighPriorityPool.pdf"
    doc = MyDocTemplate(output_file, pagesize=letter)
    pdf_content = []

    # Add title page
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=36,
        spaceAfter=30,
        alignment=1,
        leading=50,  # Increased line spacing
    )

    # Create centered title with larger spacing
    pdf_content.append(Spacer(1, 100))  # Add space at the top
    pdf_content.append(Paragraph("SURF 2025", title_style))
    pdf_content.append(Spacer(1, 20))
    pdf_content.append(Paragraph("High Potential Student<br />Graded SoP", title_style))
    pdf_content.append(Spacer(1, 100))

    # Add date at the bottom of the title page
    date_style = ParagraphStyle(
        "DateStyle", parent=styles["Normal"], fontSize=14, alignment=1, spaceAfter=30
    )
    current_date = datetime.now().strftime("%B %d, %Y")
    pdf_content.append(Paragraph(current_date, date_style))
    pdf_content.append(PageBreak())

    # Add table of contents with better formatting
    toc_title = ParagraphStyle(
        "TOCTitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=20,
        spaceBefore=10,
        alignment=1,  # Center alignment
    )
    pdf_content.append(Paragraph("TABLE OF CONTENTS", toc_title))
    pdf_content.append(Spacer(1, 10))
    pdf_content.append(doc.toc)
    pdf_content.append(PageBreak())

    # Process each student
    evaluated_students = df[pd.notna(df["model"])].sort_values(by=["guid"])
    for _, row in evaluated_students.iterrows():
        create_student_report(pdf_content, row)

    # Save the PDF
    doc.multiBuild(pdf_content)
    print(f"PDF report generated: {output_file}")
    print(f"Total students processed: {len(evaluated_students)}")


if __name__ == "__main__":
    generate_pdf_report()
