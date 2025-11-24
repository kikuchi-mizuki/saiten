'use client'

/**
 * 履歴一覧ページ
 *
 * コメント生成の履歴を表示します。
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/auth'
import { getHistoryList, exportHistoryCSV, type HistoryItem } from '@/lib/database'
import type { User } from '@supabase/supabase-js'

export default function HistoryPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [isExporting, setIsExporting] = useState(false)

  useEffect(() => {
    // 認証状態を確認
    async function checkAuth() {
      const currentUser = await getCurrentUser()

      if (!currentUser) {
        router.push('/login')
        return
      }

      setUser(currentUser)
      await loadHistory()
      setIsLoading(false)
    }

    checkAuth()
  }, [router])

  /**
   * 履歴を読み込み
   */
  async function loadHistory() {
    try {
      const data = await getHistoryList(50)
      setHistory(data)
    } catch (error) {
      console.error('Load history error:', error)
      alert('履歴の読み込みに失敗しました')
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
   * CSV形式でエクスポート
   */
  async function handleExportCSV() {
    setIsExporting(true)
    try {
      const csvData = await exportHistoryCSV()
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `history_${new Date().toISOString().slice(0, 10)}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export CSV error:', error)
      alert('エクスポートに失敗しました')
    } finally {
      setIsExporting(false)
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
            履歴
          </h1>

          <div className="flex items-center gap-4">
            {/* ダッシュボードリンク */}
            <Link
              href="/dashboard"
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
              ダッシュボード
            </Link>

            {/* 参照例管理リンク */}
            <Link
              href="/references"
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
              参照例
            </Link>

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

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* エクスポートボタン */}
        <div className="flex justify-end gap-3 mb-6">
          <button
            onClick={handleExportCSV}
            disabled={isExporting || history.length === 0}
            className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
            style={{
              backgroundColor: isExporting || history.length === 0 ? 'var(--border)' : 'var(--surface-subtle)',
              color: 'var(--text)',
              border: '1px solid var(--border)',
              opacity: isExporting || history.length === 0 ? 0.5 : 1,
              cursor: isExporting || history.length === 0 ? 'not-allowed' : 'pointer'
            }}
            onMouseEnter={(e) => {
              if (!isExporting && history.length > 0) {
                e.currentTarget.style.backgroundColor = 'var(--bg)'
              }
            }}
            onMouseLeave={(e) => {
              if (!isExporting && history.length > 0) {
                e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
              }
            }}
          >
            CSV出力
          </button>
        </div>

        {/* 履歴一覧 */}
        {history.length === 0 ? (
          <div
            className="p-12 rounded-[var(--radius)] text-center"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)'
            }}
          >
            <p
              className="text-[15px]"
              style={{ color: 'var(--text-muted)' }}
            >
              履歴はまだありません。
              <br />
              ダッシュボードでコメントを生成すると、ここに表示されます。
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {history.map((item) => {
              const totalScore = Object.values(item.feedback.rubric).reduce(
                (sum, rubricItem) => sum + rubricItem.score,
                0
              )

              return (
                <Link
                  key={item.feedback.id}
                  href={`/history/${item.feedback.id}`}
                  className="block p-6 rounded-[var(--radius)] transition"
                  style={{
                    backgroundColor: 'var(--surface)',
                    border: '1px solid var(--border)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--surface)'
                  }}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <p
                        className="text-[12px] mb-1"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {new Date(item.feedback.created_at).toLocaleString('ja-JP')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p
                        className="text-[12px] mb-1"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        Rubric合計
                      </p>
                      <p
                        className="text-[18px] font-semibold"
                        style={{ color: 'var(--accent)' }}
                      >
                        {totalScore}/25
                      </p>
                    </div>
                  </div>
                  {item.report && (
                    <p
                      className="text-[13px] line-clamp-2"
                      style={{ color: 'var(--text-muted)' }}
                    >
                      {item.report.report_text}
                    </p>
                  )}
                </Link>
              )
            })}
          </div>
        )}
      </main>
    </div>
  )
}
