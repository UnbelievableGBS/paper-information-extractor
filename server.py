#!/usr/bin/env python3
"""
Development server launcher - simple script to run the API
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils import setup_logging

def main():
    """Launch the FastAPI development server"""
    import uvicorn
    
    # Setup logging
    setup_logging("INFO")
    
    print("🚀 Starting Paper Information Extractor API")
    print("📚 Supported journals: Nature, Science.org, APS")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API documentation: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    
    # Import the app after setting up the path
    from src.api import app
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    main()