import os
import re
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def clean_filename(filename):
    # Remove extension and replace underscores/hyphens with spaces
    # Remove extension first
    name = os.path.splitext(filename)[0]
    # Remove numbers and dash from start (e.g., "41-")
    name = re.sub(r'^\d+-', '', name)
    # Replace underscore with space
    name = name.replace('_', ' ')
    # Capitalize the first letter
    return name.title()

def extract_salmos_text(file_path):
    text_content = []
    current_chapter = 0
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # Extract components using regex
            match = re.match(r'\((\d+),\s*(\d+),\s*\d+,\s*\'([^\']+)\'\)', line)
            if match:
                chapter = int(match.group(2))
                text = match.group(3)
                
                # Add chapter number when it changes
                if chapter != current_chapter:
                    current_chapter = chapter
                    text_content.append(f"/n{chapter}")
                
                # Clean and add the verse text
                text = text.replace('\\n', '\n')
                text_content.append(text)
    
    return ' '.join(text_content)

def extract_text_from_file(file_path):
    # Check if the file is Salmos
    if '19-salmos.txt' in file_path.lower():
        return extract_salmos_text(file_path)
        
    text_content = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Remove line breaks
            line = line.strip()
            
            # Remove verse numbers
            line = re.sub(r'^\d+\s', '', line)
            # Extract text between single quotes
            line = re.findall(r"'([^']*)'", line)
            line = line[0] if line else ''
            
            # Convert literal \n to actual line breaks
            line = line.replace('\\n', '\n')
            
            # Append line to text content
            text_content.append(line)
    return ' '.join(text_content)

def sort_by_book_number(filename):
    # Extract the number before the dash
    match = re.match(r'(\d+)-', filename)
    if match:
        return int(match.group(1))
    return 0

def create_bible_pdf():
    # Create PDF document
    doc = SimpleDocTemplate(
        "biblia.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Register Book Antigua font
    pdfmetrics.registerFont(TTFont('BookAntiqua', 'BookAntiqua.ttf'))
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'BookTitle',
        parent=styles['Heading1'],
        fontName='BookAntiqua',
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    text_style = ParagraphStyle(
        'VerseText',
        parent=styles['Normal'],
        fontName='BookAntiqua',
        fontSize=12,
        leading=16,
        spaceBefore=6
    )
    
    # Create Table of Contents style
    # toc_style = ParagraphStyle(
    #     'TOCEntry',
    #     parent=styles['Normal'],
    #     fontSize=14,
    #     leading=20
    # )
    
    # Store all elements
    elements = []
    toc_entries = []
    
    # Process each file in the origin directory
    origin_dir = 'origin'
    sorted_files = sorted(os.listdir(origin_dir), key=sort_by_book_number)
    
    for filename in sorted_files:
        if filename.endswith('.txt'):
            file_path = os.path.join(origin_dir, filename)
            book_title = clean_filename(filename)
            
            # Track TOC entry
            toc_entries.append((book_title, len(elements)))
            
            # Add book title
            elements.append(Paragraph(book_title, title_style))
            elements.append(Spacer(1, 12))
            
            # Extract and process content
            content = extract_text_from_file(file_path)
            
            # Split content by chapter markers
            chapters = content.split('/n')
            for chapter in chapters:
                if chapter.strip():
                    match = re.match(r'(\d+)(.*)', chapter.strip())
                    if match:
                        chapter_num, chapter_text = match.groups()
                        elements.append(Paragraph(f"{chapter_num}", styles['Heading2']))
                        if chapter_text:
                            elements.append(Paragraph(chapter_text.strip(), text_style))
                    else:
                        elements.append(Paragraph(chapter.strip(), text_style))
            
            elements.append(Spacer(1, 20))
            # Add page break after each book
            elements.append(PageBreak())
    
    # # Add Table of Contents at the beginning
    # toc_elements = [Paragraph('Tabla de Contenido', title_style)]
    # for title, page_num in toc_entries:
    #     toc_elements.append(Paragraph(f"{title} - Página {page_num + 1}", toc_style))
    # toc_elements.append(PageBreak())
    
    # # Combine TOC and main content
    # elements = toc_elements + elements
    
    # Build PDF
    doc.build(elements)

if __name__ == '__main__':
    create_bible_pdf()
