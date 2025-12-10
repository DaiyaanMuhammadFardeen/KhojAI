"use client";

import { useState, useEffect, useRef } from "react";
import { Loader2, Search, FileText, Globe, Download, FileSearch } from "lucide-react";
import styles from '@/styles/components/search-progress.module.scss';

interface StreamEvent {
  type: string;
  status?: string;
  query?: string;
  url?: string;
  title?: string;
  message?: string;
  search_queries?: string[];
  results_count?: number;
  count?: number;
  sentences_count?: number;
  original_count?: number;
  final_count?: number;
  error?: string;
  reason?: string;
}

interface SearchProgressProps {
  streamData: StreamEvent[];  // This array grows over time
}

export default function SearchProgress({ streamData }: SearchProgressProps) {
  const [currentStatus, setCurrentStatus] = useState<string>("Initializing...");
  const [searchQueries, setSearchQueries] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<Array<{url: string, title: string, sentences_count: number}>>([]);
  const [scrapingStatus, setScrapingStatus] = useState<Array<{url: string, status: 'started' | 'completed' | 'error', title?: string}>>([]);
  const [isComplete, setIsComplete] = useState<boolean>(false);

  // Track which events we've already processed
  const processedCount = useRef(0);

  useEffect(() => {
    if (streamData.length === 0) return;

    // Process only the NEW events since last render
    const newEvents = streamData.slice(processedCount.current);
    processedCount.current = streamData.length;

    newEvents.forEach(event => {
      console.log("Processing event:", event); // You’ll see ALL of them now!

      switch (event.type) {
        case 'analysis':
          if (event.status === 'started') {
            setCurrentStatus(`Analyzing prompt...`);
          } else if (event.status === 'completed') {
            setCurrentStatus('Analysis complete');
            if (event.search_queries) {
              setSearchQueries(event.search_queries);
            }
          }
          break;

        case 'search':
          if (event.status === 'started') {
            setCurrentStatus(`Searching: "${event.query}"`);
          } else if (event.status === 'completed') {
            setCurrentStatus(`Found ${event.results_count} results`);
          }
          break;

        case 'urls_found':
          setCurrentStatus(`Found ${event.count} URLs`);
          break;

        case 'scraping':
          if (event.status === 'started') {
            setCurrentStatus(`Scraping: ${event.url}`);
            setScrapingStatus(prev => {
              const exists = prev.some(s => s.url === event.url);
              if (exists) return prev;
              return [...prev, { url: event.url, status: 'started' }];
            });
          } else if (event.status === 'completed') {
            setCurrentStatus(`Scraped: ${event.title}`);
            setScrapingStatus(prev =>
              prev.map(s =>
                s.url === event.url
                  ? { ...s, status: 'completed', title: event.title }
                  : s
              )
            );
          }
          break;

        case 'scraping_error':
          setCurrentStatus(`Scraping failed: ${event.url}`);
          setScrapingStatus(prev =>
            prev.map(s => s.url === event.url ? { ...s, status: 'error' } : s)
          );
          break;

        case 'search_result':
          setSearchResults(prev => {
            if (prev.some(r => r.url === event.url)) return prev;
            return [...prev, {
              url: event.url!,
              title: event.title!,
              sentences_count: event.sentences_count!
            }];
          });
          setCurrentStatus(`Processed: ${event.title}`);
          break;

        case 'deduplication':
          setCurrentStatus(`Removed ${event.original_count! - event.final_count!} duplicates`);
          break;

        case 'final_response':
        case 'done':
          setCurrentStatus('Completed');
          setIsComplete(true);
          break;

        case 'error':
          setCurrentStatus(`Error: ${event.message || 'Unknown error'}`);
          setIsComplete(true);
          break;

        // Add more cases as needed...
      }
    });
  }, [streamData]); // This now triggers on every new event

  if (streamData.length === 0) return null;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.title}>Real-time Search Progress</h3>
        {!isComplete && <Loader2 className={`${styles.spinner} ${styles.animateSpin}`} size={16} />}
      </div>

      <div className={styles.statusContainer}>
        <div className={styles.statusIndicator}>
          <span className={styles.statusText}>{currentStatus}</span>
        </div>
      </div>

      {searchQueries.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}><Search size={14} /> Search Queries</h4>
          <ul className={styles.queriesList}>
            {searchQueries.map((q, i) => (
              <li key={i} className={styles.queryItem}>
                <Globe size={12} /> "{q}"
              </li>
            ))}
          </ul>
        </div>
      )}

      {scrapingStatus.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}><Download size={14} /> Scraping</h4>
          <ul className={styles.scrapingList}>
            {scrapingStatus.map((s, i) => (
              <li key={i} className={styles.scrapingItem}>
                {s.status === 'started' && <Loader2 className={styles.animateSpin} size={12} />}
                {s.status === 'completed' && <FileSearch size={12} />}
                {s.status === 'error' && <span className={styles.errorIcon}>Failed</span>}
                <span className={styles.scrapingUrl}>{s.title || s.url}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {searchResults.length > 0 && (
        <div className={styles.section}>
          <h4 className={styles.sectionTitle}><FileText size={14} /> Results</h4>
          <ul className={styles.resultsList}>
            {searchResults.map((r, i) => (
              <li key={i} className={styles.resultItem}>
                <div className={styles.resultTitle}>{r.title}</div>
                <div className={styles.resultUrl}>{r.url}</div>
                <div className={styles.resultCount}>
                  {r.sentences_count} relevant sentence{r.sentences_count !== 1 ? 's' : ''}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}