# Nerdo.Africa

**Bridging the Gap Between Talent and Opportunity**

Nerdo.Africa is a comprehensive platform designed to combat youth unemployment in Kenya and across Africa. It connects freelance talent with digital jobs and addresses the skills gap using intuitive learning roadmaps, verification tools, and integrated communications and payments.

## Key Features

### AI-Driven Skill Roadmaps

Unlike standard job boards, Nerdo doesn't just show you a job you aren't ready for.

- **Tailored Learning**: Users select an interest (e.g., "Data Entry"), and the system uses the YouTube Data API to generate a curated "Zero to Hero" learning path made of quality video modules.
- **Progress Tracking**: Users can track their progress through video modules with personalized dashboards and milestones.

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

## Project Structure

The project is organized into modular applications within the `nerdo_project/apps` directory:

- **users**: Handles user authentication, profiles, and role management (Applicant vs. Employer).
- **learning**: The core AI Learning Hub. Generates video roadmaps using Gemini AI and YouTube Data API.
- **opportunities**: Manages job listings, applications, reminders, and employer dashboards.
- **community**: A forum for users to share posts, like, and comment.
- **billing**: Integrates M-Pesa for payment processing.

## Local Setup Instructions

Follow these steps to run the project locally for development or grading.

### Prerequisites

- Python 3.8 or higher
- Git installed
- SQLite (Default for development) or MariaDB/PostgreSQL (for production)

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

   Create a `.env` file in the root directory.

   ```env
   SECRET_KEY=django-insecure-dev-key-placeholder
   DEBUG=True

   # Database (Defaults to SQLite if not set, or configure for MariaDB)
   # DB_NAME=nerdo_db
   # DB_USER=root
   # DB_PASSWORD=

   # Google Gemini AI (Required for Roadmaps)
   GEMINI_API_KEY=your_gemini_api_key_here
   # Cache timeout in seconds (default 24h)
   CACHE_TIMEOUT=86400

   # YouTube Data API (For fetching video content)
   # Supports multiple keys for rotation to handle quota limits
   YOUTUBE_API_KEY1=your_youtube_key_1
   YOUTUBE_API_KEY2=your_youtube_key_2
   YOUTUBE_API_KEY3=your_youtube_key_3

   # Africa's Talking (For SMS Alerts)
   AFRICASTALKING_USERNAME=sandbox
   AFRICASTALKING_API_KEY=your_africas_talking_key

   # M-Pesa Daraja API (For Payments)
   MPESA_ENVIRONMENT=sandbox
   MPESA_CONSUMER_KEY=your_mpesa_consumer_key
   MPESA_CONSUMER_SECRET=your_mpesa_consumer_secret
   MPESA_SHORTCODE=174379
   MPESA_EXPRESS_SHORTCODE=174379
   MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
   ```

5. **Run Migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**

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

## Author

- [@7ever](https://github.com/7ever)

## License

Distributed under the MIT License. See [`LICENSE`](https://github.com/7ever/Nerdo.Africa/blob/main/LICENSE) file for more information.

Built for the Youth of Africa.
