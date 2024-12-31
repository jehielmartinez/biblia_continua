import os
from ebooklib import epub
import re

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

def create_bible_epub():
    book = epub.EpubBook()
    
    # Set metadata
    book.set_identifier('biblia')
    book.set_title('Biblia Continua - Reina Valera 1960')
    book.set_language('es')
    book.add_author('God')
    
    chapters = []
    spine = ['nav']
    
    # Process each file in the origin directory
    origin_dir = 'origin'
    # Sort files using the custom sorting function
    sorted_files = sorted(os.listdir(origin_dir), key=sort_by_book_number)
    
    for filename in sorted_files:
        if filename.endswith('.txt'):
            file_path = os.path.join(origin_dir, filename)
            book_title = clean_filename(filename)
            
            # Extract text content
            content = extract_text_from_file(file_path)
            
            # Create chapter with proper HTML line breaks
            chapter = epub.EpubHtml(
                title=book_title,
                file_name=f'{book_title.lower().replace(" ", "_")}.xhtml'
            )
            content = content.replace('/n', '<br/>')
            chapter.content = f'<h1>{book_title}</h1><p>{content}</p>'
            
            # Add chapter
            book.add_item(chapter)
            chapters.append(chapter)
            spine.append(chapter)
    
    # Create table of contents
    book.toc = [(epub.Section('Libros'), chapters)]
    
    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # Set spine
    book.spine = spine
    
    # Write epub file
    epub.write_epub('biblia.epub', book)

if __name__ == '__main__':
    create_bible_epub()
