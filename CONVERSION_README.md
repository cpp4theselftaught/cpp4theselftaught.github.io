# WordPress to Markdown Conversion

This repository contains 53 blog posts that were converted from WordPress export files to Jekyll-compatible Markdown format.

## Conversion Process

The WordPress export files were located in `_drafts/will_not_backport/` as text files with the naming pattern `wp_post_*.txt`.

The conversion was performed using the `convert_wordpress_to_markdown.py` script, which:

1. Parsed WordPress export format (key-value pairs with quoted strings)
2. Extracted metadata (title, date, post_status, post_type, etc.)
3. Filtered for published posts only (`post_status: "publish"` and `post_type: "post"`)
4. Converted HTML content to Markdown using the html2text library
5. Generated Jekyll front matter with appropriate metadata
6. Created properly named markdown files in the format `YYYY-MM-DD-slug.md`

## Converted Posts

- **Total WordPress files**: 278
- **Published posts converted**: 53
- **Date range**: 2011-05-19 to 2017-09-29

## Known Limitations

The WordPress export format used some non-standard character encoding and HTML entity escaping that may result in minor formatting issues in some posts, particularly:

- Code blocks may have some character encoding issues
- Some special characters may not be perfectly converted
- Complex HTML structures may have been simplified during conversion

These posts serve as a historical record and can be manually corrected as needed.

## Usage

To re-run the conversion (if needed):

```bash
python3 convert_wordpress_to_markdown.py
```

Note: This will require the `html2text` Python package to be installed:

```bash
pip3 install html2text
```
