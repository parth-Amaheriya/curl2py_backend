export interface RequestItem {
  id: string;
  name: string;
  curl: string;
  python: string;
  status: 'idle' | 'converting' | 'completed' | 'error';
  method?: string;
  endpoint?: string;
  format?: string;
}
