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
        tocStyle = ParagraphStyle(
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
        dotPattern = " . " * 40
        self.toc.dotsMinLevel = 0
        self.toc.levelStyles = [tocStyle]
        self.toc.format = {
            0: f"%s{dotPattern}%s",
        }

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == "Title":
                key = "h1-%s" % self.seq.nextf("heading1")
                self.canv.bookmarkPage(key)
                self.notify("TOCEntry", (0, text, self.page, key))


def createStudentReport(pdf, row):
    styles = getSampleStyleSheet()

    # Title: Student Name and Record ID
    title = f"{row['Student Name']} - Record ID: {row['Record ID']}"
    pdf.append(Paragraph(title, styles["Title"]))
    pdf.append(Spacer(1, 12))

    # Cover Letter
    coverLetterTitle = "<b>Cover Letter</b>"
    justifiedStyle = ParagraphStyle(
        "Justified",
        parent=styles["BodyText"],
        alignment=4,  # 4 is for full justification
    )
    coverLetterText = Paragraph(row["Cover Letter Raw Text"], justifiedStyle)
    pdf.append(Paragraph(coverLetterTitle, styles["Heading2"]))
    pdf.append(coverLetterText)
    pdf.append(Spacer(1, 12))

    # STARS Track Choice
    trackTitle = "<b>STARS Track Recommendation</b>"
    pdf.append(Paragraph(trackTitle, styles["Heading2"]))
    pdf.append(Paragraph(f"<b>Track:</b> {row['Stars Track Choice']}", styles["BodyText"]))
    pdf.append(Paragraph(f"<b>Rationale:</b> {row['Stars Track Rationale']}", styles["BodyText"]))
    pdf.append(Spacer(1, 12))

    # Evaluation Table
    tableData = [
        [
            Paragraph(
                f"<b>Metric & Score<br/>Total: {row['Total Score']}</b>",
                styles["BodyText"],
            ),
            Paragraph("<b>Rationale</b>", styles["BodyText"]),
        ],
    ]

    metrics = [
        ("Motivation", "Motivation", "Motivation Rationale"),
        ("Initiative", "Initiative", "Initiative Rationale"),
        ("Program Expectations", "Program Expectations", "Program Expectations Rationale"),
        ("Future Alignment", "Future Alignment", "Future Alignment Rationale"),
    ]

    for metricName, scoreCol, rationaleCol in metrics:
        metricScore = f"{metricName}<br />{int(row[scoreCol])}/3"
        metricScoreText = Paragraph(metricScore, styles["BodyText"])
        rationaleText = Paragraph(str(row[rationaleCol]), styles["BodyText"])
        tableData.append([metricScoreText, rationaleText])

    # Get total width available
    totalWidth = 510

    # Calculate column widths (20% and 80% of total width)
    col1Width = totalWidth * 0.20
    col2Width = totalWidth * 0.80

    table = Table(tableData, colWidths=[col1Width, col2Width])
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


def generatePdfReport(inputFile="euroOutputs/STARS25-Evaluation-Details.xlsx",
                     outputDir="euroOutputs/pdf_reports",
                     outputFileName="STARS25-EvaluationReport.pdf",
                     authorName="VARUN AGGARAWAL",
                     reportTitle="STARS 2025",
                     reportSubtitle="Student Evaluation<br />Report"):
    # Read the evaluation details using row 2 as header
    df = pd.read_excel(inputFile, header=1)

    # Create output directory if it doesn't exist
    os.makedirs(outputDir, exist_ok=True)

    # Initialize PDF with custom document template
    outputFile = os.path.join(outputDir, outputFileName)
    doc = MyDocTemplate(outputFile, pagesize=letter)
    pdfContent = []

    # Add title page
    styles = getSampleStyleSheet()
    titleStyle = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=36,
        spaceAfter=30,
        alignment=1,
        leading=50,
    )

    # Create centered title with larger spacing
    pdfContent.append(Spacer(1, 100))
    pdfContent.append(Paragraph(reportTitle, titleStyle))
    pdfContent.append(Spacer(1, 20))
    pdfContent.append(Paragraph(reportSubtitle, titleStyle))
    pdfContent.append(Spacer(1, 100))

    # Add date at the bottom of the title page
    dateStyle = ParagraphStyle(
        "DateStyle", parent=styles["Normal"], fontSize=14, alignment=1, spaceAfter=30
    )
    currentDate = datetime.now().strftime("%B %d, %Y")
    pdfContent.append(Paragraph(f"{currentDate} | {authorName}", dateStyle))
    pdfContent.append(PageBreak())

    # Add table of contents with better formatting
    tocTitle = ParagraphStyle(
        "TOCTitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=20,
        spaceBefore=10,
        alignment=1,
    )
    pdfContent.append(Paragraph("TABLE OF CONTENTS", tocTitle))
    pdfContent.append(Spacer(1, 10))
    pdfContent.append(doc.toc)
    pdfContent.append(PageBreak())

    # Process each student
    evaluatedStudents = df.sort_values(by=["Total Score"], ascending=False)
    for _, row in evaluatedStudents.iterrows():
        createStudentReport(pdfContent, row)

    # Save the PDF
    doc.multiBuild(pdfContent)
    print(f"PDF report generated: {outputFile}")
    print(f"Total students processed: {len(evaluatedStudents)}")


if __name__ == "__main__":
    # User variables
    inputFile = "euroOutputs/STARS25-Evaluation-Details (1).xlsx"
    outputDir = "euroOutputs/pdf_reports"
    outputFileName = "STARS25-EvaluationReport.pdf"
    authorName = "VARUN AGGARAWAL"
    reportTitle = "STARS 2025"
    reportSubtitle = "Student Evaluation<br />Report"

    # Generate the report
    generatePdfReport(
        inputFile=inputFile,
        outputDir=outputDir,
        outputFileName=outputFileName,
        authorName=authorName,
        reportTitle=reportTitle,
        reportSubtitle=reportSubtitle
    )
