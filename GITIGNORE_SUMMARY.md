# .gitignore Configuration Summary

This document outlines what files and directories are ignored by git in this Audio Transcription Service project.

## 🔒 Environment & Security Files

- `.env` - Environment variables with secrets
- `.env.local`, `.env.*.local` - Local environment overrides
- `*.pem`, `*.key`, `*.crt`, `*.cert` - Certificate files

## 🐍 Backend (Python/FastAPI) Ignored Files

### Python Runtime Files
- `__pycache__/` - Python bytecode cache
- `*.py[cod]` - Compiled Python files
- `*.so` - Shared object files
- `.Python` - Python interpreter files

### Virtual Environments
- `venv/`, `env/`, `ENV/` - Virtual environment directories
- `backend/venv/`, `backend/env/` - Backend-specific virtual environments

### Testing & Coverage
- `.pytest_cache/` - Pytest cache
- `.coverage` - Coverage data
- `htmlcov/` - HTML coverage reports
- `backend/test.db` - Test database files

### Build & Distribution
- `build/`, `dist/` - Build artifacts
- `*.egg-info/` - Package metadata
- `wheels/` - Python wheel files

### Database Files
- `*.db`, `*.sqlite`, `*.sqlite3` - Database files
- `backend/*.db` - Backend database files

### Audio Files
- `audio_storage/` - Audio storage directory
- `*.wav`, `*.mp3`, `*.m4a`, `*.ogg`, `*.flac` - Audio files

## ⚛️ Frontend (React/Node.js) Ignored Files

### Dependencies
- `node_modules/` - Node.js dependencies
- `frontend/node_modules/` - Frontend-specific dependencies

### Build Artifacts
- `frontend/build/` - React production build
- `frontend/dist/` - Distribution files
- `.eslintcache` - ESLint cache

### Testing & Coverage
- `frontend/coverage/` - Test coverage reports
- `.nyc_output` - NYC test coverage

### Logs
- `npm-debug.log*` - NPM debug logs
- `yarn-debug.log*` - Yarn debug logs
- `yarn-error.log*` - Yarn error logs

### Package Manager Files
- `.yarn-integrity` - Yarn integrity file
- `.yarn/cache` - Yarn v2 cache
- `.pnp.*` - Yarn PnP files

## 🐳 Docker & Infrastructure

- `.dockerignore` - Docker ignore file
- `docker-compose.override.yml` - Docker compose overrides
- `docker-compose.local.yml` - Local development overrides

## 💻 IDE & Editor Files

- `.vscode/` - VS Code settings
- `.idea/` - IntelliJ/PyCharm settings
- `*.swp`, `*.swo` - Vim swap files
- `.DS_Store` - macOS Finder files
- `Thumbs.db` - Windows thumbnail cache

## 📝 Logs & Temporary Files

- `logs/`, `*.log` - Log files
- `*.tmp`, `*.temp` - Temporary files
- `*~` - Editor backup files
- `*.pid` - Process ID files

## ✅ What IS Tracked

### Source Code
- All `.py` files (Python source)
- All `.js`, `.jsx` files (JavaScript/React source)
- All `.css` files (Stylesheets)
- All `.html` files (Templates)

### Configuration
- `package.json`, `package-lock.json` - Node.js dependencies
- `requirements.txt` - Python dependencies
- `Dockerfile`, `docker-compose.yml` - Docker configuration
- `.env.example` - Environment template
- `pytest.ini` - Test configuration

### Documentation
- `README.md` - Project documentation
- All `.md` files - Markdown documentation

### Scripts
- All files in `scripts/` directory
- Shell scripts (`.sh` files)

## 🔍 Verification

To verify the .gitignore is working correctly:

```bash
# Check git status (should not show ignored files)
git status

# Test with temporary files
mkdir -p backend/__pycache__ frontend/build
touch backend/test.db frontend/build/index.html
git status  # Should not show these files
rm -rf backend/__pycache__ backend/test.db frontend/build
```

## 📁 .gitignore Files Structure

- **Root `.gitignore`** - Main ignore file for the entire project
- **`backend/.gitignore`** - Backend-specific ignore rules
- **`frontend/.gitignore`** - Frontend-specific ignore rules

This multi-level approach ensures comprehensive coverage while keeping each .gitignore file focused on its specific domain.
