# 🏫 Victory School Club Management System

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)

A comprehensive web-based system for managing school clubs, memberships, activities, and finances with admin dashboard capabilities.

## ✨ Features

### 🎯 Core Functionality
- **Club Management**: Create, view, and manage school clubs
- **Student Registration**: Register students with profile management
- **Membership System**: Track club memberships and roles
- **Leadership Assignment**: Assign chairpersons, secretaries, etc.

### 💰 Financial Tracking
- Membership fee collection
- Activity revenue tracking
- Financial allocations (50% activities, 30% party fund, 20% savings)
- Visual financial dashboards

### 📅 Activity Management
- Schedule and track club activities
- View past and upcoming events
- Generate activity reports

### 👨‍💼 Admin Tools
- Patron/Teacher management
- Approval workflows for membership changes
- Comprehensive dashboard with analytics

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/android-mk/victory-club-system.git
   cd victory-club-system

    Create and activate virtual environment:
    bash

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

Install dependencies:
bash

pip install -r requirements.txt

Initialize the database:
bash

    python init_db.py

Configuration

Create .env file:
ini

FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

🖥️ Running the System
bash

flask run

Access the system at: http://localhost:5000


📂 Project Structure
text

victory-club-system/
├── app/                  # Application code
│   ├── static/           # CSS, JS, images
│   ├── templates/        # HTML templates
│   ├── __init__.py       # Flask app initialization
│   └── routes.py         # Application routes
├── data_access/          # Data access layer
├── database/             # Database configuration
├── instance/             # Instance folder
├── requirements.txt      # Dependencies
└── README.md             # This file

🤝 Contributing

    Fork the project

    Create your feature branch (git checkout -b feature/AmazingFeature)

    Commit your changes (git commit -m 'Add some amazing feature')

    Push to the branch (git push origin feature/AmazingFeature)

    Open a Pull Request

📄 License

Distributed under the MIT License. See LICENSE for more information.
✉️ Contact

Project Maintainer - Android-MK
Phone No: 254797243918
Project Link: (https://github.com/android-mk/School-Club-And-Societies-System)
