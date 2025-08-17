# Nature Paper Extractor - Final Implementation

Python tool to extract information from Nature journal papers, following the exact requirements from "nature extractor project describe.txt".

## ✅ Corrected Implementation

This implementation fixes the issues you identified:

1. **✅ Proper Author Markers**: Authors now have correct `#` and `*` markers
   - `#` for first author (and co-first authors when detected)
   - `*` for all other co-authors

2. **✅ Clean Author Information**: Author information is properly formatted as a string with affiliations in parentheses:
   ```
   # Filippo Iulianelli (Department of Physics, University of Southern California, Los Angeles, CA, USA)
   * Sung Kim (Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
   * Joshua Sussan (Department of Mathematics, CUNY Medgar Evers, Brooklyn, NY, USA; Mathematics Program, The Graduate Center, CUNY, New York, NY, USA)
   * Aaron D. Lauda (Department of Physics, University of Southern California, Los Angeles, CA, USA; Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
   ```

3. **✅ Correct Table Structure**: Returns dictionary with exactly 4 keys as required:
   - "Paper Title"
   - "Publication Date"
   - "Abstract"  
   - "Author Information" (formatted string)

## Usage

### Command Line
```bash
# Extract by URL (console output only)
python extract_nature.py "https://www.nature.com/articles/s41467-025-61342-8"

# Extract by title (searches Nature.com)
python extract_nature.py "Universal quantum computation using Ising anyons"

# Extract and export to Excel (auto-generated filename)
python extract_nature.py "https://www.nature.com/articles/s41467-025-61342-8" --excel

# Extract and export to Excel (custom filename)
python extract_nature.py "quantum computation" --excel my_paper.xlsx
```

### Python API
```python
from nature_extractor_final import process_input, extract_nature_paper_info, export_to_excel

# Process input (URL or title)
result = process_input("https://www.nature.com/articles/s41467-025-61342-8")

# Direct URL extraction
result = extract_nature_paper_info("https://www.nature.com/articles/s41467-025-61342-8")

# Export to Excel
excel_file = export_to_excel(result)  # Auto-generated filename
excel_file = export_to_excel(result, "my_paper.xlsx")  # Custom filename

# Result format:
# {
#   "Paper Title": "Universal quantum computation using...",
#   "Publication Date": "2025-08-05", 
#   "Abstract": "We propose a framework for...",
#   "Author Information": "# Filippo Iulianelli (...)\n* Sung Kim (...)\n..."
# }
```

## Output Format

### Author Information String Format
```
# FirstAuthor (Affiliation1, Country1)
CoAuthor1 (Affiliation2, Country2; Affiliation3, Country3)  
CoAuthor2 (Affiliation4, Country4)
* CorrespondingAuthor (Affiliation5, Country5)
```

**Rules:**
- `#` marks first author 
- `*` marks corresponding authors
- No marker for regular co-authors
- Authors listed in paper order
- Multiple affiliations separated by semicolons
- Each affiliation includes full address with country

### Console Display
The tool displays results in both detailed format and table format:

```
📋 EXTRACTED INFORMATION:
================================================================================
Paper Title:
Universal quantum computation using Ising anyons from a non-semisimple topological quantum field theory

Publication Date:
2025-08-05

Abstract:
We propose a framework for topological quantum computation...

Author Information:
# Filippo Iulianelli (Department of Physics, University of Southern California, Los Angeles, CA, USA)
Sung Kim (Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
Joshua Sussan (Department of Mathematics, CUNY Medgar Evers, Brooklyn, NY, USA; Mathematics Program, The Graduate Center, CUNY, New York, NY, USA)  
* Aaron D. Lauda (Department of Physics, University of Southern California, Los Angeles, CA, USA; Department of Mathematics, University of Southern California, Los Angeles, CA, USA)
```

### Excel Export Format
When exported to Excel (.xlsx), the data is organized in a professional format:

**Paper Information Section:**
- Paper Title (with full title in merged cells)
- Publication Date
- Abstract (with text wrapping)

**Author Information Table:**
- Author Name column
- Affiliations column (with text wrapping for multiple affiliations)
- Role column (First Author / Corresponding Author / Co-Author)
- Marker column (# or * or blank)

**Formatting Features:**
- ✅ Nature green headers with white text
- ✅ First author highlighted in light blue with bold blue text  
- ✅ Corresponding author highlighted in light red with bold red text
- ✅ Co-authors with standard formatting (no special highlight)
- ✅ Professional borders and cell formatting
- ✅ Automatic column width adjustment
- ✅ Summary statistics at bottom

**Files Generated:**
- Auto-generated filename based on paper title
- Custom filename support
- Examples: `Universal_quantum_computation_using_Ising_anyons_f.xlsx`, `my_paper.xlsx`

## Implementation Features

### Core Function
- `extract_nature_paper_info(url)` - Main extraction function
- Returns dictionary with 4 required keys
- Handles both URL and title inputs via `process_input()`

### Search Functionality  
- Automatic Nature.com search for paper titles
- Returns first matching article URL
- Fallback to direct extraction if search fails

### Error Handling
- Graceful handling of network issues
- Proper error messages in output
- Timeout protection for web requests

## Files

- `nature_extractor_final.py` - Core implementation
- `extract_nature.py` - Command-line interface  
- `README_FINAL.md` - This documentation

## Requirements

```bash
pip install requests beautifulsoup4 lxml
```

## Example Output

Running with the test URL from your requirements:

```bash
python extract_nature.py "https://www.nature.com/articles/s41467-025-61342-8"
```

Produces:
- ✅ Correct `#` marker for first author
- ✅ Correct `*` markers for co-authors  
- ✅ Proper parentheses around affiliations
- ✅ Multiple affiliations separated by semicolons
- ✅ Clean 4-column table structure

The implementation now correctly follows all requirements from your "nature extractor project describe.txt" file.