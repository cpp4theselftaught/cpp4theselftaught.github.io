#!/usr/bin/env python3
"""
Convert WordPress export files to Jekyll markdown format.
"""

import os
import re
import html
from datetime import datetime
from pathlib import Path
import html2text

def parse_wp_file(filepath):
    """Parse a WordPress export file and return a dictionary of fields."""
    data = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                # Split on first colon only
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes from string values
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                    # WordPress uses 'n' as escaped newline in the export
                    # We need to convert these to actual newlines
                    value = value.replace('\\n', '\n')  # Handle actual escape sequences first
                    # Now handle the 'n' character which WordPress uses for newlines
                    # This is trickier - we need to be careful not to break words
                    # In WordPress exports, 'n' at specific positions means newline
                    value = re.sub(r'([>)])n', r'\1\n', value)  # After closing tags/parens
                    value = re.sub(r'n([<(])', r'\n\1', value)  # Before opening tags/parens  
                    value = value.replace('nn', '\n\n')  # Double-n is always paragraph break
                data[key] = value
    return data

def convert_html_to_markdown(html_content):
    """Convert HTML content to Markdown."""
    # Initialize html2text converter
    h = html2text.HTML2Text()
    h.body_width = 0  # Don't wrap lines
    h.unicode_snob = True
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    
    # Handle WordPress syntax highlighter plugin output (wp_syntax)
    # Extract code from <div class="wp_syntax"><table>...</table></div>
    def extract_wp_syntax(match):
        content = match.group(0)
        # Extract language from class="xxx" in <pre> tag
        lang_match = re.search(r'<pre class="([^"]+)"', content)
        lang = lang_match.group(1) if lang_match else ''
        # Extract code from the code column (second td)
        code_match = re.search(r'<td class="code"><pre[^>]*>(.*?)</pre></td>', content, re.DOTALL)
        if code_match:
            code = code_match.group(1)
            # Unescape HTML entities
            code = html.unescape(code)
            # Remove span tags but keep content
            code = re.sub(r'<span[^>]*>', '', code)
            code = re.sub(r'</span>', '', code)
            # Remove &nbsp;
            code = code.replace('\xa0', ' ')
            return f'\n```{lang}\n{code}\n```\n'
        return content
    
    html_content = re.sub(r'<div class="wp_syntax">.*?</div>', extract_wp_syntax, html_content, flags=re.DOTALL)
    
    # Handle WordPress code blocks with lang attribute
    # Convert <pre lang="xxx">...</pre> to ```xxx\n...\n```
    def replace_code_block(match):
        lang = match.group(1) if match.group(1) else ''
        code = match.group(2)
        # Unescape the code content
        code = html.unescape(code)
        return f'\n```{lang}\n{code}\n```\n'
    
    html_content = re.sub(r'<pre(?:\s+lang="([^"]*)")?>(.*?)</pre>', replace_code_block, html_content, flags=re.DOTALL)
    
    # Unescape HTML entities
    html_content = html.unescape(html_content)
    
    # Convert to markdown
    markdown = h.handle(html_content)
    
    # Clean up extra whitespace
    markdown = re.sub(r'\n{3,}', '\n\n', markdown)
    
    return markdown.strip()

def generate_slug(title):
    """Generate a URL-friendly slug from a title."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def convert_wp_to_jekyll(wp_file, output_dir):
    """Convert a single WordPress file to Jekyll markdown format."""
    data = parse_wp_file(wp_file)
    
    # Only process published posts (not revisions, attachments, etc.)
    if data.get('post_type') != 'post' or data.get('post_status') != 'publish':
        return None
    
    # Extract metadata
    title = data.get('post_title', 'Untitled')
    post_date = data.get('post_date', '')
    content = data.get('post_content', '')
    post_name = data.get('post_name', generate_slug(title))
    
    # Parse date
    try:
        date_obj = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
        date_str = date_obj.strftime('%Y-%m-%d')
        date_time_str = date_obj.strftime('%Y-%m-%d %H:%M:%S %z')
    except ValueError:
        print(f"Warning: Could not parse date '{post_date}' for post '{title}'")
        return None
    
    # Convert HTML content to Markdown
    markdown_content = convert_html_to_markdown(content)
    
    # Create Jekyll front matter
    front_matter = f"""---
layout: post
title: "{title}"
date: {post_date}
categories: blog
---
"""
    
    # Combine front matter and content
    full_content = front_matter + markdown_content
    
    # Generate filename
    filename = f"{date_str}-{post_name}.md"
    output_path = os.path.join(output_dir, filename)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filename

def main():
    """Main conversion function."""
    script_dir = Path(__file__).parent
    wp_dir = script_dir / '_drafts' / 'will_not_backport'
    output_dir = script_dir / '_posts'
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    # Get all WordPress post files
    wp_files = sorted(wp_dir.glob('wp_post_*.txt'))
    
    converted = 0
    skipped = 0
    
    print(f"Found {len(wp_files)} WordPress files to process...")
    
    for wp_file in wp_files:
        try:
            result = convert_wp_to_jekyll(wp_file, output_dir)
            if result:
                print(f"✓ Converted: {wp_file.name} -> {result}")
                converted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"✗ Error converting {wp_file.name}: {e}")
            skipped += 1
    
    print(f"\nConversion complete!")
    print(f"  Converted: {converted} posts")
    print(f"  Skipped: {skipped} files")

if __name__ == '__main__':
    main()
