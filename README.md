# GMB Automation

A comprehensive automation platform for Google Business Profile (formerly Google My Business) that helps businesses manage their online presence, automate posts, and respond to reviews using AI.

## Features

- 🏢 **Multi-Location Management** - Manage multiple Google Business Profile locations from a single dashboard
- 📝 **AI-Powered Post Generation** - Automatically generate engaging posts using OpenAI
- ⭐ **Smart Review Management** - Automatically respond to customer reviews with AI-generated replies
- 📅 **Post Scheduling** - Schedule posts to be published at optimal times
- 🤖 **Automation** - Set up automatic posting and review responses per location
- 📊 **Analytics Dashboard** - Track performance across all your locations

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database management
- **PostgreSQL** - Primary database
- **Celery** - Distributed task queue for background jobs
- **Redis** - Message broker and cache
- **Google Business Profile API** - Integration with Google services
- **OpenAI API** - AI-powered content generation

### Frontend
- **React** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **Lucide React** - Icon library
- **Axios** - HTTP client

## Project Structure

```
gmb-automation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── core/                # Configuration, database, security
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic (Google API, AI)
│   │   ├── tasks/               # Celery background tasks
│   │   └── api/v1/endpoints/    # API routes
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main React component
│   │   ├── components/layout/   # Layout components
│   │   ├── pages/               # Page components
│   │   ├── services/api.ts      # API client
│   │   └── hooks/useAuth.ts     # Authentication hook
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Google Cloud Project with Business Profile API enabled
- OpenAI API key

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gmb-automation
   ```

2. **Set up backend environment**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Set up frontend environment**
   ```bash
   cd frontend
   cp .env.example .env
   # Edit .env if needed
   ```

4. **Configure Google Business Profile API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Business Profile API
   - Create OAuth 2.0 credentials
   - Add credentials to backend `.env` file

5. **Configure OpenAI API**
   - Get your API key from [OpenAI](https://platform.openai.com/)
   - Add to backend `.env` file

### Running with Docker (Recommended)

```bash
# Build and start all services
make build
make up

# View logs
make logs

# Stop services
make down
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Running Locally (Development)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Celery Worker:**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Celery Beat (Scheduler):**
```bash
cd backend
celery -A app.tasks.celery_app beat --loglevel=info
```

## Usage

### 1. Register and Login
- Create an account at http://localhost:3000/register
- Login with your credentials

### 2. Connect Google Account
- Navigate to Settings
- Click "Connect Google Account"
- Authorize the application

### 3. Sync Locations
- Go to Locations page
- Click "Sync from Google"
- Your Google Business Profile locations will be imported

### 4. Manage Posts
- Navigate to Posts page
- Create posts manually or use AI generation
- Schedule posts for future publishing
- Publish posts immediately

### 5. Manage Reviews
- Go to Reviews page
- View all reviews across locations
- Reply manually or generate AI responses
- Enable auto-reply for automatic responses

### 6. Enable Automation
- In Locations page, toggle automation settings:
  - **Auto Reply**: Automatically respond to new reviews
  - **Auto Post**: Automatically generate and publish posts

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation powered by Swagger UI.

## Database Migrations

To create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Background Tasks

The application uses Celery for background task processing:

- **Post Publishing**: Scheduled posts are automatically published
- **Review Syncing**: Reviews are periodically synced from Google
- **Auto-Reply**: New reviews receive automatic AI-generated responses
- **AI Content Generation**: Posts are generated asynchronously

## Security Considerations

- Never commit `.env` files to version control
- Use strong passwords and secure API keys
- Enable HTTPS in production
- Regularly update dependencies
- Review Google OAuth scopes and permissions

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file

**Google API errors:**
- Verify OAuth credentials are correct
- Check API is enabled in Google Cloud Console
- Ensure redirect URIs match

**Celery tasks not running:**
- Verify Redis is running
- Check Celery worker logs
- Ensure CELERY_BROKER_URL is correct

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.
