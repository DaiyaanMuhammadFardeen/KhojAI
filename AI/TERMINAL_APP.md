# KhojAI Terminal Application

This is a terminal-based application that provides a beautiful, real-time streaming interface for the KhojAI AI assistant.

## Features

- Real-time streaming of AI responses token-by-token
- Visual display of prompt analysis (intents, keywords)
- Live updates of web search progress
- Colorful ncurses-based UI
- Continuous chat-like interaction

## How to Run

To run the terminal application:

```bash
python terminal_app.py
```

## Controls

- Type your question in the input box at the bottom
- Press Enter to submit your question
- Press Esc to exit the application

## UI Layout

The interface is divided into several sections:

1. **Title Bar** - Application title and description
2. **Status** - Current application status (ready/generating)
3. **Prompt Analysis** - Identified intents and keywords from your prompt
4. **Search Queries** - Web search queries being executed
5. **AI Response** - Main area showing the AI's response as it's generated
6. **Input** - Where you type your questions

## How It Works

The terminal application uses the same AI orchestration engine as the web API, but presents the information in a real-time, terminal-friendly format. As the AI processes your query:

1. First, it analyzes your prompt to identify intents and extract keywords
2. Then, it generates search queries and performs web searches
3. Finally, it generates a coherent response based on the search results

Each step is displayed in real-time in the terminal interface, giving you insight into the AI's thought process.