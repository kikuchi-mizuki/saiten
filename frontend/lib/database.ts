/**
 * データベース操作ヘルパー関数
 */

import { supabase } from './supabase'
import type { RubricResult, SummaryResult } from './api'
import { encryptText } from './api'

/**
 * レポート型定義
 */
export interface Report {
  id: string
  user_id: string
  student_id: string | null
  report_text: string
  encrypted_text: string | null
  created_at: string
  updated_at: string
}

/**
 * コメント生成結果型定義
 */
export interface Feedback {
  id: string
  user_id: string
  report_id: string | null
  ai_comment: string
  edited_comment: string | null
  rubric: RubricResult
  summary: SummaryResult
  llm_used: boolean
  llm_model: string | null
  used_refs: string[] | null
  edit_time_seconds: number | null
  satisfaction_score: number | null
  feedback_text: string | null
  created_at: string
  updated_at: string
}

/**
 * 履歴アイテム（結合データ）
 */
export interface HistoryItem {
  feedback: Feedback
  report: Report | null
}

/**
 * レポートを保存
 */
export async function saveReport(
  studentId: string,
  reportText: string
): Promise<Report | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  // レポートテキストを暗号化
  let encryptedText: string | null = null
  try {
    encryptedText = await encryptText(reportText)
  } catch (error) {
    console.error('Encryption error:', error)
    // 暗号化に失敗してもレポートは保存する（Phase 1では暗号化は任意）
  }

  const { data, error } = await supabase
    .from('reports')
    .insert({
      user_id: user.id,
      student_id: studentId || null,
      report_text: reportText,
      encrypted_text: encryptedText,
    })
    .select()
    .single()

  if (error) {
    console.error('Report save error:', error)
    throw error
  }

  return data
}

/**
 * コメント生成結果を保存
 */
export async function saveFeedback(
  reportId: string | null,
  aiComment: string,
  rubric: RubricResult,
  summary: SummaryResult,
  llmUsed: boolean,
  llmModel: string,
  usedRefs: string[]
): Promise<Feedback | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  const { data, error } = await supabase
    .from('feedbacks')
    .insert({
      user_id: user.id,
      report_id: reportId,
      ai_comment: aiComment,
      rubric: rubric,
      summary: summary,
      llm_used: llmUsed,
      llm_model: llmModel,
      used_refs: usedRefs,
    })
    .select()
    .single()

  if (error) {
    console.error('Feedback save error:', error)
    throw error
  }

  return data
}

/**
 * 編集されたコメントを更新
 */
export async function updateEditedComment(
  feedbackId: string,
  editedComment: string
): Promise<void> {
  const { error } = await supabase
    .from('feedbacks')
    .update({ edited_comment: editedComment })
    .eq('id', feedbackId)

  if (error) {
    console.error('Update edited comment error:', error)
    throw error
  }
}

/**
 * 品質評価を保存
 */
export async function saveQualityRating(
  feedbackId: string,
  editTimeSeconds: number,
  satisfactionScore: number,
  feedbackText: string
): Promise<void> {
  const { error } = await supabase
    .from('feedbacks')
    .update({
      edit_time_seconds: editTimeSeconds,
      satisfaction_score: satisfactionScore,
      feedback_text: feedbackText,
    })
    .eq('id', feedbackId)

  if (error) {
    console.error('Save quality rating error:', error)
    throw error
  }
}

/**
 * 履歴一覧を取得（最新順）
 */
export async function getHistoryList(
  limit: number = 50,
  offset: number = 0
): Promise<HistoryItem[]> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  // feedbacksを取得し、reportsを結合
  const { data: feedbacks, error } = await supabase
    .from('feedbacks')
    .select(
      `
      *,
      report:reports(*)
    `
    )
    .eq('user_id', user.id)
    .order('created_at', { ascending: false })
    .range(offset, offset + limit - 1)

  if (error) {
    console.error('Get history list error:', error)
    throw error
  }

  return (feedbacks || []).map((fb: any) => ({
    feedback: fb,
    report: fb.report,
  }))
}

/**
 * 履歴詳細を取得
 */
export async function getHistoryDetail(feedbackId: string): Promise<HistoryItem | null> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  const { data, error } = await supabase
    .from('feedbacks')
    .select(
      `
      *,
      report:reports(*)
    `
    )
    .eq('id', feedbackId)
    .eq('user_id', user.id)
    .single()

  if (error) {
    console.error('Get history detail error:', error)
    throw error
  }

  if (!data) {
    return null
  }

  return {
    feedback: data,
    report: data.report,
  }
}

/**
 * 履歴を削除
 */
export async function deleteHistory(feedbackId: string): Promise<void> {
  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    throw new Error('ユーザーが認証されていません')
  }

  // feedbackを削除（関連するreportはCASCADEで削除される）
  const { error } = await supabase
    .from('feedbacks')
    .delete()
    .eq('id', feedbackId)
    .eq('user_id', user.id)

  if (error) {
    console.error('Delete history error:', error)
    throw error
  }
}

/**
 * 履歴データをCSV形式でエクスポート
 */
export async function exportHistoryCSV(): Promise<string> {
  const history = await getHistoryList(1000) // 全件取得

  // CSVヘッダー
  const headers = [
    '作成日時',
    '学生ID',
    'レポート文字数',
    'Rubric合計点',
    'AI使用',
    'コメント文字数',
    '満足度',
  ]

  // CSVデータ
  const rows = history.map((item) => {
    const totalScore = Object.values(item.feedback.rubric).reduce(
      (sum, rubricItem) => sum + rubricItem.score,
      0
    )

    return [
      new Date(item.feedback.created_at).toLocaleString('ja-JP'),
      item.report?.student_id || '',
      item.report?.report_text.length || 0,
      totalScore,
      item.feedback.llm_used ? 'はい' : 'いいえ',
      item.feedback.ai_comment.length,
      item.feedback.satisfaction_score || '',
    ]
  })

  // CSV文字列を生成
  const csvContent = [headers, ...rows]
    .map((row) => row.map((cell) => `"${cell}"`).join(','))
    .join('\n')

  return csvContent
}
