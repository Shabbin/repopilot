# RepoPilot 

An AI-powered software engineering assistant that allows you to import GitHub repositories and ask intelligent, code-aware questions. RepoPilot leverages semantic search to retrieve relevant code snippets and provides contextual answers about your codebase.

## Overview

RepoPilot is a full-stack application that bridges the gap between developers and their codebases. Instead of manually searching through code, you can ask questions about how your repository works, and the system will retrieve the relevant code chunks to provide grounded, accurate answers.

### Key Features

- **Repository Import**: Seamlessly import any public GitHub repository into RepoPilot
- **Code Chunking**: Automatically split imported repositories into manageable, searchable code chunks
- **Repository-Aware Q&A**: Ask technical questions and get answers backed by actual code from your repository
- **Retrieved Context**: View the exact code snippets that informed each answer, with line numbers and file paths
- **Code-Only Search**: Filter results to focus on implementation code rather than documentation
- **Semantic Search**: Find relevant code snippets based on meaning and intent, not just exact keywords

## Tech Stack

### Frontend
- **Next.js 16.2.3** - Modern React framework with TypeScript
- **React 19** - UI library
- **Tailwind CSS 4** - Utility-first CSS framework
- **TypeScript 5** - Type-safe JavaScript
- **Axios** - HTTP client for API communication
- **ESLint** - Code quality and style

### Backend
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy** - SQL toolkit and ORM for database operations
- **PostgreSQL 16** - Primary database (via Docker)
- **Pydantic** - Data validation and settings management
- **GitPython** - Clone and manage Git repositories
- **Alembic** - Database migrations
- **Uvicorn** - ASGI server

### DevOps
- **Docker** - Containerization (database service)
- **Docker Compose** - Multi-container orchestration

## Project Structure

```
repopilot/
├── frontend/                    # Next.js React application
│   ├── app/                    # Next.js App Router
│   │   └── page.tsx           # Main UI component
│   ├── package.json           # Frontend dependencies
│   ├── next.config.ts         # Next.js configuration
│   ├── tailwind.config.ts     # Tailwind CSS config
│   └── tsconfig.json          # TypeScript configuration
├── backend/                     # FastAPI Python backend
│   ├── main.py               # FastAPI application entry point
│   ├── requirements.txt       # Python dependencies
│   ├── models/               # Database models
│   ├── routes/               # API endpoints
│   ├── services/             # Business logic
│   └── schemas/              # Pydantic request/response models
├── docker-compose.yml          # Docker services configuration
└── README.md                   # This file
```

## Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend development)
- **Python** 3.10+ (for backend development)
- **Docker & Docker Compose** (for PostgreSQL database)

### Installation & Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Shabbin/repopilot.git
cd repopilot
```

#### 2. Start the Database

```bash
docker-compose up -d
```

This starts a PostgreSQL database on port 5433 with credentials:
- **User**: `repopilot`
- **Password**: `repopilot`
- **Database**: `repopilot`

#### 3. Set Up the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```env
DATABASE_URL=postgresql://repopilot:repopilot@localhost:5433/repopilot
```

Run database migrations:

```bash
alembic upgrade head
```

Start the FastAPI server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at `http://localhost:8000`

#### 4. Set Up the Frontend

```bash
cd frontend
npm install
```

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

### Importing a Repository

1. Navigate to `http://localhost:3000`
2. In the **"Import repository"** panel on the left:
   - Enter a repository name (e.g., "fastapi-sample")
   - Paste the GitHub URL (e.g., `https://github.com/tiangolo/fastapi.git`)
   - Click **"Import Repository"**
3. The system will clone the repository, chunk the code, and add it to the database

### Asking Questions

1. Select an imported repository from the dropdown
2. Type your technical question in the text area (e.g., "How does FastAPI include routers?")
3. Click **"Ask RepoPilot"**
4. View the AI-generated answer in the **"Answer"** section
5. Inspect the **"Retrieved Context"** panel to see the actual code chunks that informed the answer

### Query Options

When asking questions, the frontend sends these parameters:

- **`limit: 3`** - Retrieves up to 3 most relevant code chunks
- **`code_only: true`** - Excludes comments and documentation
- **`exclude_docs: true`** - Filters out documentation files
- **`exclude_examples: true`** - Excludes example files

## API Endpoints

### Repositories

- `GET /repositories/` - List all imported repositories
- `POST /repositories/` - Import a new repository
- `POST /repositories/{id}/ingest-chunks` - Parse and chunk repository code
- `POST /repositories/{id}/ask` - Ask a question about a repository

## Development

### Frontend Development

```bash
cd frontend
npm run dev      # Start development server
npm run build    # Build for production
npm run lint     # Run ESLint
```

### Backend Development

```bash
cd backend
uvicorn main:app --reload  # Start with auto-reload
```

### Database Management

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Revert migrations
alembic downgrade -1
```

## Architecture

### Data Flow

1. **Import**: User provides GitHub URL → Backend clones repo → Code is parsed into chunks
2. **Storage**: Code chunks stored in PostgreSQL with metadata (file path, line numbers, file type)
3. **Query**: User asks question → Backend performs semantic search on chunks
4. **Retrieval**: System returns most relevant chunks with LLM-generated answer
5. **Display**: Frontend shows answer and retrieved code context with visual highlights

### Key Components

**Frontend (`page.tsx`)**
- Repository management UI
- Question input interface
- Real-time response display
- Code chunk viewer with syntax context

**Backend (`main.py`)**
- Repository ingestion pipeline
- Code chunking and vectorization
- Semantic search engine
- Q&A generation with context retrieval

**Database**
- Repositories table (repo metadata)
- CodeChunks table (indexed for fast semantic search)
- User sessions and queries

## Environment Variables

### Frontend (`.env.local`)

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000  # Backend API URL
```

### Backend (`.env`)

```env
DATABASE_URL=postgresql://user:password@host:port/database
GITHUB_TOKEN=optional-for-private-repos  # Optional GitHub token
```

## Production Deployment

### Frontend
- Build: `npm run build`
- Deploy to Vercel, Netlify, or any static host

### Backend
- Use production ASGI server: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
- Set appropriate database connection string
- Configure CORS for your domain

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Backend Connection Issues

**Error**: "Failed to load repositories. Make sure the backend is running."

- Verify the backend is running on `http://127.0.0.1:8000`
- Check `NEXT_PUBLIC_API_BASE_URL` in frontend `.env.local`
- Ensure no firewall blocks the connection

### Database Connection Issues

**Error**: "Connection refused" in backend logs

- Verify PostgreSQL container is running: `docker ps`
- Check credentials in `.env` match docker-compose.yml
- Ensure port 5433 is not in use

### Slow Code Ingestion

- Large repositories may take time to process
- Monitor backend logs for progress
- Consider chunking strategy for very large codebases

## Performance Tips

- Use `code_only: true` to reduce noise in results
- Adjust `limit` parameter based on performance needs
- Run database indexing for large code datasets

## Future Enhancements

- [ ] Support for private GitHub repositories with token authentication
- [ ] Multiple embedding models for semantic search
- [ ] Repository comparison and similarity analysis
- [ ] Code review assistance
- [ ] Testing strategy suggestions
- [ ] Documentation generation
- [ ] Multi-language support improvement

## License

This project is open source. Check the repository for license details.

## Support

For issues, questions, or feature requests, please open a [GitHub Issue](https://github.com/Shabbin/repopilot/issues).

---

**Built with ❤️ by [Shabbin](https://github.com/Shabbin)**
