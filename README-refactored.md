# Paper Information Extractor

> Clean, unified system for extracting academic paper information from multiple journals

## Supported Journals

- **Nature** journals (nature.com)
- **Science.org** papers
- **APS** journals (journals.aps.org)

## Architecture

Clean layered design following good engineering principles:

```
src/
├── models/          # Data structures
├── core/           # Base abstractions  
├── extractors/     # Journal-specific implementations
├── services/       # Business logic
├── api/           # REST API interface
└── utils/         # Common utilities
```

## Quick Start

### Installation

```bash
pip install -r requirements-refactored.txt
```

### Command Line Usage

```bash
# Extract by URL
python cli.py "https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.010344"

# Extract by title with journal hint
python cli.py "Strong-to-Weak Spontaneous Symmetry Breaking" --journal aps

# Export to different formats
python cli.py "paper_title" --format json --output my_paper.json
```

### API Server

```bash
# Start development server
python server.py

# API available at: http://localhost:8000
# Documentation: http://localhost:8000/docs
```

### Python API

```python
from src import ExtractionService, ExportService

# Initialize services
extraction = ExtractionService()
export = ExportService()

# Extract paper
result = extraction.extract_paper("https://www.nature.com/articles/...")

if result.success:
    paper = result.paper
    print(f"Title: {paper.title}")
    print(f"Authors: {paper.author_count}")
    
    # Export to Excel
    filename = export.export_to_excel(paper)
    print(f"Exported to: {filename}")
```

## API Endpoints

### Core Extraction

- `POST /extract` - Extract paper information
- `POST /extract/batch` - Batch extraction
- `GET /search/{journal}` - Search specific journal

### Utility

- `GET /journals` - List supported journals
- `GET /health` - Health check
- `GET /stats` - Usage statistics

### Example API Request

```bash
curl -X POST "http://localhost:8000/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "input_text": "https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.010344",
    "journal_hint": "aps"
  }'
```

## Features

### Author Information

- **Name extraction** with proper formatting
- **Role detection** (first, co-first, corresponding)
- **ORCID integration** where available
- **Affiliation mapping** with institutional details
- **Contact information** extraction

### Export Formats

- **Excel** (.xlsx) with journal-specific styling
- **JSON** for programmatic use
- **CSV** for data analysis

### Error Handling

- **Graceful degradation** when access is restricted
- **Multiple access methods** for different journals
- **Comprehensive logging** for debugging
- **Validation** of extracted data

## Design Principles

### Good Taste Applied

- **No special cases** - uniform interface across journals
- **Clean abstractions** - base classes eliminate code duplication  
- **Simple data flow** - request → extract → validate → export
- **Composition over inheritance** - services use extractors, don't extend them

### Pragmatic Choices

- **FastAPI** for modern async API development
- **Pydantic** for data validation without complexity
- **BeautifulSoup** for reliable HTML parsing
- **Factory pattern** for extractor selection

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src

# Integration tests (requires network)
pytest tests/ -m integration
```

## Development

### Adding New Journals

1. Create extractor in `src/extractors/`
2. Inherit from `BaseExtractor`
3. Implement required methods
4. Register in `ExtractionService`

### Code Style

```bash
# Format code
black src/ tests/

# Lint code  
flake8 src/ tests/
```

## Project Structure

```
├── src/                    # Main source code
│   ├── models/            # Data models
│   ├── core/              # Base abstractions
│   ├── extractors/        # Journal extractors
│   ├── services/          # Business logic
│   ├── api/               # REST API
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── config/                # Configuration files
├── docs/                  # Documentation
├── cli.py                 # Command line interface
├── server.py              # Development server
└── requirements-refactored.txt
```

## License

This project follows clean engineering principles and is designed for educational and research purposes.