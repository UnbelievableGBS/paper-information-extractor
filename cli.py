#!/usr/bin/env python3
"""
Command Line Interface - simple, clean implementation
No special cases, just straightforward functionality
"""

import argparse
import sys
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src import ExtractionService, ExportService, setup_logging


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Paper Information Extractor CLI",
        epilog="Supports Nature, Science.org, and APS journals"
    )
    
    parser.add_argument(
        "input",
        help="Paper URL or title to extract"
    )
    
    parser.add_argument(
        "--journal", "-j",
        choices=["nature", "science", "aps"],
        help="Journal hint for faster extraction"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["excel", "json", "csv"],
        default="excel",
        help="Export format (default: excel)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output filename (auto-generated if not specified)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize services
        extraction_service = ExtractionService()
        export_service = ExportService()
        
        print("🔬 Paper Information Extractor")
        print("=" * 50)
        
        # Extract paper information
        print(f"📋 Processing: {args.input}")
        if args.journal:
            print(f"🎯 Journal hint: {args.journal}")
        
        result = extraction_service.extract_paper(
            input_text=args.input,
            journal_hint=args.journal
        )
        
        if not result.success:
            print(f"❌ Extraction failed: {result.error}")
            return 1
        
        paper = result.paper
        
        # Display results
        print("\n✅ Successfully extracted paper information:")
        print(f"  📄 Title: {paper.title}")
        print(f"  📖 Journal: {paper.journal.value.title()}")
        print(f"  👥 Authors: {paper.author_count}")
        print(f"  📝 Abstract: {len(paper.abstract)} characters")
        if paper.doi:
            print(f"  🔗 DOI: {paper.doi}")
        
        # Export to specified format
        print(f"\n📊 Exporting to {args.format.upper()}...")
        
        if args.format == "excel":
            output_file = export_service.export_to_excel(paper, args.output)
        elif args.format == "json":
            output_file = export_service.export_to_json(paper, args.output)
        elif args.format == "csv":
            output_file = export_service.export_to_csv(paper, args.output)
        
        print(f"✅ Exported to: {output_file}")
        
        # Display author information
        print(f"\n👥 Authors ({paper.author_count}):")
        for i, author in enumerate(paper.authors, 1):
            role_markers = []
            if any(role.value in ['first', 'co_first'] for role in author.roles):
                role_markers.append("🥇")
            if any(role.value == 'corresponding' for role in author.roles):
                role_markers.append("✉️")
            
            marker_str = " ".join(role_markers)
            print(f"  {i:2d}. {author.name} {marker_str}")
            
            if author.affiliations:
                for affil in author.affiliations:
                    print(f"      📍 {affil}")
        
        print(f"\n🎉 Extraction completed in {result.extraction_time:.2f}s")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 130
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())