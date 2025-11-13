'use client'

/**
 * ダッシュボードページ（メイン画面）
 *
 * 認証後のメイン画面。将来的にはレポートコメント生成機能を実装します。
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getCurrentUser, signOut } from '@/lib/auth'
import type { User } from '@supabase/supabase-js'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // 認証状態を確認
    async function checkAuth() {
      const currentUser = await getCurrentUser()

      if (!currentUser) {
        // 未認証の場合はログインページにリダイレクト
        router.push('/login')
        return
      }

      setUser(currentUser)
      setIsLoading(false)
    }

    checkAuth()
  }, [router])

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
            教授コメント自動化ボット
          </h1>

          <div className="flex items-center gap-4">
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
        <div
          className="p-8 rounded-[var(--radius)] text-center"
          style={{
            backgroundColor: 'var(--surface)',
            border: '1px solid var(--border)'
          }}
        >
          <h2
            className="text-[22px] font-semibold mb-4"
            style={{ color: 'var(--text)' }}
          >
            ようこそ、{user?.user_metadata?.full_name || 'ユーザー'}さん
          </h2>
          <p
            className="text-[15px] mb-6"
            style={{ color: 'var(--text-muted)' }}
          >
            Week 2: 認証機能の実装が完了しました。
          </p>

          <div
            className="inline-block p-4 rounded-[var(--radius-sm)] text-left"
            style={{
              backgroundColor: 'var(--surface-subtle)',
              border: '1px solid var(--border)'
            }}
          >
            <p
              className="text-[14px] font-medium mb-2"
              style={{ color: 'var(--text)' }}
            >
              📋 次の実装予定（Week 3-4）:
            </p>
            <ul
              className="text-[13px] space-y-1 list-disc list-inside"
              style={{ color: 'var(--text-muted)' }}
            >
              <li>レポート入力フォーム（左カラム）</li>
              <li>結果表示エリア（右カラム、7:5レイアウト）</li>
              <li>Rubric表示タブ</li>
              <li>要約表示タブ</li>
              <li>コメント編集タブ</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  )
}
