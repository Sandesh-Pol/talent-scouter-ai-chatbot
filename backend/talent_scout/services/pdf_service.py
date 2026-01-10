"""
PDF Report Generation Service

Generates professional screening reports with:
- Candidate profile information
- Skill matrix with 5-star ratings
- Assessment summary
- Company logo and branding
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from io import BytesIO

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """
    Service for generating PDF screening reports.
    
    Features:
    - Professional layout with company branding
    - Candidate bio section
    - Skill matrix with star ratings
    - Assessment summary
    - Export as downloadable PDF
    """
    
    # Color scheme (matching glassmorphism theme)
    PRIMARY_COLOR = colors.HexColor("#1AA260")  # Teal/Cyan
    SECONDARY_COLOR = colors.HexColor("#1C232B")  # Dark background
    TEXT_COLOR = colors.HexColor("#E5E7EB")  # Light text
    ACCENT_COLOR = colors.HexColor("#38BDF8")  # Light blue
    TABLE_HEADER = colors.HexColor("#2D3748")  # Dark gray
    TABLE_ROW_ALT = colors.HexColor("#1F2937")  # Alternate row color
    
    def __init__(self):
        """Initialize the PDF generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Caption style
        self.styles.add(ParagraphStyle(
            name='CustomCaption',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            alignment=TA_CENTER,
            fontName='Helvetica-Oblique'
        ))
    
    def generate_report(
        self,
        candidate_data: Dict[str, Any],
        skill_ratings: Dict[str, Any],
        assessment_summary: str,
        logo_path: Optional[str] = None
    ) -> BytesIO:
        """
        Generate a complete PDF screening report.
        
        Args:
            candidate_data: Dictionary with candidate information
            skill_ratings: Dictionary mapping skills to rating data
            assessment_summary: LLM-generated summary text
            logo_path: Optional path to company logo image
        
        Returns:
            BytesIO buffer containing the PDF
        
        Candidate Data Format:
        {
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "location": "San Francisco, CA",
            "experience_level": "Senior",
            "position_applied": "Full Stack Developer",
            "years_experience": 5
        }
        
        Skill Ratings Format:
        {
            "Python": {
                "stars": 4.5,
                "percentage": 85.0,
                "grade": "A",
                "assessment": "Excellent understanding"
            },
            ...
        }
        """
        # Create PDF buffer
        buffer = BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=inch,
            bottomMargin=0.75*inch
        )
        
        # Container for document elements
        story = []
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            try:
                logo = Image(logo_path, width=2*inch, height=0.8*inch)
                logo.hAlign = 'CENTER'
                story.append(logo)
                story.append(Spacer(1, 0.25*inch))
            except Exception as e:
                logger.warning(f"Failed to add logo: {e}")
        
        # Title Section
        title = Paragraph(
            "<b>Technical Screening Report</b>",
            self.styles['CustomTitle']
        )
        story.append(title)
        
        # Report metadata
        report_date = datetime.now().strftime("%B %d, %Y")
        metadata_text = f"<i>Generated on: {report_date}</i>"
        metadata = Paragraph(metadata_text, self.styles['CustomCaption'])
        story.append(metadata)
        story.append(Spacer(1, 0.3*inch))
        
        # Candidate Bio Section
        story.append(self._create_bio_section(candidate_data))
        story.append(Spacer(1, 0.3*inch))
        
        # Skill Matrix Section
        story.append(self._create_skill_matrix(skill_ratings))
        story.append(Spacer(1, 0.3*inch))
        
        # Assessment Summary Section
        story.append(self._create_summary_section(assessment_summary))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        footer_text = (
            "<i>This report was generated by TalentScout AI. "
            "All information is confidential and should be treated as such.</i>"
        )
        footer = Paragraph(footer_text, self.styles['CustomCaption'])
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        # Reset buffer position
        buffer.seek(0)
        
        logger.info(f"Generated PDF report for {candidate_data.get('full_name', 'Unknown')}")
        return buffer
    
    def _create_bio_section(self, candidate_data: Dict[str, Any]) -> KeepTogether:
        """Create the candidate bio section"""
        elements = []
        
        # Section heading
        heading = Paragraph(
            "<b>Candidate Profile</b>",
            self.styles['CustomHeading']
        )
        elements.append(heading)
        elements.append(Spacer(1, 0.15*inch))
        
        # Bio table
        bio_data = [
            ["Full Name:", candidate_data.get("full_name", "N/A")],
            ["Email:", candidate_data.get("email", "N/A")],
            ["Phone:", candidate_data.get("phone", "N/A")],
            ["Location:", candidate_data.get("location", "N/A")],
            ["Position Applied:", candidate_data.get("position_applied", "N/A")],
            ["Experience Level:", candidate_data.get("experience_level", "N/A")],
            ["Years of Experience:", str(candidate_data.get("years_experience", "N/A"))],
        ]
        
        bio_table = Table(bio_data, colWidths=[2*inch, 4*inch])
        bio_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(bio_table)
        
        return KeepTogether(elements)
    
    def _create_skill_matrix(self, skill_ratings: Dict[str, Any]) -> KeepTogether:
        """Create the skill matrix with star ratings"""
        elements = []
        
        # Section heading
        heading = Paragraph(
            "<b>Technical Skills Assessment</b>",
            self.styles['CustomHeading']
        )
        elements.append(heading)
        elements.append(Spacer(1, 0.15*inch))
        
        # Table header
        table_data = [
            ["Skill", "Rating", "Score", "Grade", "Assessment"]
        ]
        
        # Add skill rows
        for skill, rating_data in skill_ratings.items():
            stars = rating_data.get("stars", 0)
            stars_display = self._stars_to_text(stars)
            percentage = f"{rating_data.get('percentage', 0):.0f}%"
            grade = rating_data.get("grade", "N/A")
            assessment = rating_data.get("assessment", "N/A")
            
            table_data.append([
                skill,
                stars_display,
                percentage,
                grade,
                assessment
            ])
        
        # Create table
        skills_table = Table(
            table_data,
            colWidths=[1.8*inch, 1.2*inch, 0.8*inch, 0.6*inch, 2.2*inch]
        )
        
        # Style table
        table_style = [
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (3, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Alternate row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(
                    ('BACKGROUND', (0, i), (-1, i), colors.Color(0.95, 0.95, 0.95))
                )
        
        skills_table.setStyle(TableStyle(table_style))
        elements.append(skills_table)
        
        return KeepTogether(elements)
    
    def _create_summary_section(self, summary: str) -> KeepTogether:
        """Create the assessment summary section"""
        elements = []
        
        # Section heading
        heading = Paragraph(
            "<b>Overall Assessment</b>",
            self.styles['CustomHeading']
        )
        elements.append(heading)
        elements.append(Spacer(1, 0.15*inch))
        
        # Summary text
        summary_para = Paragraph(summary, self.styles['CustomBody'])
        elements.append(summary_para)
        
        return KeepTogether(elements)
    
    def _stars_to_text(self, stars: float) -> str:
        """Convert star rating to text representation"""
        full_stars = int(stars)
        half_star = 1 if (stars - full_stars) >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        star_text = "★" * full_stars
        if half_star:
            star_text += "⯨"
        star_text += "☆" * empty_stars
        
        return f"{star_text} ({stars:.1f}/5)"


# Singleton instance
_pdf_generator_instance = None


def get_pdf_generator() -> PDFReportGenerator:
    """
    Get singleton instance of PDFReportGenerator.
    """
    global _pdf_generator_instance
    
    if _pdf_generator_instance is None:
        _pdf_generator_instance = PDFReportGenerator()
    
    return _pdf_generator_instance
