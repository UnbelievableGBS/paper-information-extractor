# Paper Information Extractor

Clean, unified paper extraction for Nature, Science, and APS journals.

## Usage

### Command Line
```bash
python main.py https://www.nature.com/articles/s41567-025-02944-3
python main.py https://www.science.org/doi/10.1126/scitranslmed.ads7438 -o output.json
```

### Python API
```python
from paper_extractor import extract_paper

# New unified interface
result = extract_paper(url)  # Returns JSON string

# Legacy compatibility
from legacy_wrappers import parse_nature_authors, parse_science_authors, scrape_aps_authors
nature_data = parse_nature_authors(nature_url)
science_data = parse_science_authors(science_url)
aps_data = scrape_aps_authors(aps_url)
```

## Architecture

- `paper_model.py` - Unified data structures
- `base_extractor.py` - Common HTTP/parsing logic  
- `paper_extractor.py` - Main extractor with journal detection
- `legacy_wrappers.py` - Backward compatibility
- `main.py` - Command line interface

## Supported Journals

- **Nature** (`nature.com`)
- **Science** (`science.org`)  
- **APS Journals** (`journals.aps.org`)

No special cases. No duplicate code. One extractor that works.