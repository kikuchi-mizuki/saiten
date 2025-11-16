/**
 * 参照例管理用のAPI呼び出し関数
 */

import { getAccessToken } from './auth'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8010'

/**
 * 認証ヘッダーを含むヘッダーを取得
 */
async function getAuthHeaders(): Promise<HeadersInit> {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  const token = await getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

/**
 * 参照例型定義
 */
export interface ReferenceExample {
  id: string
  type: 'reflection' | 'final'
  text: string
  tags: string[]
  source: string
}

/**
 * 参照例作成リクエスト
 */
export interface ReferenceCreateRequest {
  type: 'reflection' | 'final'
  text: string
  tags: string[]
  source?: string
}

/**
 * 参照例更新リクエスト
 */
export interface ReferenceUpdateRequest {
  type?: 'reflection' | 'final'
  text?: string
  tags?: string[]
  source?: string
}

/**
 * 全ての参照例を取得
 */
export async function getAllReferences(): Promise<{
  references: ReferenceExample[]
  count: number
}> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references`, { headers })
  if (!response.ok) {
    throw new Error('参照例の取得に失敗しました')
  }
  return response.json()
}

/**
 * 特定の参照例を取得
 */
export async function getReference(id: string): Promise<ReferenceExample> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references/${id}`, { headers })
  if (!response.ok) {
    throw new Error('参照例の取得に失敗しました')
  }
  return response.json()
}

/**
 * 新しい参照例を作成
 */
export async function createReference(
  data: ReferenceCreateRequest
): Promise<{ success: boolean; reference: ReferenceExample }> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('参照例の作成に失敗しました')
  }

  return response.json()
}

/**
 * 参照例を更新
 */
export async function updateReference(
  id: string,
  data: ReferenceUpdateRequest
): Promise<{ success: boolean; reference: ReferenceExample }> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references/${id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data),
  })

  if (!response.ok) {
    throw new Error('参照例の更新に失敗しました')
  }

  return response.json()
}

/**
 * 参照例を削除
 */
export async function deleteReference(id: string): Promise<void> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references/${id}`, {
    method: 'DELETE',
    headers,
  })

  if (!response.ok) {
    throw new Error('参照例の削除に失敗しました')
  }
}

/**
 * CSV形式で参照例を一括インポート
 */
export async function importReferencesFromCSV(
  csvData: string
): Promise<{
  success: boolean
  imported_count: number
  errors?: string[]
}> {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_BASE}/references/import-csv`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ csv_data: csvData }),
  })

  if (!response.ok) {
    throw new Error('CSVインポートに失敗しました')
  }

  return response.json()
}
