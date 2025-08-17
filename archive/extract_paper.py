#!/usr/bin/env python3
"""
Multi-Journal Paper Extractor - Command Line Interface
Supports Nature, APS, and other academic journals

Usage:
    python extract_paper.py "URL_or_Title_or_DOI"
    python extract_paper.py "input" --journal nature
    python extract_paper.py "input" --excel
    python extract_paper.py "input" --excel filename.xlsx
    python extract_paper.py "input" --journal aps --excel
"""

import sys
import argparse
from multi_journal_extractor import extract_paper_info, JournalExtractorFactory
from export_utils import export_multi_journal_to_excel


def display_paper_info(paper_info: dict) -> None:
    """Display paper information in formatted console output"""
    
    if "Error" in paper_info:
        print(f"❌ {paper_info['Error']}")
        return
    
    print("📋 EXTRACTED PAPER INFORMATION:")
    print("=" * 80)
    
    # Display in organized sections
    sections = [
        ("📄 Paper Details", ["Paper Title", "Journal", "Publication Date", "DOI", "URL"]),
        ("📝 Abstract", ["Abstract"]),
        ("👥 Author Information", ["Author Information"])
    ]
    
    for section_name, keys in sections:
        print(f"\n{section_name}:")
        print("-" * 50)
        
        for key in keys:
            if key in paper_info:
                value = paper_info[key]
                if key == "Author Information":
                    print(value)
                elif key == "Abstract":
                    # Wrap long abstracts
                    if len(value) > 300:
                        print(f"{value[:300]}...")
                    else:
                        print(value)
                else:
                    print(f"{key}: {value}")
    
    print("\n" + "=" * 80)


def create_table_display(paper_info: dict) -> str:
    """Create simple table display of key information"""
    if "Error" in paper_info:
        return f"Error: {paper_info['Error']}"
    
    # Extract key info for table
    title = paper_info.get("Paper Title", "")[:40] + "..." if len(paper_info.get("Paper Title", "")) > 40 else paper_info.get("Paper Title", "")
    journal = paper_info.get("Journal", "")
    date = paper_info.get("Publication Date", "")
    
    # Get first author for summary
    author_info = paper_info.get("Author Information", "")
    first_author = ""
    if author_info:
        lines = author_info.split('\n')
        for line in lines:
            if line.strip():
                # Remove marker and get just the name
                clean_line = line.strip().lstrip('#*').strip()
                first_author = clean_line.split('(')[0].strip()
                break
    
    return f"""
📊 SUMMARY TABLE:
{'-'*80}
{'Title':<20} | {'Journal':<15} | {'Date':<12} | {'First Author':<25}
{'-'*80}
{title:<20} | {journal:<15} | {date:<12} | {first_author:<25}
{'-'*80}
"""


def main():
    parser = argparse.ArgumentParser(
        description='Extract information from academic journal papers (Nature, APS, etc.)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Extract from URL
    python extract_paper.py "https://www.nature.com/articles/s41467-025-61342-8"
    python extract_paper.py "https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.123.456789"
    
    # Search by title
    python extract_paper.py "quantum computation topological"
    python extract_paper.py "machine learning" --journal nature
    
    # Export to Excel
    python extract_paper.py "quantum entanglement" --excel
    python extract_paper.py "some paper title" --excel my_paper.xlsx
    
    # Search specific journal
    python extract_paper.py "condensed matter" --journal aps --excel

Supported Journals:
    - Nature (nature.com)
    - APS journals (journals.aps.org): PRL, PRA, PRB, PRC, PRD, PRE, PRX, PRX Quantum, etc.
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Paper URL, DOI, or title to search'
    )
    
    parser.add_argument(
        '--journal', '-j',
        choices=['nature', 'aps'],
        help='Preferred journal to search (nature/aps)'
    )
    
    parser.add_argument(
        '--excel', '-e',
        nargs='?',
        const='auto',
        help='Export to Excel file (optionally specify filename)'
    )
    
    parser.add_argument(
        '--table', '-t',
        action='store_true',
        help='Show summary table format'
    )
    
    parser.add_argument(
        '--list-journals',
        action='store_true',
        help='List supported journals'
    )
    
    args = parser.parse_args()
    
    # Show supported journals
    if args.list_journals:
        print("🔬 Supported Journals:")
        for journal in JournalExtractorFactory.list_supported_journals():
            print(f"  - {journal}")
        return 0
    
    # Check if input is provided when not listing journals
    if not args.input:
        parser.error("input is required unless using --list-journals")
        return 1
    
    print("🔬 Multi-Journal Paper Extractor")
    print("=" * 50)
    
    # Extract paper information
    try:
        result = extract_paper_info(args.input, journal=args.journal)
        
        if "Error" in result:
            print(f"❌ {result['Error']}")
            return 1
        
        # Display results
        if args.table:
            print(create_table_display(result))
        else:
            display_paper_info(result)
        
        # Export to Excel if requested
        if args.excel:
            print("\n📊 EXCEL EXPORT:")
            print("=" * 50)
            
            filename = None if args.excel == 'auto' else args.excel
            excel_file = export_multi_journal_to_excel(result, filename)
            
            if excel_file:
                print(f"✅ Excel file created: {excel_file}")
                
                # Show what was exported
                journal = result.get("Journal", "Unknown")
                author_count = len([line for line in result.get("Author Information", "").split('\n') if line.strip()])
                print(f"📝 Exported: {journal} paper with {author_count} authors")
            else:
                print("❌ Failed to create Excel file")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())