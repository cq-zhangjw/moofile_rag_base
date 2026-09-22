// 状态体系（对应 ui-design.md §8）
import type { CSSProperties } from 'vue';

export interface StatusStyle {
  label: string;
  color: string;
  soft: string;
  border: string;
  spin?: boolean;
}

// 文档生命周期状态
export const DOC_STATUS: Record<string, StatusStyle> = {
  uploaded:    { label: 'status.uploaded', color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' },
  parsed:      { label: 'status.parsed', color: '#2563EB', soft: '#EFF6FF', border: '#BFDBFE' },
  waiting:     { label: 'status.waiting', color: '#D97706', soft: '#FFFBEB', border: '#FDE68A' },
  vectorizing: { label: 'status.vectorizing', color: '#7C3AED', soft: '#F5F3FF', border: '#DDD6FE', spin: true },
  completed:   { label: 'status.completed', color: '#16A34A', soft: '#F0FDF4', border: '#BBF7D0' },
  failed:      { label: 'status.failed', color: '#DC2626', soft: '#FEF2F2', border: '#FECACA' },
};

// 向量状态（文档表格中的第二列）
export const VECTOR_STATUS: Record<string, StatusStyle> = {
  none:    { label: 'status.none', color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' },
  partial: { label: 'status.partial', color: '#D97706', soft: '#FFFBEB', border: '#FDE68A' },
  done:    { label: 'status.done', color: '#16A34A', soft: '#F0FDF4', border: '#BBF7D0' },
  doing:   { label: 'status.doing', color: '#7C3AED', soft: '#F5F3FF', border: '#DDD6FE', spin: true },
  failed:  { label: 'status.failed', color: '#DC2626', soft: '#FEF2F2', border: '#FECACA' },
};

// 任务状态
export const TASK_STATUS: Record<string, StatusStyle> = {
  pending:   { label: 'status.pending', color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' },
  running:   { label: 'status.running', color: '#2563EB', soft: '#EFF6FF', border: '#BFDBFE', spin: true },
  completed: { label: 'status.completed', color: '#16A34A', soft: '#F0FDF4', border: '#BBF7D0' },
  failed:    { label: 'status.failed', color: '#DC2626', soft: '#FEF2F2', border: '#FECACA' },
  cancelled: { label: 'status.cancelled', color: '#9CA3AF', soft: '#F3F4F6', border: '#E5E7EB' },
};

// 索引状态
export const INDEX_STATUS: Record<string, StatusStyle> = {
  not_built: { label: 'status.notBuilt', color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' },
  building:  { label: 'status.building', color: '#2563EB', soft: '#EFF6FF', border: '#BFDBFE', spin: true },
  ready:     { label: 'status.completed', color: '#16A34A', soft: '#F0FDF4', border: '#BBF7D0' },
  failed:    { label: 'status.failed', color: '#DC2626', soft: '#FEF2F2', border: '#FECACA' },
};

// 数据浏览页 status（chunk 索引状态）
export const RECORD_STATUS: Record<string, StatusStyle> = {
  indexed:     { label: 'status.indexed', color: '#16A34A', soft: '#F0FDF4', border: '#BBF7D0' },
  not_indexed: { label: 'status.notIndexed', color: '#374151', soft: '#F3F4F6', border: '#E5E7EB' },
  failed:      { label: 'status.failed', color: '#DC2626', soft: '#FEF2F2', border: '#FECACA' },
};

export const TASK_TYPES: Record<string, { label: string; style: CSSProperties }> = {
  parse:         { label: 'taskType.parse', style: { color: '#2563EB' } },
  vectorization: { label: 'taskType.vectorization', style: { color: '#7C3AED' } },
  rebuild:       { label: 'taskType.rebuild', style: { color: '#D97706' } },
  delete_index:  { label: 'taskType.deleteIndex', style: { color: '#DC2626' } },
};

// 筛选操作符（对应 ui-design.md §8.3）
export const OPERATORS = [
  { key: 'eq', label: 'operator.eq', needValue: true, type: 'input' },
  { key: 'ne', label: 'operator.ne', needValue: true, type: 'input' },
  { key: 'contains', label: 'operator.contains', needValue: true, type: 'input' },
  { key: 'not_contains', label: 'operator.notContains', needValue: true, type: 'input' },
  { key: 'gt', label: 'operator.gt', needValue: true, type: 'number' },
  { key: 'gte', label: 'operator.gte', needValue: true, type: 'number' },
  { key: 'lt', label: 'operator.lt', needValue: true, type: 'number' },
  { key: 'lte', label: 'operator.lte', needValue: true, type: 'number' },
  { key: 'exists', label: 'operator.exists', needValue: false, type: 'none' },
  { key: 'not_exists', label: 'operator.notExists', needValue: false, type: 'none' },
  { key: 'regex', label: 'operator.regex', needValue: true, type: 'input' },
  { key: 'array_contains', label: 'operator.arrayContains', needValue: true, type: 'input' },
] as const;

export const EMBEDDING_MODELS = [
  { label: 'text-embedding-3-small', value: 'text-embedding-3-small' },
  { label: 'text-embedding-3-large', value: 'text-embedding-3-large' },
  { label: 'bge-large', value: 'bge-large' },
  { label: 'gte-large', value: 'gte-large' },
];

export const FILE_TYPE_COLORS: Record<string, string> = {
  PDF: '#DC2626',
  DOCX: '#2563EB',
  TXT: '#6B7280',
  MD: '#7C3AED',
  PPTX: '#D97706',
  HTML: '#D97706',
  MP4: '#7C3AED',
};
