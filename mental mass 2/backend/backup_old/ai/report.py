from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io
from datetime import datetime

def generate_report(user_data=None, sessions_data=None):
    try:
        # Create a buffer for the PDF
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph("MENTALMASS - Mental Health Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.25*inch))

        # Date
        current_date = datetime.now().strftime("%B %d, %Y")
        date_para = Paragraph(f"Report Generated: {current_date}", styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 0.25*inch))

        # User Information
        if user_data:
            user_title = Paragraph("User Information", styles['Heading2'])
            story.append(user_title)
            story.append(Spacer(1, 0.1*inch))

            user_info = f"Name: {user_data.get('name', 'N/A')}<br/>Email: {user_data.get('email', 'N/A')}"
            user_para = Paragraph(user_info, styles['Normal'])
            story.append(user_para)
            story.append(Spacer(1, 0.25*inch))

        # Mood Summary
        mood_title = Paragraph("Mood Summary", styles['Heading2'])
        story.append(mood_title)
        story.append(Spacer(1, 0.1*inch))

        if sessions_data:
            total_sessions = len(sessions_data)
            avg_score = sum(session.get('score', 0) for session in sessions_data) / total_sessions if total_sessions > 0 else 0

            mood_info = f"Total Sessions: {total_sessions}<br/>Average Mood Score: {avg_score:.1f}/100"
            mood_para = Paragraph(mood_info, styles['Normal'])
            story.append(mood_para)
        else:
            mood_para = Paragraph("No session data available", styles['Normal'])
            story.append(mood_para)

        story.append(Spacer(1, 0.25*inch))

        # Risk Assessment
        risk_title = Paragraph("Risk Assessment", styles['Heading2'])
        story.append(risk_title)
        story.append(Spacer(1, 0.1*inch))

        if sessions_data and sessions_data:
            latest_score = sessions_data[-1].get('score', 50)
            if latest_score < 35:
                risk_level = "High Stress Level"
                risk_message = "You may be experiencing high stress. Consider taking immediate steps to relax."
            elif latest_score <= 60:
                risk_level = "Moderate Stress Level"
                risk_message = "You may be experiencing moderate stress. Try some relaxation techniques."
            else:
                risk_level = "Low Stress Level"
                risk_message = "You are doing well! Keep maintaining your mental wellness."

            risk_info = f"Current Risk Level: {risk_level}<br/>{risk_message}"
            risk_para = Paragraph(risk_info, styles['Normal'])
            story.append(risk_para)
        else:
            risk_para = Paragraph("Unable to assess risk without session data", styles['Normal'])
            story.append(risk_para)

        story.append(Spacer(1, 0.25*inch))

        # Recommendations
        rec_title = Paragraph("Recommendations", styles['Heading2'])
        story.append(rec_title)
        story.append(Spacer(1, 0.1*inch))

        recommendations = [
            "Continue monitoring your mental wellness regularly",
            "Practice stress-reduction techniques daily",
            "Maintain a healthy sleep schedule",
            "Stay connected with supportive friends and family",
            "Consider professional help if needed"
        ]

        for rec in recommendations:
            rec_para = Paragraph(f"• {rec}", styles['Normal'])
            story.append(rec_para)
            story.append(Spacer(1, 0.05*inch))

        # Build the PDF
        doc.build(story)

        # Get the PDF data
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        buffer.close()

        return pdf_data

    except Exception as e:
        raise ValueError(f"PDF generation failed: {str(e)}")