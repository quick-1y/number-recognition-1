export type ChannelStatus = 'online' | 'offline' | 'degraded';
export type Tab = 'grid' | 'events' | 'search' | 'lists' | 'settings' | 'diagnostics';
export type UserRole = 'admin' | 'operator' | 'viewer';

export interface ChannelInfo {
  id: string;
  name: string;
  fps: number;
  status: ChannelStatus;
}

export interface EventItem {
  id: string;
  plate: string;
  timestamp: string;
  channel: string;
  confidence: number;
  list?: 'white' | 'black' | 'info';
}
