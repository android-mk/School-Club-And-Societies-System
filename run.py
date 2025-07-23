import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)