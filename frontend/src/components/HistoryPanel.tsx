import { Clock3, Wrench } from 'lucide-react';
import type { ChatMessage } from '../types/api';

interface HistoryPanelProps {
  messages: ChatMessage[];
}

export function HistoryPanel({ messages }: HistoryPanelProps) {
  const userQuestions = messages.filter((message) => message.role === 'user').slice(-8).reverse();
  const traces = messages
    .filter((message) => message.response?.tool_trace?.length)
    .slice(-5)
    .reverse();

  return (
    <section className="panel history-panel">
      <div className="panel__header">
        <h2>Query history & trace</h2>
      </div>

      <div className="history-section">
        <h3><Clock3 size={17} /> Recent questions</h3>
        {userQuestions.length === 0 ? (
          <p className="muted">Questions you ask will appear here.</p>
        ) : (
          <ol>
            {userQuestions.map((message) => (
              <li key={message.id}>
                <span>{message.content}</span>
                <time>{new Date(message.createdAt).toLocaleTimeString()}</time>
              </li>
            ))}
          </ol>
        )}
      </div>

      <div className="history-section">
        <h3><Wrench size={17} /> Backend tool trace</h3>
        {traces.length === 0 ? (
          <p className="muted">Tool calls returned by the assistant will appear here.</p>
        ) : (
          traces.map((message) => (
            <div key={message.id} className="trace-card">
              {message.response?.tool_trace?.map((trace, index) => (
                <div key={`${message.id}-${trace.tool}-${index}`}>
                  <strong>{trace.tool}</strong>
                  <span>{trace.reason ?? 'Approved backend tool'}</span>
                  {trace.result_count !== undefined && (<small>{trace.result_count} rows</small>)}
                </div>
              ))}
            </div>
          ))
        )}
      </div>
    </section>
  );
}