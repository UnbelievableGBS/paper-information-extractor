# Multi-Journal Paper Extractor

A unified Python tool for extracting author information and paper details from multiple academic journal publishers, including **Nature** and **APS (American Physical Society)** journals.

## 🔬 Supported Journals

### Nature Journals
- Nature.com articles
- All Nature family journals

### APS Journals  
- Physical Review Letters (PRL)
- Physical Review A, B, C, D, E, X
- PRX Quantum
- Reviews of Modern Physics
- Physical Review Applied
- All journals.aps.org publications

## ✨ Key Features

### 🎯 Unified Interface
- Single command works across all supported journals
- Auto-detects journal type from URL
- Consistent output format regardless of source

### 📊 Multiple Output Formats
- **Console**: Formatted text display
- **Table**: Summary table view
- **Excel**: Professional spreadsheet with journal-specific styling

### 🔍 Smart Input Handling
- **URLs**: Direct paper extraction
- **DOIs**: Automatic resolution to publisher
- **Titles**: Intelligent search across journals
- **Journal Preference**: Search specific publishers

### 📋 Comprehensive Data Extraction
- Paper title (exact as published)
- Publication date
- Complete abstract
- Author information with corrected markers:
  - `#` First author
  - `*` Corresponding authors  
  - No marker for co-authors
- Journal name and publisher
- DOI when available
- Full author affiliations with countries

## 🚀 Installation

```bash
# Install required dependencies
pip install requests beautifulsoup4 lxml openpyxl
```

## 📖 Usage

### Command Line Interface

```bash
# Basic extraction
python extract_paper.py "https://www.nature.com/articles/s41467-025-61342-8"
python extract_paper.py "https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.123.456"

# Search by title
python extract_paper.py "quantum computation topological"
python extract_paper.py "machine learning" --journal nature

# Export to Excel
python extract_paper.py "quantum entanglement" --excel
python extract_paper.py "paper title" --excel custom_filename.xlsx

# Table summary view
python extract_paper.py "condensed matter physics" --table

# Search specific journals
python extract_paper.py "quantum mechanics" --journal aps --excel

# List supported journals
python extract_paper.py --list-journals
```

### Python API

```python
from multi_journal_extractor import extract_paper_info
from export_utils import export_multi_journal_to_excel

# Extract from any supported journal
result = extract_paper_info("https://www.nature.com/articles/...")
result = extract_paper_info("https://journals.aps.org/prl/abstract/...")

# Search with journal preference
result = extract_paper_info("quantum computing", journal="nature")
result = extract_paper_info("condensed matter", journal="aps")

# Export to Excel
excel_file = export_multi_journal_to_excel(result, "paper_analysis.xlsx")
```

## 📁 Output Format

### Dictionary Structure
```python
{
    "Paper Title": "Full paper title...",
    "Publication Date": "2025-08-05",
    "Abstract": "Complete abstract text...",
    "Author Information": "# FirstAuthor (...)\nCoAuthor (...)\n* CorrespondingAuthor (...)",
    "Journal": "Nature" or "Physical Review Letters" etc.,
    "DOI": "10.1038/...",
    "URL": "https://..."
}
```

### Author Information Format
```
# Filippo Iulianelli (Department of Physics, University of Southern California, Los Angeles, CA, USA)
Sung Kim (Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
Joshua Sussan (Department of Mathematics, CUNY Medgar Evers, Brooklyn, NY, USA; Mathematics Program, The Graduate Center, CUNY, New York, NY, USA)
* Aaron D. Lauda (Department of Physics, University of Southern California, Los Angeles, CA, USA; Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
```

## 📊 Excel Export Features

### Journal-Specific Styling
- **Nature**: Green color scheme with Nature branding
- **APS**: Blue color scheme with APS styling
- **Others**: Extensible color system

### Rich Formatting
- Professional headers and borders
- Author role highlighting:
  - First authors: Light blue background + bold blue text
  - Corresponding authors: Light red background + bold red text
  - Co-authors: Standard formatting
- Summary statistics
- Column optimization for readability

### Multi-Paper Support
- Individual paper exports
- Comparison tables across journals
- Batch processing capabilities

## 🏗️ Architecture

### Extensible Design
```
JournalExtractor (Abstract Base)
├── NatureExtractor
├── APSExtractor
└── [Future: IEEEExtractor, ElsevierExtractor, etc.]
```

### Factory Pattern
- Auto-detection of journal types
- Easy addition of new publishers
- Consistent interface across all journals

### Modular Components
- `multi_journal_extractor.py`: Core extraction framework
- `export_utils.py`: Excel export utilities
- `extract_paper.py`: Command-line interface

## 🔧 Advanced Features

### Search Capabilities
- Intelligent title-based search
- Journal-specific search strategies
- Fallback across multiple publishers

### Error Handling
- Graceful handling of inaccessible papers
- Clear error messages and suggestions
- Timeout protection for network requests

### Performance
- Respectful request timing
- Efficient HTML parsing
- Cached session management

## 🎯 Use Cases

### Research Workflows
- Literature review automation
- Citation analysis
- Author collaboration mapping
- Multi-journal paper comparison

### Academic Administration
- Publication tracking
- Author affiliation analysis
- Journal coverage assessment
- Research impact measurement

### Data Analysis
- Large-scale paper processing
- Cross-journal studies
- Author network analysis
- Publication trend analysis

## 🚧 Future Extensions

### Planned Publishers
- IEEE Xplore
- arXiv.org
- Elsevier/ScienceDirect
- Springer journals
- Wiley publications

### Enhanced Features
- Batch processing from file lists
- Citation network extraction
- Author disambiguation
- Institution standardization
- API rate limiting
- Database storage options

## 🧪 Examples

### Nature Paper
```bash
$ python extract_paper.py "https://www.nature.com/articles/s41467-025-61342-8" --table

📊 SUMMARY TABLE:
--------------------------------------------------------------------------------
Title                | Journal         | Date         | First Author             
--------------------------------------------------------------------------------
Universal quantum... | Nature          | 2025-08-05   | Filippo Iulianelli       
--------------------------------------------------------------------------------
```

### APS Paper  
```bash
$ python extract_paper.py "https://journals.aps.org/prxquantum/abstract/10.1103/kw39-yxq5" --excel

✅ Excel file created: PRX_Quantum_Exponentially_Reduced_Circuit.xlsx
📝 Exported: PRX Quantum paper with 4 authors
```

### Multi-Journal Search
```bash
$ python extract_paper.py "quantum computation" --journal nature
✓ Searching Nature for: quantum computation
✓ Found: https://www.nature.com/articles/s41467-025-61342-8
```

## 🛠️ Development

### Adding New Journals
1. Create new extractor class inheriting from `JournalExtractor`
2. Implement required abstract methods
3. Add to `JournalExtractorFactory._extractors`
4. Add journal-specific styling to `export_utils.py`

### Testing
```bash
# Test core functionality
python multi_journal_extractor.py

# Test command-line interface
python extract_paper.py --list-journals
python extract_paper.py "test paper" --table
```

## 📋 Requirements

- Python 3.7+
- requests==2.31.0
- beautifulsoup4==4.12.3
- lxml==4.9.4
- openpyxl==3.1.2

## 🤝 Contributing

The architecture is designed for easy extension. New journal extractors can be added by implementing the `JournalExtractor` interface and adding journal-specific parsing logic.

## 📄 License

This project extends the original Nature extractor to support multiple academic publishers while maintaining the same high-quality extraction standards.