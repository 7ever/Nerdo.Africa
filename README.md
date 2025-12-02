🌍 Nerdo.Africa

Nerdo.Africa is a comprehensive digital ecosystem designed to bridge the gap between African youth and the global freelancing economy. By leveraging AI-driven learning paths and integrating local financial infrastructures like M-Pesa, we are tackling youth unemployment directly.

🚀 Key Features

🤖 AI Learning Roadmap: A "YouTube-style" recommendation engine that curates personalized video tutorials to take users from novice to expert based on market demand.

📋 Smart Job Board: Aggregates remote freelance gigs specifically available to African applicants, filtering out geo-blocked opportunities.

📅 Opportunity Reminders: Automated notifications for upcoming job application windows, sponsorships, and funding programs.

💳 M-Pesa Integration: Seamless payment processing for premium features and verifications using Safaricom's Daraja API.

🇰🇪 Civic Integration: Aligns with the Ajira Digital Program for verified digital skills certification.

🛠 Tech Stack

Backend: Python 3.11+, Django 5.0, Django REST Framework

Frontend: HTML5, CSS3, Bootstrap 5

Database: PostgreSQL (Production), SQLite (Dev)

APIs: Safaricom Daraja (M-Pesa), Google YouTube Data API, GOK Ajira Digital frameworks

Task Queue: Celery & Redis (for notifications)

📦 Installation

Clone the repository:

git clone [(https://github.com/7ever/Nerdo.Africa.git)](https://github.com/7ever/Nerdo.Africa.git)
cd Nerdo.Africa


Create and activate a virtual environment:

python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate


Install dependencies:

pip install -r requirements.txt


Set up Environment Variables:
Create a .env file in the root directory (see .env.example) and add your API keys:

SECRET_KEY=your_django_secret
DEBUG=True
MPESA_CONSUMER_KEY=your_key
MPESA_CONSUMER_SECRET=your_secret
YOUTUBE_API_KEY=your_key


Run Migrations:

python manage.py migrate


Start the Server:

python manage.py runserver


🤝 Contributing

We welcome contributions from the community! Please read our CONTRIBUTING.md to get started.

📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
