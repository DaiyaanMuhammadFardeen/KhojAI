"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Plus, Menu } from "lucide-react";
import styles from "@/styles/components/chat-interface.module.scss";
import ChatMessage from "./chat-message";
import SearchProgress from "./search-progress";
import { MessageAPI, AIApi, ConversationAPI } from "../app/api/chat/route";
import { CreateMessageRequest, MessageDTO } from "../types";

interface ChatInterfaceProps {
  chatId: string | null;
  onMenuClick: () => void;
}

function ChatInterface({ chatId, onMenuClick }: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState<MessageDTO[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamData, setStreamData] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const streamingMessageIdRef = useRef<string | null>(null);
  const finalResponseRef = useRef<string>("");

  useEffect(() => {
    const loadMessages = async () => {
      if (!chatId) {
        setMessages([]);
        return;
      }

      try {
        const response = await ConversationAPI.get(chatId);
        setMessages(response.data.messages || []);
      } catch (error) {
        console.error("Failed to load messages:", error);
        setMessages([]);
      }
    };

    loadMessages();
  }, [chatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamData]);

  const handleSend = async () => {
    if (!inputValue.trim() || !chatId || isLoading) return;

    const userPrompt = inputValue.trim();
    setInputValue("");
    setIsLoading(true);
    finalResponseRef.current = ""; // Reset final response
    
    // Add user message
    const userMessage: MessageDTO = {
      id: `user-${Date.now()}`,
      role: "USER",
      content: userPrompt,
      sentAt: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Save user message to backend (async, don't block)
    const userMessageRequest: CreateMessageRequest = {
      convId: chatId,
      role: 'USER',
      content: userPrompt
    };
    
    MessageAPI.create(userMessageRequest)
      .then(response => {
        const savedMessage = response.data.messages[response.data.messages.length - 1];
        setMessages(prev => 
          prev.map(msg => 
            msg.id === userMessage.id ? { ...msg, id: savedMessage.id } : msg
          )
        );
      })
      .catch(error => console.error("Failed to save user message:", error));
    
    // Create AI message placeholder
    const aiMessageId = `ai-${Date.now()}`;
    streamingMessageIdRef.current = aiMessageId;
    
    const aiMessage: MessageDTO = {
      id: aiMessageId,
      role: "AI",
      content: " Initializing search...",
      sentAt: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, aiMessage]);
    setStreamData([]); // Reset stream data

    try {
      await AIApi.streamSearch(
        { prompt: userPrompt },
        (parsed) => {
          // Add to stream data for progress component
          setStreamData(prev => [...prev, parsed]);
          
          // Update AI message based on event type
          let statusMessage = "";
          
          switch (parsed.type) {
            case 'analysis':
              statusMessage = parsed.status === 'started' 
                ? " Analyzing your query..." 
                : " Analysis complete";
              break;
              
            case 'search':
              if (parsed.status === 'started') {
                statusMessage = ` Searching the web for "${parsed.query}"...`;
              } else if (parsed.status === 'completed') {
                statusMessage = ` Found ${parsed.results_count} results for "${parsed.query}"`;
              }
              break;
              
            case 'urls_found':
              statusMessage = ` Found ${parsed.count} URLs for query: "${parsed.query}"`;
              break;
              
            case 'scraping':
              if (parsed.status === 'started') {
                statusMessage = ` Scraping: ${parsed.url}`;
              } else if (parsed.status === 'completed') {
                statusMessage = ` Scraped: ${parsed.title}`;
              }
              break;
              
            case 'scraping_error':
              statusMessage = ` Error scraping: ${parsed.url} - ${parsed.error}`;
              break;
              
            case 'extracting':
              if (parsed.status === 'started') {
                statusMessage = ` Extracting relevant information from: ${parsed.url}`;
              } else if (parsed.status === 'completed') {
                statusMessage = ` Extracted ${parsed.sentences_count} relevant sentences`;
              }
              break;
              
            case 'search_result':
              statusMessage = ` Processed result: ${parsed.title}`;
              break;
              
            case 'deduplication':
              statusMessage = ` Removed ${parsed.original_count - parsed.final_count} duplicate results`;
              break;
              
            case 'response_generation':
              if (parsed.status === 'started') {
                statusMessage = " Generating response...";
              } else if (parsed.status === 'completed') {
                statusMessage = " Response generated";
              }
              break;
              
            case 'skip_search':
              statusMessage = ` Skipping search: ${parsed.reason}`;
              break;
              
            case 'final_response':
              finalResponseRef.current = parsed.message;
              statusMessage = parsed.message;
              break;
              
            case 'done':
              // Stream complete - this is handled by the onComplete callback
              return;
              
            case 'error':
              statusMessage = ` Error: ${parsed.message || 'Unknown error'}`;
              break;
              
            default:
              console.log("Unknown event type:", parsed.type);
              return;
          }
          
          // Only update the message if we haven't received the final response yet
          if (parsed.type !== 'final_response' && finalResponseRef.current === "") {
            // Update the AI message with the latest status
            setMessages(prev => 
              prev.map(msg => 
                msg.id === streamingMessageIdRef.current 
                  ? { ...msg, content: statusMessage } 
                  : msg
              )
            );
          }
        },
        () => {
          // onComplete callback
          console.log("Stream completed successfully");
          
          // Save final AI message to backend
          if (finalResponseRef.current && chatId) {
            const aiMessageRequest: CreateMessageRequest = {
              convId: chatId,
              role: 'AI',
              content: finalResponseRef.current
            };
            
            MessageAPI.create(aiMessageRequest)
              .then(response => {
                const savedMessage = response.data.messages[response.data.messages.length - 1];
                setMessages(prev => 
                  prev.map(msg => 
                    msg.id === streamingMessageIdRef.current 
                      ? { ...msg, id: savedMessage.id, content: finalResponseRef.current } 
                      : msg
                  )
                );
              })
              .catch(error => console.error("Failed to save AI message:", error));
          }
          
          streamingMessageIdRef.current = null;
          setIsLoading(false);
        },
        (error) => {
          // onError callback
          console.error("Streaming error:", error);
          setMessages(prev => 
            prev.map(msg => 
              msg.id === streamingMessageIdRef.current 
                ? { ...msg, content: ` Error: ${error.message || 'Connection failed'}` } 
                : msg
            )
          );
          streamingMessageIdRef.current = null;
          setIsLoading(false);
        }
      );
    } catch (error) {
      console.error("Failed to send message:", error);
      setMessages(prev => 
        prev.map(msg => 
          msg.id === streamingMessageIdRef.current 
            ? { ...msg, content: ` Error: ${error instanceof Error ? error.message : 'Unknown error'}` } 
            : msg
        )
      );
      streamingMessageIdRef.current = null;
      setIsLoading(false);
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  if (!chatId) {
    return (
      <div className={styles.emptyChatContainer}>
        <div className={styles.emptyChatContent}>
          <Plus size={48} className={styles.emptyChatIcon} />
          <h2 className={styles.emptyChatTitle}>No Chat Selected</h2>
          <p className={styles.emptyChatDescription}>
            Select an existing chat from the sidebar or create a new one to get started.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.menuButton}
          onClick={onMenuClick}
        >
          <Menu size={20} />
        </button>
        <h1 className={styles.title}>KhojAI Chat</h1>
      </div>

      <div className={styles.messagesContainer}>
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            role={message.role}
            content={message.content}
            timestamp={message.sentAt}
          />
        ))}
        {isLoading && streamData.length > 0 && (
          <SearchProgress streamData={streamData} />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputContainer}>
        <div className={styles.inputWrapper}>
          <textarea
            className={styles.input}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            disabled={isLoading}
            rows={1}
          />
          <button
            className={styles.sendButton}
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface;