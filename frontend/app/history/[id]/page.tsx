'use client'

/**
 * 履歴詳細ページ
 *
 * 特定のコメント生成履歴の詳細を表示します。
 */

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/auth'
import { getHistoryDetail, deleteHistory, type HistoryItem } from '@/lib/database'
import type { User } from '@supabase/supabase-js'

type TabType = 'rubric' | 'summary' | 'comment'

export default function HistoryDetailPage() {
  const router = useRouter()
  const params = useParams()
  const feedbackId = params.id as string

  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [history, setHistory] = useState<HistoryItem | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('rubric')
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    // 認証状態を確認
    async function checkAuth() {
      const currentUser = await getCurrentUser()

      if (!currentUser) {
        router.push('/login')
        return
      }

      setUser(currentUser)
      await loadHistoryDetail()
      setIsLoading(false)
    }

    checkAuth()
  }, [router, feedbackId])

  /**
   * 履歴詳細を読み込み
   */
  async function loadHistoryDetail() {
    try {
      const data = await getHistoryDetail(feedbackId)
      if (!data) {
        alert('履歴が見つかりませんでした')
        router.push('/history')
        return
      }
      setHistory(data)
    } catch (error) {
      console.error('Load history detail error:', error)
      alert('履歴の読み込みに失敗しました')
      router.push('/history')
    }
  }

  /**
   * ログアウト処理
   */
  async function handleSignOut() {
    try {
      await signOut()
      router.push('/login')
    } catch (error) {
      console.error('Sign out error:', error)
      alert('ログアウトに失敗しました')
    }
  }

  /**
   * 履歴削除
   */
  async function handleDelete() {
    if (!confirm('この履歴を削除しますか？この操作は取り消せません。')) {
      return
    }

    setIsDeleting(true)

    try {
      await deleteHistory(feedbackId)
      alert('履歴を削除しました')
      router.push('/history')
    } catch (error) {
      console.error('Delete history error:', error)
      alert('履歴の削除に失敗しました')
      setIsDeleting(false)
    }
  }

  /**
   * コメントをコピー
   */
  function handleCopyComment() {
    if (history?.feedback.edited_comment || history?.feedback.ai_comment) {
      const comment = history.feedback.edited_comment || history.feedback.ai_comment
      navigator.clipboard.writeText(comment)
      alert('コメントをクリップボードにコピーしました')
    }
  }

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ backgroundColor: 'var(--bg)' }}
      >
        <div className="text-center">
          <svg
            className="animate-spin h-8 w-8 mx-auto mb-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            style={{ color: 'var(--accent)' }}
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p style={{ color: 'var(--text-muted)' }}>読み込み中...</p>
        </div>
      </div>
    )
  }

  if (!history) {
    return null
  }

  const totalScore = Object.values(history.feedback.rubric).reduce(
    (sum, rubricItem) => sum + rubricItem.score,
    0
  )

  return (
    <div
      className="min-h-screen"
      style={{ backgroundColor: 'var(--bg)' }}
    >
      {/* ヘッダー */}
      <header
        className="border-b"
        style={{
          backgroundColor: 'var(--surface)',
          borderColor: 'var(--border)'
        }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1
            className="text-[18px] font-semibold"
            style={{ color: 'var(--text)' }}
          >
            履歴詳細
          </h1>

          <div className="flex items-center gap-4">
            {/* 戻るリンク */}
            <Link
              href="/history"
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--surface-subtle)',
                color: 'var(--text)',
                border: '1px solid var(--border)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
              }}
            >
              履歴に戻る
            </Link>

            {/* 削除ボタン */}
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: isDeleting ? 'var(--border)' : '#FEE2E2',
                color: '#DC2626',
                border: '1px solid #FCA5A5',
                opacity: isDeleting ? 0.5 : 1,
                cursor: isDeleting ? 'not-allowed' : 'pointer'
              }}
              onMouseEnter={(e) => {
                if (!isDeleting) {
                  e.currentTarget.style.backgroundColor = '#FCA5A5'
                }
              }}
              onMouseLeave={(e) => {
                if (!isDeleting) {
                  e.currentTarget.style.backgroundColor = '#FEE2E2'
                }
              }}
            >
              {isDeleting ? '削除中...' : '削除'}
            </button>

            {/* ユーザー情報 */}
            <div className="text-right">
              <p
                className="text-[13px] font-medium"
                style={{ color: 'var(--text)' }}
              >
                {user?.email}
              </p>
              <p
                className="text-[12px]"
                style={{ color: 'var(--text-muted)' }}
              >
                ログイン中
              </p>
            </div>

            {/* ログアウトボタン */}
            <button
              onClick={handleSignOut}
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--surface-subtle)',
                color: 'var(--text-muted)',
                border: '1px solid var(--border)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--bg)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
              }}
            >
              ログアウト
            </button>
          </div>
        </div>
      </header>

      {/* メインコンテンツ: 7:5の2カラムレイアウト */}
      <main className="max-w-[1400px] mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* 左カラム（7/12） - レポート表示 */}
          <div className="col-span-7">
            <div
              className="p-6 rounded-[var(--radius)]"
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)'
              }}
            >
              <div className="mb-4">
                <p
                  className="text-[12px] mb-1"
                  style={{ color: 'var(--text-muted)' }}
                >
                  作成日時
                </p>
                <p
                  className="text-[14px] font-medium"
                  style={{ color: 'var(--text)' }}
                >
                  {new Date(history.feedback.created_at).toLocaleString('ja-JP')}
                </p>
              </div>

              {history.report?.student_id && (
                <div className="mb-4">
                  <p
                    className="text-[12px] mb-1"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    学生ID
                  </p>
                  <p
                    className="text-[14px] font-medium"
                    style={{ color: 'var(--text)' }}
                  >
                    {history.report.student_id}
                  </p>
                </div>
              )}

              <div className="mb-4">
                <p
                  className="text-[12px] mb-2"
                  style={{ color: 'var(--text-muted)' }}
                >
                  レポート本文
                </p>
                <div
                  className="p-4 rounded-[var(--radius-sm)] max-h-[500px] overflow-y-auto"
                  style={{
                    backgroundColor: 'var(--bg)',
                    border: '1px solid var(--border)'
                  }}
                >
                  <p
                    className="text-[14px] leading-relaxed whitespace-pre-wrap"
                    style={{ color: 'var(--text)' }}
                  >
                    {history.report?.report_text || '（レポート本文なし）'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* 右カラム（5/12） - 結果表示エリア */}
          <div className="col-span-5">
            <div
              className="rounded-[var(--radius)]"
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)'
              }}
            >
              {/* タブヘッダー */}
              <div
                className="flex border-b"
                style={{ borderColor: 'var(--border)' }}
              >
                <button
                  onClick={() => setActiveTab('rubric')}
                  className="flex-1 px-4 py-3 text-[13px] font-medium transition"
                  style={{
                    backgroundColor: activeTab === 'rubric' ? 'var(--accent)' : 'var(--surface-subtle)',
                    color: activeTab === 'rubric' ? 'white' : 'var(--text-muted)',
                    borderTopLeftRadius: 'var(--radius)',
                    borderBottom: activeTab === 'rubric' ? 'none' : '1px solid var(--border)'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== 'rubric') {
                      e.currentTarget.style.backgroundColor = 'var(--bg)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== 'rubric') {
                      e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                    }
                  }}
                >
                  Rubric
                </button>
                <button
                  onClick={() => setActiveTab('summary')}
                  className="flex-1 px-4 py-3 text-[13px] font-medium transition"
                  style={{
                    backgroundColor: activeTab === 'summary' ? 'var(--accent)' : 'var(--surface-subtle)',
                    color: activeTab === 'summary' ? 'white' : 'var(--text-muted)',
                    borderBottom: activeTab === 'summary' ? 'none' : '1px solid var(--border)'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== 'summary') {
                      e.currentTarget.style.backgroundColor = 'var(--bg)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== 'summary') {
                      e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                    }
                  }}
                >
                  要約
                </button>
                <button
                  onClick={() => setActiveTab('comment')}
                  className="flex-1 px-4 py-3 text-[13px] font-medium transition"
                  style={{
                    backgroundColor: activeTab === 'comment' ? 'var(--accent)' : 'var(--surface-subtle)',
                    color: activeTab === 'comment' ? 'white' : 'var(--text-muted)',
                    borderTopRightRadius: 'var(--radius)',
                    borderBottom: activeTab === 'comment' ? 'none' : '1px solid var(--border)'
                  }}
                  onMouseEnter={(e) => {
                    if (activeTab !== 'comment') {
                      e.currentTarget.style.backgroundColor = 'var(--bg)'
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeTab !== 'comment') {
                      e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                    }
                  }}
                >
                  コメント
                </button>
              </div>

              {/* タブコンテンツ */}
              <div className="p-6">
                {activeTab === 'rubric' && (
                  <div>
                    <h3
                      className="text-[16px] font-semibold mb-4"
                      style={{ color: 'var(--text)' }}
                    >
                      Rubric採点結果
                    </h3>

                    <div className="space-y-4">
                      {['理解度', '論理性', '独自性', '実践性', '表現力'].map((category) => {
                        const item = history.feedback.rubric[category as keyof typeof history.feedback.rubric]
                        return (
                          <div
                            key={category}
                            className="p-3 rounded-[var(--radius-sm)]"
                            style={{
                              backgroundColor: 'var(--surface-subtle)',
                              border: '1px solid var(--border)'
                            }}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <span
                                className="text-[13px] font-medium"
                                style={{ color: 'var(--text)' }}
                              >
                                {category}
                              </span>
                              <span
                                className="text-[14px] font-semibold"
                                style={{ color: 'var(--accent)' }}
                              >
                                {item.score}/5
                              </span>
                            </div>
                            <p
                              className="text-[12px] leading-relaxed"
                              style={{ color: 'var(--text-muted)' }}
                            >
                              {item.reason}
                            </p>
                          </div>
                        )
                      })}

                      {/* 合計スコア */}
                      <div
                        className="p-4 rounded-[var(--radius-sm)] text-center mt-6"
                        style={{
                          backgroundColor: 'var(--bg)',
                          border: '2px solid var(--border)'
                        }}
                      >
                        <p
                          className="text-[12px] mb-1"
                          style={{ color: 'var(--text-muted)' }}
                        >
                          合計スコア
                        </p>
                        <p
                          className="text-[24px] font-bold"
                          style={{ color: 'var(--text)' }}
                        >
                          {totalScore}/25
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'summary' && (
                  <div>
                    <h3
                      className="text-[16px] font-semibold mb-4"
                      style={{ color: 'var(--text)' }}
                    >
                      レポート要約
                    </h3>

                    <div
                      className="p-4 rounded-[var(--radius-sm)] min-h-[300px] max-h-[400px] overflow-y-auto"
                      style={{
                        backgroundColor: 'var(--surface-subtle)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      <p
                        className="text-[13px] leading-relaxed whitespace-pre-wrap"
                        style={{ color: 'var(--text)' }}
                      >
                        {history.feedback.summary.formatted || history.feedback.summary.executive}
                      </p>
                    </div>

                    {history.report && (
                      <div className="mt-4 grid grid-cols-3 gap-3">
                        <div
                          className="p-3 rounded-[var(--radius-sm)] text-center"
                          style={{
                            backgroundColor: 'var(--bg)',
                            border: '1px solid var(--border)'
                          }}
                        >
                          <p
                            className="text-[11px] mb-1"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            レポート文字数
                          </p>
                          <p
                            className="text-[16px] font-semibold"
                            style={{ color: 'var(--text)' }}
                          >
                            {history.report.report_text.length}
                          </p>
                        </div>
                        <div
                          className="p-3 rounded-[var(--radius-sm)] text-center"
                          style={{
                            backgroundColor: 'var(--bg)',
                            border: '1px solid var(--border)'
                          }}
                        >
                          <p
                            className="text-[11px] mb-1"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            要約文字数
                          </p>
                          <p
                            className="text-[16px] font-semibold"
                            style={{ color: 'var(--text)' }}
                          >
                            {(history.feedback.summary.formatted || history.feedback.summary.executive).length}
                          </p>
                        </div>
                        <div
                          className="p-3 rounded-[var(--radius-sm)] text-center"
                          style={{
                            backgroundColor: 'var(--bg)',
                            border: '1px solid var(--border)'
                          }}
                        >
                          <p
                            className="text-[11px] mb-1"
                            style={{ color: 'var(--text-muted)' }}
                          >
                            圧縮率
                          </p>
                          <p
                            className="text-[16px] font-semibold"
                            style={{ color: 'var(--text)' }}
                          >
                            {Math.round(((history.feedback.summary.formatted || history.feedback.summary.executive).length / history.report.report_text.length) * 100)}%
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeTab === 'comment' && (
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3
                        className="text-[16px] font-semibold"
                        style={{ color: 'var(--text)' }}
                      >
                        生成コメント
                      </h3>
                      <button
                        onClick={handleCopyComment}
                        className="px-3 py-1.5 rounded-[var(--radius-sm)] text-[12px] font-medium transition"
                        style={{
                          backgroundColor: 'var(--surface-subtle)',
                          color: 'var(--text)',
                          border: '1px solid var(--border)'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = 'var(--bg)'
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                        }}
                      >
                        コピー
                      </button>
                    </div>

                    <div
                      className="p-4 rounded-[var(--radius-sm)] min-h-[300px] max-h-[450px] overflow-y-auto"
                      style={{
                        backgroundColor: 'var(--surface-subtle)',
                        border: '1px solid var(--border)'
                      }}
                    >
                      <p
                        className="text-[13px] leading-relaxed whitespace-pre-wrap"
                        style={{ color: 'var(--text)' }}
                      >
                        {history.feedback.edited_comment || history.feedback.ai_comment}
                      </p>
                    </div>

                    <div className="mt-2 flex justify-between items-center">
                      <p
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {history.feedback.llm_used ? 'AI生成（GPT-4o-mini）' : 'ルールベース生成'}
                      </p>
                      <p
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {(history.feedback.edited_comment || history.feedback.ai_comment).length}文字
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
