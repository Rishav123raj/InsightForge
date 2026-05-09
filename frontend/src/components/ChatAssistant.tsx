import { FormEvent, useMemo, useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { askAssistant } from '../lib/api';
import type { AssistantSettings, ChatMessage } from '../types/api';

const sampleQuestions = [
  'Which titles performed best in 2025?',
  'Why is Stellar Run trending recently?',
  'Compare Dark Orbit vs Last Kingdom.',
  'Which city had the strongest engagement last month?',
  'What explains weak comedy performance?',
  'What recommendations would you give for leadership?'
];

interface ChatAssistantProps {
  settings: AssistantSettings;
  onHistoryChange: (messages: ChatMessage[]) => void;
}

export function ChatAssistant({ settings, onHistoryChange }: ChatAssistantProps) {
  const [question, setQuestion] = useState(sampleQuestions[0]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const activeTrace = useMemo(
    () => [...messages].reverse().find((message) => message.response?.tool_trace?.length),
    [messages]
  );

  const updateMessages = (nextMessages: ChatMessage[]) => {
    setMessages(nextMessages);
    onHistoryChange(nextMessages);
  };

  const submitQuestion = async (event?: FormEvent) => {
    event?.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isLoading) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
      createdAt: new Date().toISOString()
    };
    const optimistic = [...messages, userMessage];
    updateMessages(optimistic);
    setIsLoading(true);

    try {
      const response = await askAssistant(trimmed, settings);
      updateMessages([
        ...optimistic,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.answer,
          createdAt: new Date().toISOString(),
          response
        }
      ]);
    } catch (error) {
      updateMessages([
        ...optimistic,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'I could not complete that request. Check backend status, API key, role, and CORS settings.',
          createdAt: new Date().toISOString(),
          error: error instanceof Error ? error.message : String(error)
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="panel chat-panel">
      <div className="panel__header">
        <h2>Chat assistant</h2>
        <span>{messages.length} messages</span>
      </div>

      <div className="prompt-chips" aria-label="Example questions">
        {sampleQuestions.map((sample) => (
          <button key={sample} type="button" onClick={() => setQuestion(sample)}>
            {sample}
          </button>
        ))}
      </div>

      <div className="messages" aria-live="polite">
        {messages.length === 0 ? (
          <div className="empty-state">
            <Sparkles size={30} />
            <h3>Ask a business question</h3>
            <p>Answers include sources, chart-ready data, and the backend tool trace used to produce the response.</p>
          </div>
        ) : (
          messages.map((message) => (
            <article key={message.id} className={`message message--${message.role}`}>
              <div className="message__meta">
                <strong>{message.role === 'user' ? 'You' : 'Assistant'}</strong>
                <time>{new Date(message.createdAt).toLocaleTimeString()}</time>
              </div>
              <p>{message.content}</p>
              {message.error && <pre className="error-box">{message.error}</pre>}
              {!!message.response?.sources?.length && (
                <div className="source-list">
                  {message.response.sources.map((source, index) => (
                    <span key={`${source.name}-${index}`}>{source.type}: {source.name}</span>
                  ))}
                </div>
              )}
              {message.response?.privacy_note && <small className="privacy-line">{message.response.privacy_note}</small>}
            </article>
          ))
        )}
      </div>

      <form className="ask-form" onSubmit={submitQuestion}>
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask about title performance, trends, regions, genres, or leadership recommendations..."
          rows={3}
        />
        <button type="submit" disabled={isLoading}>
          <Send size={18} /> {isLoading ? 'Asking...' : 'Ask'}
        </button>
      </form>

      {activeTrace?.response?.tool_trace && (
        <div className="compact-trace">
          <strong>Latest tool trace</strong>
          {activeTrace.response.tool_trace.map((trace, index) => (
            <span key={`${trace.tool}-${index}`}>{trace.tool}{trace.rows !== undefined ? ` (${trace.rows} rows)` : ''}</span>
          ))}
        </div>
      )}
    </section>
  );
}