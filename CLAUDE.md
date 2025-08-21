# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a paper information extractor that scrapes academic papers from Nature, Science, and APS journals. The system extracts author information, affiliations, abstracts, and other metadata, then uses DeepSeek LLM to generate Chinese news-style summaries and structured information extraction.

## Architecture

### Current Implementation
- **Individual extractors**: `nature_extractor.py`, `science_extractor.py`, `aps_extractor.py` - Each handles journal-specific HTML parsing
- **Main orchestrator**: `main.py` - Routes URLs to appropriate extractors and processes results through DeepSeek LLM
- **LLM post-processing**: Uses DeepSeek API to generate Chinese summaries and extract structured information

### Data Flow
1. URL → Journal detection (nature/science/aps)
2. Journal-specific extractor → Raw paper data (JSON)
3. DeepSeek LLM → Chinese news summary + structured extraction
4. Output structured data with regex parsing

## Key Components

### Journal Extractors
Each extractor (`*_extractor.py`) implements paper parsing with:
- HTTP request handling with anti-bot protection (random delays, proper headers)
- BeautifulSoup HTML parsing with journal-specific selectors
- Author/affiliation mapping and role detection (first author, corresponding author)
- Institution name cleaning (extracts university/institute level, removes departments)
- Country extraction from affiliations

### LLM Integration
- **API**: DeepSeek Chat API via OpenAI-compatible interface
- **Task**: Dual-purpose prompt for Chinese news generation + structured extraction
- **Output parsing**: Regex patterns extract structured data from LLM response

## Dependencies
- `requests`, `beautifulsoup4` - Web scraping
- `openai` - DeepSeek API client  
- `pandas` - Data handling
- `re` - Text processing and output parsing

## Environment Setup
```bash
export DEEPSEEK_API_KEY="your-api-key"
```

## Usage Patterns

### Running Single Paper Extraction
```bash
python main.py  # Uses hardcoded URL in __main__
```

### Adding New Journal Support
1. Create new `*_extractor.py` with `parse_*_authors(url)` function
2. Add journal detection logic to `main()` function
3. Follow existing patterns for HTTP handling and data structure

### Modifying LLM Behavior
- Edit `system_prompt` variable in `main.py`
- Update regex patterns in `extract_paper_info()` if output format changes
- LLM expects specific JSON input format with `title`, `url`, `authors`, `countries`, etc.

## Development Notes

### Anti-Bot Protection
All extractors implement:
- Random delays (1-6 seconds)
- Comprehensive browser headers
- Retry logic with exponential backoff
- 403 error handling

### Data Structure Conventions
- Authors have `name`, `role`, `affiliations`, `is_corresponding` fields
- Institutions cleaned to university/institute level only
- Countries extracted and normalized (USA, UK standardization)
- Publication dates formatted as both ISO and human-readable

### Error Handling
- Network failures: Retry with delays
- Parsing failures: Return empty/default structures
- LLM failures: Graceful degradation with error logging

## Output Format
The system produces both:
1. **Chinese news summary**: Academic paper presented as news article
2. **Structured extraction**: First author units, corresponding author units, countries, URLs

Chinese translation is handled by the LLM for all institutional names and countries.