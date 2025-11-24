/**
 * 参照例管理用のAPI呼び出し関数
 */

import { getAccessToken } from './auth'

// 本番環境では必ずRailwayのURLを使用
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://saiten-production.up.railway.app'

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
 * 参照例取得のオプション（Phase 2: 検索・フィルタ・ページネーション対応）
 */
export interface GetReferencesOptions {
  search?: string
  tags?: string
  type?: 'reflection' | 'final'
  sort?: 'created_desc' | 'created_asc'
  page?: number
  per_page?: number
}

/**
 * 参照例取得のレスポンス（Phase 2対応）
 */
export interface GetReferencesResponse {
  references: ReferenceExample[]
  count: number
  total: number
  page: number
  per_page: number
  total_pages: number
}

/**
 * 全ての参照例を取得（Phase 2: 検索・フィルタ・ページネーション対応）
 */
export async function getAllReferences(
  options: GetReferencesOptions = {}
): Promise<GetReferencesResponse> {
  const headers = await getAuthHeaders()

  // クエリパラメータを構築
  const params = new URLSearchParams()
  if (options.search) params.append('search', options.search)
  if (options.tags) params.append('tags', options.tags)
  if (options.type) params.append('type', options.type)
  if (options.sort) params.append('sort', options.sort)
  if (options.page) params.append('page', options.page.toString())
  if (options.per_page) params.append('per_page', options.per_page.toString())

  const url = `${API_BASE}/references${params.toString() ? `?${params.toString()}` : ''}`
  const response = await fetch(url, { headers })

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
 * 参照例作成のレスポンス（Phase 2: LLM自動タグ付け対応）
 */
export interface CreateReferenceResponse {
  success: boolean
  reference: ReferenceExample & {
    auto_tagged?: boolean  // LLMが自動でタグ付けしたかどうか
  }
}

/**
 * 新しい参照例を作成（Phase 2: LLM自動タグ付け対応）
 */
export async function createReference(
  data: ReferenceCreateRequest
): Promise<CreateReferenceResponse> {
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

