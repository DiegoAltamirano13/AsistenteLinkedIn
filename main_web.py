from app import create_app
import os
import webbrowser

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    webbrowser.open(f'http://localhost:{port}')
    app.run(host='0.0.0.0', port=port, debug=True)