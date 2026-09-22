// 前端响应式状态层（由 API 服务层填充）
import { reactive } from 'vue'

export interface DatabaseInfo {
  id: string;
  name: string;
  type: 'normal' | 'vector';
  recordCount: number;
  documentCount: number;
  fieldCount: number;
  sizeMB: number;
  updatedAt: string;
  trashed?: boolean;
  createdAt?: string;
  vectorConfig?: VectorConfig;
}

export interface VectorConfig {
  model: string;
  dimensions: number;
  chunkSize: number;
  chunkOverlap: number;
  topK: number;
  similarityThreshold: number;
}

export interface RecordRow {
  _id: string;
  [k: string]: any;
}

export interface DocInfo {
  id: string;
  dbId: string;
  name: string;
  type: string;
  size: number;
  uploadTime: string;
  docStatus: 'uploaded' | 'parsed' | 'waiting' | 'vectorizing' | 'completed' | 'failed';
  chunkCount: number;
  vectorStatus: 'none' | 'partial' | 'done' | 'doing' | 'failed';
  chunkSize: number;
  overlap: number;
  errorMsg?: string;
}

export interface ChunkInfo {
  id: string;
  dbId: string;
  documentId: string;
  document: string;
  index: number;
  content: string;
  tokens: number;
  embedStatus: 'done' | 'none' | 'failed';
  page: number;
}

export interface TaskInfo {
  id: string;
  dbId: string;
  type: 'parse' | 'vectorization' | 'rebuild' | 'delete_index';
  target: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startAt: string;
  endAt: string | null;
  progress: number;
  docIds?: string[];
  failChance?: number;
  logs?: string[];
}

export const state = reactive({
  databases: [] as DatabaseInfo[],
  trash: [] as DatabaseInfo[],
  records: {} as Record<string, RecordRow[]>,
  documents: {} as Record<string, DocInfo[]>,
  chunks: {} as Record<string, ChunkInfo[]>,
  tasks: {} as Record<string, TaskInfo[]>,
  storage: { usedGB: 0, quotaGB: 5, percent: 0 },
  index: {} as Record<string, any>,
})
