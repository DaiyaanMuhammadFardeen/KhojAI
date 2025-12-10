#!/usr/bin/env python3

import curses
import asyncio
import json
import os
from ai_orchestrator import generate_response_with_web_search_stream
from prompt_analyzer import analyze_prompt_async, get_spacy_pipeline, get_kw_extractor

# Set environment variable to prevent tokenizer parallelism issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class TerminalApp:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.setup_colors()
        
        # Preload all models
        self.preload_models()
        
        # Get screen dimensions
        self.height, self.width = stdscr.getmaxyx()
        
        # Setup windows
        self.setup_windows()
        
        # State tracking
        self.current_prompt = ""
        self.search_queries = []
        self.intents = []
        self.keywords = []
        self.response_buffer = ""  # Buffer for accumulating tokens
        self.response_lines = []
        self.is_generating = False
        self.search_progress = ""  # Track search progress
        self.search_results = []   # Store search results with URLs
        self.response_scroll_pos = 0  # Track scrolling position
        
    def preload_models(self):
        """Preload all models to avoid loading delays during prompt processing"""
        try:
            # Preload spaCy and YAKE models
            get_spacy_pipeline()
            get_kw_extractor()
            
            # Models are loaded automatically when imported
            # KeyBERT and other models will be loaded on first use
        except Exception as e:
            pass  # Models will be loaded on demand if needed
            
    def setup_colors(self):
        """Initialize color pairs for UI elements"""
        curses.start_color()
        curses.use_default_colors()
        
        # Define color pairs
        curses.init_pair(1, curses.COLOR_CYAN, -1)    # Headers
        curses.init_pair(2, curses.COLOR_GREEN, -1)   # Success messages
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Warnings
        curses.init_pair(4, curses.COLOR_RED, -1)     # Errors
        curses.init_pair(5, curses.COLOR_BLUE, -1)    # Info
        curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Prompts
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN) # Title bar (black text on green background)
        curses.init_pair(8, curses.COLOR_WHITE, -1)   # Default text
        curses.init_pair(9, curses.COLOR_CYAN, -1)    # Search information
        curses.init_pair(10, curses.COLOR_YELLOW, -1) # Response generation messages
        curses.init_pair(11, curses.COLOR_GREEN, -1)  # Actual AI response
        
    def setup_windows(self):
        """Setup the different sections of the UI"""
        # Title window (top)
        self.title_win = curses.newwin(3, self.width, 0, 0)
        
        # Status window (below title)
        self.status_win = curses.newwin(3, self.width, 3, 0)
        
        # Analysis window (below status)
        self.analysis_win = curses.newwin(6, self.width, 6, 0)
        
        # Search window (below analysis)
        self.search_win = curses.newwin(8, self.width, 12, 0)
        
        # Response window (main area) - now takes full width
        response_height = self.height - 24
        self.response_win = curses.newwin(response_height, self.width, 20, 0)
        
        # Input window (bottom)
        self.input_win = curses.newwin(4, self.width, self.height - 4, 0)
        
        # Enable scrolling for response window
        self.response_win.scrollok(True)
        self.response_win.idlok(True)
        self.response_win.keypad(True)  # Enable arrow keys
        
    def draw_title(self):
        """Draw the application title"""
        self.title_win.clear()
        self.title_win.bkgd(' ', curses.color_pair(7) | curses.A_BOLD)
        
        title = "KhojAI Terminal Interface"
        subtitle = "Real-time AI Assistant with Web Search"
        
        self.title_win.addstr(0, (self.width - len(title)) // 2, title)
        self.title_win.addstr(1, (self.width - len(subtitle)) // 2, subtitle)
        self.title_win.refresh()
        
    def draw_status(self):
        """Draw the status section"""
        self.status_win.clear()
        self.status_win.box()
        self.status_win.addstr(0, 2, " Status ", curses.A_BOLD | curses.color_pair(1))
        
        if self.is_generating:
            status_text = "Generating response..."
            self.status_win.addstr(1, 2, status_text, curses.color_pair(3))
        else:
            status_text = "Ready for input. Type your question below."
            self.status_win.addstr(1, 2, status_text, curses.color_pair(2))
            
        self.status_win.refresh()
        
    def draw_analysis(self):
        """Draw the prompt analysis section"""
        self.analysis_win.clear()
        self.analysis_win.box()
        self.analysis_win.addstr(0, 2, " Prompt Analysis ", curses.A_BOLD | curses.color_pair(1))
        
        if self.intents:
            intents_str = ", ".join(self.intents)
            self.analysis_win.addstr(1, 2, f"Intents: {intents_str}", curses.color_pair(5))
        
        if self.keywords:
            keywords_str = ", ".join([kw['term'] for kw in self.keywords[:5]])
            self.analysis_win.addstr(2, 2, f"Keywords: {keywords_str}", curses.color_pair(5))
            
        self.analysis_win.refresh()
        
    def draw_search(self):
        """Draw the search section"""
        self.search_win.clear()
        self.search_win.box()
        self.search_win.addstr(0, 2, " Search Progress ", curses.A_BOLD | curses.color_pair(1))
        
        if self.search_progress:
            # Show live search progress
            self.search_win.addstr(1, 2, self.search_progress, curses.color_pair(3))
        elif self.search_results:
            # Show search results with URLs
            self.search_win.addstr(1, 2, f"Found {len(self.search_results)} sources:", curses.color_pair(2))
            for i, result in enumerate(self.search_results[:4]):  # Show up to 4 results
                try:
                    url_display = result['url'][:self.width-10]  # Truncate URL to fit window
                    self.search_win.addstr(i+2, 2, f"• {url_display}", curses.color_pair(5))
                except curses.error:
                    break
        elif self.search_queries:
            for i, query in enumerate(self.search_queries[:3]):
                self.search_win.addstr(i+1, 2, f"• {query}", curses.color_pair(5))
        else:
            self.search_win.addstr(1, 2, "No search queries generated", curses.color_pair(3))
            
        self.search_win.refresh()
        
    def draw_response(self):
        """Draw the AI response section with full terminal width"""
        self.response_win.clear()
        self.response_win.box()
        self.response_win.addstr(0, 2, " AI Response ", curses.A_BOLD | curses.color_pair(1))
        
        # Calculate available space for content
        max_y, max_x = self.response_win.getmaxyx()
        content_height = max_y - 2  # Subtract 2 for border lines
        content_width = max_x - 4    # Subtract 4 for borders and padding
        
        # Display response lines with color coding and full width usage
        start_idx = max(0, len(self.response_lines) - content_height - self.response_scroll_pos)
        end_idx = min(start_idx + content_height, len(self.response_lines))
        
        visible_lines = self.response_lines[start_idx:end_idx]
        
        for i, line in enumerate(visible_lines):
            try:
                # Apply color based on line content
                if line.startswith("[SEARCH]"):
                    color = curses.color_pair(9)  # Cyan for search info
                elif line.startswith("[RESPONSE]"):
                    color = curses.color_pair(10)  # Yellow for response generation messages
                elif line.startswith("[ERROR]"):
                    color = curses.color_pair(4)  # Red for errors
                elif line.startswith("> "):  # User prompts
                    color = curses.color_pair(6)  # Magenta for user prompts
                else:
                    color = curses.color_pair(11)  # Green for actual AI response
                    
                # Use full width for content, wrapping or truncating as needed
                # Fill the entire width with the line content
                if len(line) <= content_width:
                    # Line fits within content area
                    self.response_win.addstr(i+1, 2, line)
                    # Fill remaining space with spaces to ensure full width coloring
                    remaining_spaces = content_width - len(line)
                    if remaining_spaces > 0:
                        self.response_win.addstr(i+1, 2 + len(line), " " * remaining_spaces, color)
                else:
                    # Line is longer than content area, truncate and show as much as possible
                    truncated_line = line[:content_width]
                    self.response_win.addstr(i+1, 2, truncated_line, color)
                    
            except curses.error:
                # Handle case where we try to write beyond window
                break
                
        self.response_win.refresh()
        
    def draw_input(self):
        """Draw the input section"""
        self.input_win.clear()
        self.input_win.box()
        self.input_win.addstr(0, 2, " Your Question ", curses.A_BOLD | curses.color_pair(1))
        
        # Show current input
        input_text = f"> {self.current_prompt}"
        max_x = self.input_win.getmaxyx()[1]
        if len(input_text) > max_x - 4:
            # Truncate input to fit window
            display_text = input_text[:max_x-7] + "..."
        else:
            display_text = input_text
            
        self.input_win.addstr(1, 2, display_text)
        
        # Position cursor
        cursor_x = min(len(input_text) + 2, max_x - 2)
        self.input_win.move(1, cursor_x)
        self.input_win.refresh()
        
    def update_display(self):
        """Redraw all sections of the UI"""
        self.draw_title()
        self.draw_status()
        self.draw_analysis()
        self.draw_search()
        self.draw_response()
        self.draw_input()
        
    def update_analysis(self, intents, keywords):
        """Update the analysis section"""
        self.intents = intents
        self.keywords = keywords
        self.draw_analysis()
        
    def update_search_queries(self, queries):
        """Update the search queries section"""
        self.search_queries = queries
        self.search_progress = ""
        self.draw_search()
        
    def update_search_progress(self, progress_text):
        """Update search progress in real-time"""
        self.search_progress = progress_text
        self.draw_search()
        
    def update_search_results(self, results):
        """Update search results with URLs"""
        self.search_results = results
        self.search_progress = ""
        self.draw_search()
        
    def add_response_chunk(self, chunk):
        """Add a chunk of response text"""
        # Accumulate tokens in buffer
        self.response_buffer += chunk
        
        # Process complete lines
        while '\n' in self.response_buffer:
            line, self.response_buffer = self.response_buffer.split('\n', 1)
            if line.strip():  # Only add non-empty lines
                self.response_lines.append(line)
        
        # Add any remaining text as a line if we have significant content
        if self.response_buffer and (self.response_buffer.endswith(('.', '!', '?')) or len(self.response_buffer) > 50):
            if self.response_buffer.strip():
                self.response_lines.append(self.response_buffer)
            self.response_buffer = ""
            
        self.draw_response()
        
    def flush_response_buffer(self):
        """Flush any remaining text in the response buffer"""
        if self.response_buffer.strip():
            self.response_lines.append(self.response_buffer)
        self.response_buffer = ""
        self.draw_response()
        
    def clear_previous_outputs(self):
        """Clear previous search and response outputs"""
        self.response_lines = []
        self.response_scroll_pos = 0
        self.search_results = []
        self.search_queries = []
        self.search_progress = ""
        self.intents = []
        self.keywords = []
        self.draw_response()
        self.draw_search()
        self.draw_analysis()
        
    def scroll_response(self, direction):
        """Scroll the response window"""
        if direction == "up" and self.response_scroll_pos > 0:
            self.response_scroll_pos -= 1
            self.draw_response()
        elif direction == "down":
            # Allow scrolling down if there's more content
            max_y = self.response_win.getmaxyx()[0]
            content_height = max_y - 2
            if len(self.response_lines) > content_height + self.response_scroll_pos:
                self.response_scroll_pos += 1
                self.draw_response()
        
    async def process_prompt(self, prompt):
        """Process the user prompt and stream the response"""
        self.is_generating = True
        self.update_display()
        
        try:
            # Generate response with streaming
            async for chunk in generate_response_with_web_search_stream(prompt, raw_stream=True):
                # Process streaming chunks
                if chunk.startswith("[ANALYSIS]"):
                    # Parse analysis data
                    if "Intents:" in chunk:
                        intents_str = chunk.split("Intents:")[1].strip().strip('[]')
                        intents = [intent.strip().strip("'") for intent in intents_str.split(",") if intent.strip()]
                        self.update_analysis(intents, self.keywords)
                    elif "Keywords:" in chunk:
                        keywords_str = chunk.split("Keywords:")[1].strip().strip('[]')
                        keywords = [{"term": kw.strip().strip("'")} for kw in keywords_str.split(",") if kw.strip()]
                        self.update_analysis(self.intents, keywords)
                    elif "Search Queries:" in chunk:
                        queries_str = chunk.split("Search Queries:")[1].strip().strip('[]')
                        queries = [q.strip().strip("'") for q in queries_str.split(",") if q.strip()]
                        self.update_search_queries(queries)
                elif chunk.startswith("[SEARCH]"):
                    # Live search updates
                    if "Found information from" in chunk:
                        # Extract number of sources
                        self.update_search_progress(chunk[9:].strip())  # Remove "[SEARCH] " prefix
                    elif "Query" in chunk and "/" in chunk:
                        # Show current query progress
                        self.update_search_progress(chunk[9:].strip())  # Remove "[SEARCH] " prefix
                    else:
                        self.update_search_progress(chunk[9:].strip())  # Remove "[SEARCH] " prefix
                    self.add_response_chunk(chunk)
                elif chunk.startswith("[RESPONSE]"):
                    # Response generation updates
                    self.add_response_chunk(chunk)
                elif chunk.startswith("[ERROR]"):
                    # Error messages
                    self.add_response_chunk(chunk)
                else:
                    # Regular response text (LLM output)
                    self.add_response_chunk(chunk)
                    
        except Exception as e:
            self.add_response_chunk(f"[ERROR] Processing prompt: {str(e)}")
        finally:
            # Flush any remaining text in buffer
            self.flush_response_buffer()
            self.is_generating = False
            self.search_progress = ""
            self.draw_status()
            self.draw_search()
            
    def handle_input(self, key):
        """Handle user input"""
        # Handle scrolling keys
        if key == curses.KEY_UP:
            self.scroll_response("up")
            return True
        elif key == curses.KEY_DOWN:
            self.scroll_response("down")
            return True
            
        if key == 27:  # ESC key
            return False
        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
            # Backspace
            self.current_prompt = self.current_prompt[:-1]
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            # Enter key - submit prompt
            if self.current_prompt.strip() and not self.is_generating:
                # Clear previous outputs
                self.clear_previous_outputs()
                
                # Add user prompt to response
                self.response_lines.append(f"> {self.current_prompt}")
                prompt = self.current_prompt
                self.current_prompt = ""
                
                # Process in background
                asyncio.create_task(self.process_prompt(prompt))
        elif 32 <= key <= 126:  # Printable ASCII characters
            # Add character to prompt
            self.current_prompt += chr(key)
            
        return True
        
    async def run(self):
        """Main application loop"""
        # Show loading message during startup
        self.stdscr.clear()
        self.stdscr.addstr(0, 0, "Loading models, please wait...")
        self.stdscr.refresh()
        
        # Preload models
        self.preload_models()
        
        # Setup UI
        self.update_display()
        
        while True:
            key = self.stdscr.getch()
            if not self.handle_input(key):
                break
                
            self.draw_input()
            
            # Small delay to prevent high CPU usage
            await asyncio.sleep(0.01)

def main(stdscr):
    """Main entry point"""
    # Clear screen
    stdscr.clear()
    curses.curs_set(1)  # Show cursor
    stdscr.nodelay(True)  # Non-blocking input
    
    # Create and run app
    app = TerminalApp(stdscr)
    
    # Run the asyncio event loop
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    curses.wrapper(main)