"""
Main entry point - the ONE way to extract papers.
Simple command line interface without enterprise bullshit.
"""

import sys
import argparse
from paper_extractor import extract_paper


def main():
    parser = argparse.ArgumentParser(description='Extract paper information from journal URLs')
    parser.add_argument('url', help='Paper URL (Nature, Science, or APS)')
    parser.add_argument('-o', '--output', help='Output file (optional)')
    
    args = parser.parse_args()
    
    try:
        result = extract_paper(args.url)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✅ Results saved to {args.output}")
        else:
            print(result)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()