# Nerdo.Africa

**Bridging the Gap Between Talent and Opportunity**

Nerdo.Africa is a comprehensive platform designed to combat youth unemployment in Kenya and Africa. It connects freelance talent with digital jobs while solving the skills gap through AI-driven learning roadmaps. By aligning with the Government of Kenya's Ajira Digital framework, this project ensures that youth are not just finding jobs, but are verified, skilled, and digitally ready for the global market.

## Key Features

### AI-Driven Skill Roadmaps

Unlike standard job boards, Nerdo doesn't just show you a job you aren't ready for.

- **Tailored Learning**: Users select an interest (e.g., "Data Entry"), and the system uses the YouTube Data API to generate a curated "Zero to Hero" learning path.
- **Progress Tracking**: Users can track their progress through video modules with personalized dashboards.

### GOK-Aligned Verification

- **Simulated Ajira Validation**: The platform implements data structures compatible with the Ajira Digital Program to verify user identity and registration status.
- **Trust Badges**: Verified users receive a "Verified Talent" badge, increasing their hireability and trustworthiness to employers.

### Intelligent Reminders (SMS)

- **The 3-Day Rule**: The system automatically tracks application deadlines.
- **SMS Notifications**: Powered by Africa's Talking API (Sandbox), users receive SMS alerts 3 days before a job closes, ensuring they never miss an opportunity.

### Integrated Payment System

- **M-Pesa Integration**: Users can pay for premium verification or expedited alerts using Lipa Na M-Pesa (STK Push) for seamless mobile money transactions.

## Technical Stack

- **Backend Framework**: Django (Python)
- **Database**: MariaDB (Production-grade SQL)
- **Frontend**: Bootstrap (Responsive Mobile-First UI)
- **APIs Integrated**:
  - Google YouTube Data API (for fetching learning content)
  - Africa's Talking (for SMS notifications and alerts)
  - Safaricom Daraja (for M-Pesa payments)

## Local Setup Instructions

Follow these steps to run the project locally for development or grading.

### Prerequisites

- Python 3.8 or higher
- MariaDB (or XAMPP/WAMP) running and accessible
- Git installed

### Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/7ever/Nerdo.Africa.git
   cd Nerdo.Africa
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory. You can leave the API keys blank for the initial setup; the app will run, but SMS and YouTube features will be disabled.

   ```env
   SECRET_KEY=django-insecure-dev-key-placeholder
   DEBUG=True
   
   # Database
   DB_NAME=nerdo_db
   DB_USER=root
   DB_PASSWORD=
   
   # APIs (Leave blank for now)
   AFRICASTALKING_USERNAME=sandbox
   AFRICASTALKING_API_KEY=
   YOUTUBE_API_KEY=
   ```

5. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Start the Development Server**

   ```bash
   python manage.py runserver
   ```

   The application will be available at `http://localhost:8000`

## Contributing

This is a final year academic project, but contributions are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

Please ensure your code follows Django best practices and includes appropriate documentation.

### Reporting Bugs

If you find a bug, please create a GitHub Issue. Include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Screenshots if applicable

### Suggesting Enhancements

Have an idea for the AI Recommendation Engine or the Job Board? Open a Feature Request issue to discuss it before writing code.

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/7ever/Nerdo.Africa/blob/main/LICENSE) file for more information.

## Author

Built for the Youth of Africa.
