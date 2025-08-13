# pizza_qa

## Running with Docker

This project includes a Docker setup for local development using Python 3.11 and Django. The default configuration runs the Django development server on port 8000.

### Build and Run

Use Docker Compose to build and start the application:

```sh
docker compose up --build
```

- The app will be available at [http://localhost:8000](http://localhost:8000).
- The container exposes port `8000`.

### Project-specific Details

- **Python version:** 3.11 (as specified in the Dockerfile)
- **Dependencies:** Installed from `requirements.txt` inside a virtual environment (`.venv`)
- **User:** Runs as a non-root user (`appuser`) for security
- **No database or cache service is included by default** in the compose file. If you need a database, add it to `docker-compose.yml` and update `depends_on` accordingly.
- **Environment variables:** No required environment variables are set by default. If you need to add any, uncomment and use the `env_file` section in the compose file.

### Notes

- Static files are not collected automatically. For production, ensure you handle static/media files appropriately.
- The default command runs the Django development server. For production, use a proper WSGI server (e.g., Gunicorn) and configure static/media file serving.
