**Project Requirement: APS Journal Parser**

Develop a function to extract metadata from American Physical Society (APS) journals given a paper title or URL. Parsed information should be structured into a table.

### Key Features:

1. **Input Flexibility**:
   * Accept either a paper title (search APS website: **https://www.aps.org**) or direct APS article URL.
2. **Metadata Extraction**:
   * **Title**: Name of the paper
   * **Publication Date**: In `DD Month, YYYY`format
   * **Abstract**: Full abstract text
   * **Authors**: Structured list with:
     * Full name(s) and affiliation(s) (institution + country)
     * `*`for **corresponding authors**
     * `#`for **first/co-first authors**
     * Nationality inferred from affiliations
3. **Output Format**:
   All data compiled into a table with columns:
   `Title | Publication Date | Abstract | Authors`

### Example Execution:

**Input**:

URL = `https://journals.aps.org/prxquantum/abstract/10.1103/kw39-yxq5`

**Extracted Output**:

<pre class="ybc-pre-component ybc-pre-component_not-math"><div class="hyc-common-markdown__code"><div class="expand-code-width-placeholder"></div><div class="hyc-common-markdown__code__hd"></div><pre class="hyc-common-markdown__code-lan"><div class="hyc-code-scrollbar"><div class="hyc-code-scrollbar__view"><code class="language-markdown">Title: Exponentially Reduced Circuit Depths Using Trotter Error Mitigation  
Publication Date: 12 August, 2025  
Abstract: [Full abstract text as in the specification]  
Authors:  
  - Author 1 (Affiliation 1, Country)*#  
  - Author 2 (Affiliation 2, Country)#  
  - Author 3 (Affiliation 3, Country)*</code></div><div class="hyc-code-scrollbar__track"><div class="hyc-code-scrollbar__thumb"></div></div><div><div></div></div></div></pre></div></pre>

### Technical Specifications:

1. **Author Annotation**:
   * `*`= Corresponding author (prioritize explicit footnotes like `*Corresponding author`)
   * `#`= First/co-first author (derive from: author order + footnotes like `*These authors contributed equally`)
2. **Country Extraction**:
   * Parse affiliation strings to detect country names (e.g., "Stanford University, USA" → `USA`).
   * Fallback to full affiliation text if country ambiguous.
3. **APS Website Handling**:
   * Automatically resolve titles to URLs via APS search.
   * Handle abstract page structure (e.g., `https://journals.aps.org/{journal}/abstract/{doi}`).
4. **Edge Cases**:
   * Missing abstracts/affiliations
   * No corresponding/first-author markers
   * Multi-country affiliations

### Output Table Structure:

| Title    | Publication Date | Abstract | Authors          |
| -------- | ---------------- | -------- | ---------------- |
| [String] | [String]         | [String] | [Annotated list] |

---

**Implementation Ready for AI Development**.

The requirement emphasizes unambiguous data extraction, annotation logic, and structured output. The example URL demonstrates the expected input→output transformation.
