// 真实 API 服务层：使用 fetch 调用后端
import { state } from './store'
import type { DatabaseInfo, RecordRow, DocInfo, ChunkInfo, TaskInfo, VectorConfig } from './store'

export interface FilterCondition { field: string; operator: string; value: any }
export interface FilterGroup { logic: 'AND' | 'OR'; conditions: FilterCondition[] }
export interface RecordQuery {
  page?: number; pageSize?: number; search?: string; filter?: FilterGroup | null
}

async function apiFetch(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = { ...(options.headers as Record<string, string> || {}) }
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }
  const resp = await fetch(path, { ...options, headers })
  const json = await resp.json()
  if (json.code !== 0) throw new Error(json.message || 'API error')
  return json.data
}

// ---------- 数据库 ----------
export async function listDatabases(): Promise<DatabaseInfo[]> {
  const data = await apiFetch('/api/databases')
  const list = (data || []).map((d: any) => ({ ...d, id: d.id || d._id }))
  state.databases = list
  return list
}

export async function createDatabase(name: string, type: 'normal' | 'vector'): Promise<DatabaseInfo> {
  const d = await apiFetch('/api/databases', {
    method: 'POST',
    body: JSON.stringify({ name, type }),
  })
  return { ...d, id: d.id || d._id }
}

export async function renameDatabase(id: string, name: string): Promise<DatabaseInfo> {
  const data = await apiFetch(`/api/databases/${id}`, { method: 'PUT', body: JSON.stringify({ name }) })
  return { ...data, id: data.id || data._id }
}

export async function deleteDatabase(id: string) {
  await apiFetch(`/api/databases/${id}`, { method: 'DELETE' })
}

export async function listTrash(): Promise<DatabaseInfo[]> {
  const data = await apiFetch('/api/trash')
  const list = (data || []).map((d: any) => ({ ...d, id: d.id || d._id }))
  state.trash = list
  return list
}

export async function loadStorage() {
  const data = await apiFetch('/api/system/storage')
  state.storage = data
}

export interface EmbeddingModel {
  name: string
  path: string
  dims: number | null
  default: boolean
}

export async function listModels(): Promise<EmbeddingModel[]> {
  return apiFetch('/api/system/models')
}

export async function getVectorConfig(dbId: string): Promise<VectorConfig> {
  return apiFetch(`/api/databases/${dbId}/vector-config`)
}

export async function updateVectorConfig(dbId: string, config: Omit<VectorConfig, 'dimensions'>): Promise<VectorConfig> {
  return apiFetch(`/api/databases/${dbId}/vector-config`, {
    method: 'PUT',
    body: JSON.stringify(config),
  })
}

export async function getHelpDocument(locale: 'zh' | 'ja' | 'en'): Promise<{ locale: 'zh' | 'ja' | 'en'; content: string }> {
  return apiFetch(`/api/system/help?locale=${encodeURIComponent(locale)}`)
}

export async function restoreFromTrash(id: string) {
  await apiFetch(`/api/trash/${id}/restore`, { method: 'POST' })
}

export async function destroyTrashed(id: string) {
  await apiFetch(`/api/trash/${id}`, { method: 'DELETE' })
}

export async function emptyTrash() {
  await apiFetch('/api/trash', { method: 'DELETE' })
}

// ---------- 记录 ----------
export async function listRecords(dbId: string, q: RecordQuery) {
  const params = new URLSearchParams({
    page: String(q.page || 1),
    pageSize: String(q.pageSize || 20),
    search: q.search || '',
  })
  if (q.filter) params.set('filter', JSON.stringify(q.filter))
  return apiFetch(`/api/databases/${dbId}/records?${params}`)
}

export async function getRecord(dbId: string, rid: string): Promise<RecordRow | undefined> {
  const data = await apiFetch(`/api/databases/${dbId}/records`)
  return (data.list || []).find((x: any) => (x._id === rid || x.id === rid))
}

export async function createRecord(dbId: string, json: RecordRow) {
  await apiFetch(`/api/databases/${dbId}/records`, { method: 'POST', body: JSON.stringify(json) })
}

export async function updateRecord(dbId: string, rid: string, json: RecordRow) {
  await apiFetch(`/api/databases/${dbId}/records/${rid}`, { method: 'PUT', body: JSON.stringify(json) })
}

export async function deleteRecords(dbId: string, ids: string[]) {
  await apiFetch(`/api/databases/${dbId}/records/delete`, { method: 'POST', body: JSON.stringify({ ids }) })
}

export async function getFields(dbId: string): Promise<string[]> {
  return apiFetch(`/api/databases/${dbId}/records/fields`)
}

// ---------- 文档 ----------
export async function listDocuments(dbId: string, opts: { search?: string; status?: string } = {}) {
  const params = new URLSearchParams(opts as any)
  const data = await apiFetch(`/api/databases/${dbId}/documents?${params}`)
  return (data || []).map((d: any) => ({ ...d, id: d.id || d._id }))
}

export async function addUploadedDocument(dbId: string, file: File | Blob) {
  const form = new FormData()
  form.append('file', file, (file as File).name || 'upload.txt')
  const resp = await fetch(`/api/databases/${dbId}/documents/upload`, { method: 'POST', body: form })
  const json = await resp.json()
  if (json.code !== 0) throw new Error(json.message || 'upload error')
  return json.data
}

export async function renameDocument(dbId: string, docId: string, name: string) {
  // 暂不支持
}

export async function deleteDocuments(dbId: string, docIds: string[]) {
  await apiFetch(`/api/databases/${dbId}/documents/delete`, { method: 'POST', body: JSON.stringify({ ids: docIds }) })
}

export async function downloadDocument(dbId: string, docId: string, filename: string) {
  const resp = await fetch(`/api/databases/${dbId}/documents/${docId}/download`)
  if (!resp.ok) throw new Error('文档下载失败')
  const url = URL.createObjectURL(await resp.blob())
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export async function startVectorization(dbId: string, docIds: string[], config: { model: string; chunkSize: number; overlap: number }) {
  await apiFetch(`/api/databases/${dbId}/documents/vectorize`, {
    method: 'POST',
    body: JSON.stringify({ docIds, ...config }),
  })
}

// ---------- 分片 ----------
export async function listChunks(dbId: string, opts: { docId?: string; search?: string; page?: number; pageSize?: number } = {}) {
  const params = new URLSearchParams({
    page: String(opts.page || 1),
    pageSize: String(opts.pageSize || 20),
    search: opts.search || '',
    docId: opts.docId || '',
  })
  return apiFetch(`/api/databases/${dbId}/chunks?${params}`)
}

export async function reembedChunk(dbId: string, chunkId: string) {
  await apiFetch(`/api/databases/${dbId}/chunks/${chunkId}/reembed`, { method: 'POST' })
}

export async function deleteChunks(dbId: string, ids: string[]) {
  await apiFetch(`/api/databases/${dbId}/chunks/delete`, { method: 'POST', body: JSON.stringify({ ids }) })
}

// ---------- 任务 ----------
export async function listTasks(dbId?: string, opts: { type?: string; status?: string } = {}) {
  const params = new URLSearchParams({
    dbId: dbId || '',
    type: opts.type || '',
    status: opts.status || '',
  })
  const data = await apiFetch(`/api/tasks?${params}`)
  return (data || []).map((t: any) => ({ ...t, id: t.id || t._id }))
}

export async function cancelTask(dbId: string, taskId: string) {
  await apiFetch(`/api/tasks/${taskId}/cancel?dbId=${dbId}`, { method: 'POST' })
}

export async function retryTask(dbId: string, taskId: string) {
  await apiFetch(`/api/tasks/${taskId}/retry?dbId=${dbId}`, { method: 'POST' })
}

export async function getTaskLogs(dbId: string, taskId: string): Promise<string[]> {
  return apiFetch(`/api/tasks/${taskId}/logs?dbId=${dbId}`)
}

// ---------- 索引 ----------
export async function getIndexSettings(dbId: string) {
  return apiFetch(`/api/databases/${dbId}/index`)
}

export async function rebuildIndex(dbId: string) {
  await apiFetch(`/api/databases/${dbId}/index/rebuild`, { method: 'POST' })
}

export async function deleteIndexTask(dbId: string) {
  await apiFetch(`/api/databases/${dbId}/index`, { method: 'DELETE' })
}

export async function changeIndexModel(dbId: string, model: string) {
  await apiFetch(`/api/databases/${dbId}/index/change-model`, { method: 'POST', body: JSON.stringify({ model }) })
}

// ---------- 检索 ----------
export async function retrievalQuery(dbId: string, opts: { question: string; topK: number; threshold: number }) {
  return apiFetch(`/api/databases/${dbId}/retrieval`, {
    method: 'POST',
    body: JSON.stringify({
      query: opts.question,
      topK: opts.topK,
      threshold: opts.threshold,
    }),
  })
}

// ---------- 统计 ----------
export async function getStats(dbId: string) {
  return apiFetch(`/api/databases/${dbId}/stats`)
}
