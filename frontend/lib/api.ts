/**
 * バックエンドAPI呼び出し関数
 * Updated: 2025-11-17 - Force rebuild for Railway deployment
 */

import { getAccessToken } from './auth'

// 本番環境では必ずRailwayのURLを使用
// 環境変数が設定されていない場合は本番URLをフォールバック
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://saiten-production.up.railway.app'

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
 * Rubric評価項目の型定義
 */
export interface RubricItem {
  score: number
  reason: string
}

/**
 * Rubric評価結果の型定義
 */
export interface RubricResult {
  理解度: RubricItem
  論理性: RubricItem
  独自性: RubricItem
  実践性: RubricItem
  表現力: RubricItem
}

/**
 * 要約結果の型定義
 */
export interface SummaryResult {
  executive: string
  bullets: string[]
  structured: {
    主要テーマ: string
    要点: string
    考察の深さ: string
    実践性: string
  }
  formatted: string
}

/**
 * コメント生成レスポンスの型定義
 */
export interface GenerateResponse {
  report_id: string | null
  feedback_id: string | null
  ai_comment: string
  rubric: RubricResult
  summary: SummaryResult
  used_refs: string[]
  llm_used: boolean
  llm_error: string | null
  summary_llm_used: boolean
  summary_error: string | null
}

/**
 * コメント生成リクエスト
 */
export async function generateComment(
  text: string,
  type: 'reflection' | 'final' = 'reflection'
): Promise<GenerateResponse> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/generate_direct`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      text,
      type,
    }),
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`)
  }

  return response.json()
}

/**
 * ヘルスチェック
 */
export async function healthCheck(): Promise<{ ok: boolean }> {
  const response = await fetch(`${API_BASE_URL}/health`)

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`)
  }

  return response.json()
}

/**
 * テキストを暗号化
 */
export async function encryptText(text: string): Promise<string> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/encrypt`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ text }),
  })

  if (!response.ok) {
    throw new Error(`Encryption failed: ${response.status} ${response.statusText}`)
  }

  const data = await response.json()
  return data.encrypted_text
}

/**
 * 暗号文を復号化
 */
export async function decryptText(encryptedText: string): Promise<string> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/decrypt`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ encrypted_text: encryptedText }),
  })

  if (!response.ok) {
    throw new Error(`Decryption failed: ${response.status} ${response.statusText}`)
  }

  const data = await response.json()
  return data.text
}

/**
 * 統計情報型定義
 */
export interface StatsResponse {
  total_feedbacks: number
  avg_rubric_scores: {
    理解度: number
    論理性: number
    独自性: number
    実践性: number
    表現力: number
  }
  avg_edit_time_seconds: number | null
  avg_satisfaction_score: number | null
}

/**
 * 統計情報を取得
 */
export async function getStats(): Promise<StatsResponse> {
  const headers = await getAuthHeaders()

  const response = await fetch(`${API_BASE_URL}/stats`, {
    method: 'GET',
    headers,
  })

  if (!response.ok) {
    throw new Error(`Stats fetch failed: ${response.status} ${response.statusText}`)
  }

  return response.json()
}
