## Web Service for Extracting Author Information from Science.org Papers

### 🔧 Feature 1: Web Page with Search Box

1. Build a simple web interface (e.g., using Flask + HTML/JS).
2. The page should include a search box that allows the user to input:
   - A paper title (e.g., *Non-Hermitian topological photonics*), or
   - A direct paper URL from `https://www.science.org`.

------

### 🔍 Feature 2: Paper URL Resolution Logic

1. **If the user inputs a paper title**:
   - Perform a search query on Science.org to locate the paper’s detail page.
   - Extract the link of the most relevant result.
2. **If the user inputs a direct paper URL**:
   - Use the given link directly for processing.

------

### 🧠 Feature 3: Author Information Extraction

1. Visit the target paper page and parse its HTML content.

2. Locate the author section at the DOM path:

   ```
   html
   
   
   复制编辑
   /html/body/div[1]/div/div[1]/main/div[1]/article/div[4]/div[1]/section[2]/section[1]
   ```

   (This corresponds to the `<section class="core-authors">` block.)

3. For each author, extract the following details:

   - Given name
   - Family name
   - ORCID (if available)
   - Email (if available)
   - Affiliation(s)
   - Roles
   - Author detail link (e.g., “View all articles by this author”)

4. Display the extracted author information on the frontend in a clean format (e.g., table or cards).

------

### 💾 Feature 4: Export to Excel

1. Provide a button to **export author information**.
2. When clicked, the system should generate and download an `.xlsx` file containing all extracted author data.
3. The exported Excel should include columns for:
   - Full Name
   - ORCID
   - Email
   - Affiliation(s)
   - Roles
   - Profile Link

------

### ✅ Suggested Tech Stack (Optional)

- **Backend**: Python (Flask or FastAPI), BeautifulSoup / lxml for HTML parsing
- **Frontend**: HTML + Bootstrap or similar UI framework
- **Excel Export**: `openpyxl` or `pandas.to_excel()` for `.xlsx` generation