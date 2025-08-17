I want you to write a Python script that can scrape research papers from the APS (American Physical Society) journal website (https://www.aps.org/).

Requirements:

Input:

Either a direct APS paper link (e.g. https://journals.aps.org/prxquantum/abstract/10.1103/PRXQuantum.6.030202)

Or a paper title (e.g. "Practical Introduction to Benchmarking and Characterization of Quantum Computers").

Behavior:

If the input is a URL, go directly to that APS paper page and scrape.

If the input is a paper title, search it on the APS site, find the correct paper link, and then scrape.

Scraped Information:

Paper title

Abstract

Authors (with the following annotations when available):

First author (no mark)

Co-first authors → add # after their names

Corresponding （contact） author(s) → add * after their names

Output:

Save the scraped data into an Excel file (.xlsx) locally, with columns:

Title

Abstract

Authors

Implementation details:

Use Python

Use requests + BeautifulSoup for web scraping

Use openpyxl or pandas for saving Excel file

Handle errors gracefully (e.g. if paper not found, print a clear error message).

Deliverable:
Provide the complete Python script that fulfills these requirements.