export type UserRole = 'analyst' | 'leadership' | 'marketing';

export interface SourceRef {
  type: string;
  name: string;
  detail?: string;
}

export interface ToolTraceItem {
  tool: string;
  reason?: string;
  result_count?: number;
}

export interface ChartPoint {
  label?: string;
  title?: string;
  city?: string;
  value?: number;
  revenue?: number;
  views?: number;
  completion_rate?: number;
  [key: string]: string | number | boolean | undefined;
}

export interface ChatResponse {
  answer: string;
  sources?: SourceRef[];
  tool_trace?: ToolTraceItem[];
  chart?: ChartPoint[];
  privacy_note?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
  response?: ChatResponse;
  error?: string;
}

export interface BestTitleRow {
  title: string;
  genre: string;
  minutes: number;
  completions: number;
  avg_rating: number;
  revenue: number;
}

export interface CityEngagementRow {
  city: string;
  views: number;
  completion_rate: number;
  revenue: number;
}

export interface AssistantSettings {
  apiBaseUrl: string;
  apiKey: string;
  role: UserRole;
  year: number;
  month: string;
  isAuthenticated:boolean;
}