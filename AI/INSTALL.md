# KhojAI Installation Guide

This guide provides step-by-step instructions for setting up and running the KhojAI project.

## Prerequisites

Before installing, ensure you have the following:

1. Python 3.8 or higher
2. Git (for cloning the repository)
3. Internet connection for downloading dependencies

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd KhojAI
```

### 2. Automated Installation (Recommended)

Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

This script will automatically:
- Create a Python virtual environment
- Install all required packages from [requirements.txt](file:///home/daiyaan2002/Desktop/Projects/KhojAI/AI/requirements.txt)
- Download necessary NLTK datasets
- Download the spaCy English language model
- Pull the required Ollama model (if Ollama is installed)

### 3. Manual Installation

If you prefer to install manually, follow these steps:

#### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Download NLTK Data

The project requires several NLTK datasets:

```bash
python3 -c "
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
try:
    nltk.download('punkt_tab')
except:
    pass
"
```

#### Download spaCy Model

```bash
python3 -m spacy download en_core_web_sm
```

### 4. Install System Dependencies

#### Install Ollama

Ollama is required for local LLM inference:

1. Visit [https://ollama.ai/download](https://ollama.ai/download) and download the appropriate version for your OS
2. Install Ollama following the instructions for your platform
3. Pull the required model:

```bash
ollama pull gemma3:1b
ollama pull gemma3:270m
```

#### Google API Credentials

To enable web search functionality, you'll need Google API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Custom Search API
4. Create credentials (API key)
5. Create a [Programmable Search Engine](https://programmablesearchengine.google.com/) and get the Search Engine ID

Add these credentials to your [.env](file:///home/daiyaan2002/Desktop/Projects/KhojAI/AI/.env) file:

```env
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CX=your_search_engine_id_here
MAX_SEARCH_RESULTS=7
```

### 5. Directory Structure

After installation, your project directory should look like this:

```
KhojAI/
├── app.py                 # Main FastAPI application
├── ai_orchestrator.py     # AI orchestration logic
├── web_search.py          # Web search functionality
├── search_utils.py        # Search utilities and ranking
├── prompt_analyzer.py     # Prompt analysis
├── prompt_analyzer_llm.py # LLM-based prompt analysis
├── patterns.py            # Intent patterns
├── scrape_util.py         # Web scraping utilities
├── requirements.txt       # Python dependencies
├── install.sh             # Installation script
├── .env                   # Environment variables
├── cache/                 # Cache directory
│   ├── hot/
│   ├── cold/
│   └── bm25_index/
└── venv/                  # Python virtual environment
```

## Running the Application

### Start the Server

Activate the virtual environment and start the server:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

The application will start on `http://127.0.0.1:8000`.

### Access the API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure you've activated the virtual environment and installed all dependencies.

2. **NLTK Lookup Error**: If you encounter NLTK data errors, manually download the required datasets using the Python command in step 3.

3. **spaCy Model Not Found**: If spaCy reports that the model is not found, reinstall it with:
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Ollama Connection Error**: Ensure the Ollama service is running. On most systems, it starts automatically after installation.

### Verifying Installation

To verify that all components are correctly installed, run the tests:

```bash
source venv/bin/activate
python -m pytest tests.py
```

## Updating the Application

To update the application:

1. Pull the latest changes from the repository
2. Activate the virtual environment
3. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. Update NLTK data if needed
5. Restart the application

## Additional Notes

- The application uses a disk-based caching system located in the `cache/` directory
- Models and data are automatically downloaded on first use
- The application requires approximately 2-4GB of RAM for optimal operation