#!/usr/bin/env python3
"""
Science.org Paper Author Extractor - Web Interface
Implements the web service requirements from the project description
"""

from flask import Flask, render_template, request, jsonify, send_file
from science_paper_extractor import SciencePaperExtractor
import tempfile
import os
from datetime import datetime

app = Flask(__name__)

# Initialize the extractor
extractor = SciencePaperExtractor()

@app.route('/')
def index():
    """Main page with search box"""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_authors():
    """Extract author information from Science.org paper"""
    try:
        # Get input from form
        user_input = request.form.get('input', '').strip()
        
        if not user_input:
            return jsonify({'error': 'Please provide a paper title or Science.org URL'})
        
        # Resolve URL if needed
        if user_input.startswith('https://www.science.org'):
            paper_url = user_input
        else:
            # Search for the paper
            paper_url = extractor.search_paper_by_title(user_input)
            if not paper_url:
                return jsonify({'error': f'Could not find paper on Science.org: {user_input}'})
        
        # Extract author information
        authors = extractor.extract_author_info(paper_url)
        
        if not authors:
            return jsonify({'error': 'No authors found for this paper'})
        
        # Return results
        return jsonify({
            'success': True,
            'paper_url': paper_url,
            'authors': authors,
            'total_authors': len(authors),
            'corresponding_authors': sum(1 for a in authors if a.get('is_corresponding', False))
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'})

@app.route('/export', methods=['POST'])
def export_to_excel():
    """Export author information to Excel file"""
    try:
        # Get authors data from request
        authors_data = request.json.get('authors', [])
        
        if not authors_data:
            return jsonify({'error': 'No author data to export'})
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            filename = tmp_file.name
        
        # Export to Excel
        result_filename = extractor.export_to_excel(authors_data, filename)
        
        if result_filename:
            # Send file to user
            return send_file(
                result_filename,
                as_attachment=True,
                download_name=f'science_authors_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            return jsonify({'error': 'Failed to create Excel file'})
            
    except Exception as e:
        return jsonify({'error': f'Error exporting to Excel: {str(e)}'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create the HTML template
    create_html_template()
    
    print("🌐 Starting Science.org Author Extractor Web Service...")
    print("📝 Features:")
    print("   - Search by paper title or direct Science.org URL")
    print("   - Extract author information with ORCID, email, affiliations, roles")
    print("   - Export to Excel with corresponding author highlighting")
    print("\n🔗 Access the web interface at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_html_template():
    """Create the HTML template for the web interface"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Science.org Author Extractor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
        }
        .author-card {
            border-left: 4px solid #007bff;
            margin-bottom: 1rem;
        }
        .corresponding-author {
            border-left-color: #dc3545 !important;
            background-color: #fff5f5;
        }
        .orcid-link {
            color: #a6ce39;
            text-decoration: none;
        }
        .loading {
            display: none;
        }
    </style>
</head>
<body>
    <div class="hero-section">
        <div class="container">
            <h1 class="display-4">🔬 Science.org Author Extractor</h1>
            <p class="lead">Extract detailed author information from Science.org papers</p>
        </div>
    </div>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card">
                    <div class="card-header">
                        <h5>🔍 Search for Paper</h5>
                    </div>
                    <div class="card-body">
                        <form id="searchForm">
                            <div class="mb-3">
                                <label for="paperInput" class="form-label">Paper Title or Science.org URL</label>
                                <input type="text" class="form-control" id="paperInput" 
                                       placeholder="e.g., 'Non-Hermitian topological photonics' or 'https://www.science.org/doi/...'">
                                <div class="form-text">
                                    Enter a paper title to search, or paste a direct Science.org URL
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary">
                                <span class="loading spinner-border spinner-border-sm me-2" role="status"></span>
                                Extract Authors
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div id="results" class="mt-4" style="display: none;">
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5>👥 Author Information</h5>
                            <button id="exportBtn" class="btn btn-success btn-sm">
                                📊 Export to Excel
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="paperInfo" class="mb-3"></div>
                            <div id="authorList"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div id="error" class="alert alert-danger mt-4" style="display: none;"></div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let currentAuthors = [];

        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const input = document.getElementById('paperInput').value.trim();
            if (!input) {
                showError('Please enter a paper title or URL');
                return;
            }

            showLoading(true);
            hideError();
            hideResults();

            try {
                const response = await fetch('/extract', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `input=${encodeURIComponent(input)}`
                });

                const data = await response.json();

                if (data.success) {
                    currentAuthors = data.authors;
                    displayResults(data);
                } else {
                    showError(data.error);
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                showLoading(false);
            }
        });

        document.getElementById('exportBtn').addEventListener('click', async function() {
            if (currentAuthors.length === 0) {
                showError('No authors to export');
                return;
            }

            try {
                const response = await fetch('/export', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({authors: currentAuthors})
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `science_authors_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.xlsx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    const error = await response.json();
                    showError(error.error);
                }
            } catch (error) {
                showError('Export error: ' + error.message);
            }
        });

        function displayResults(data) {
            const paperInfo = `
                <div class="alert alert-info">
                    <strong>Paper URL:</strong> <a href="${data.paper_url}" target="_blank">${data.paper_url}</a><br>
                    <strong>Total Authors:</strong> ${data.total_authors} 
                    (${data.corresponding_authors} corresponding)
                </div>
            `;
            document.getElementById('paperInfo').innerHTML = paperInfo;

            const authorHtml = data.authors.map(author => `
                <div class="card author-card ${author.is_corresponding ? 'corresponding-author' : ''}">
                    <div class="card-body">
                        <h6 class="card-title">
                            ${author.full_name}
                            ${author.is_corresponding ? '<span class="badge bg-danger ms-2">Corresponding</span>' : ''}
                        </h6>
                        ${author.orcid ? `<p class="mb-1"><strong>ORCID:</strong> <a href="https://orcid.org/${author.orcid}" target="_blank" class="orcid-link">${author.orcid}</a></p>` : ''}
                        ${author.email ? `<p class="mb-1"><strong>Email:</strong> ${author.email}</p>` : ''}
                        ${author.affiliations ? `<p class="mb-1"><strong>Affiliations:</strong> ${author.affiliations}</p>` : ''}
                        ${author.roles ? `<p class="mb-1"><strong>Roles:</strong> ${author.roles}</p>` : ''}
                        ${author.profile_link ? `<p class="mb-1"><strong>Profile:</strong> <a href="${author.profile_link}" target="_blank">View all articles</a></p>` : ''}
                    </div>
                </div>
            `).join('');

            document.getElementById('authorList').innerHTML = authorHtml;
            document.getElementById('results').style.display = 'block';
        }

        function showError(message) {
            document.getElementById('error').textContent = message;
            document.getElementById('error').style.display = 'block';
        }

        function hideError() {
            document.getElementById('error').style.display = 'none';
        }

        function hideResults() {
            document.getElementById('results').style.display = 'none';
        }

        function showLoading(show) {
            document.querySelector('.loading').style.display = show ? 'inline-block' : 'none';
        }
    </script>
</body>
</html>'''
    
    # Write the template file
    with open('templates/index.html', 'w') as f:
        f.write(html_content)
    
    print("✅ HTML template created at templates/index.html")