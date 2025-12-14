"""
Simple startup script for the Lost and Found Management System
"""

from app import app

if __name__ == '__main__':
    print("🚀 Starting Lost and Found Management System...")
    print("📍 The application will be available at: http://127.0.0.1:5000")
    print("🔧 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run the Flask application - configure for production
    import os
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() in ['true', '1', 'yes']
    
    app.run(host=host, port=port, debug=debug)