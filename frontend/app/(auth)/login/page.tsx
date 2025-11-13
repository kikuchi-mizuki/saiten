'use client'

/**
 * ログイン画面
 *
 * Google OAuth認証を使用してログインを行います。
 * 初回ログイン時に利用規約への同意を求めます。
 */

import { useState } from 'react'
import { supabase } from '@/lib/supabase'
import Link from 'next/link'

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [agreed, setAgreed] = useState(false)

  /**
   * Googleログイン処理
   */
  async function handleGoogleLogin() {
    if (!agreed) {
      setError('利用規約に同意してください')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      })

      if (error) {
        throw error
      }
    } catch (err) {
      console.error('Login error:', err)
      setError('ログインに失敗しました。もう一度お試しください。')
      setIsLoading(false)
    }
  }

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ backgroundColor: 'var(--bg)' }}
    >
      <div
        className="w-full max-w-md p-8 rounded-[var(--radius)] shadow-sm"
        style={{ backgroundColor: 'var(--surface)' }}
      >
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <h1
            className="text-[22px] font-semibold mb-2"
            style={{ color: 'var(--text)' }}
          >
            教授コメント自動化ボット
          </h1>
          <p
            className="text-[13px]"
            style={{ color: 'var(--text-muted)' }}
          >
            経営戦略論のレポートコメント作成をサポート
          </p>
        </div>

        {/* エラーメッセージ */}
        {error && (
          <div
            className="mb-6 p-3 rounded-[var(--radius-sm)] text-[13px]"
            style={{
              backgroundColor: '#FEE2E2',
              color: 'var(--danger)',
              border: '1px solid var(--danger)'
            }}
          >
            {error}
          </div>
        )}

        {/* Googleログインボタン */}
        <button
          onClick={handleGoogleLogin}
          disabled={isLoading}
          className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-[var(--radius-sm)] font-medium text-[15px] transition disabled:opacity-50 disabled:cursor-not-allowed mb-6"
          style={{
            backgroundColor: isLoading ? 'var(--text-muted-light)' : 'var(--accent)',
            color: '#FFFFFF',
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = 'var(--accent-hover)'
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading) {
              e.currentTarget.style.backgroundColor = 'var(--accent)'
            }
          }}
        >
          {isLoading ? (
            <>
              <svg
                className="animate-spin h-5 w-5"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
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
              ログイン中...
            </>
          ) : (
            <>
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              Googleでログイン
            </>
          )}
        </button>

        {/* 利用規約同意チェックボックス */}
        <div className="mb-6">
          <label
            className="flex items-start gap-2 cursor-pointer"
            style={{ color: 'var(--text-muted)' }}
          >
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="mt-1 w-4 h-4 rounded accent-blue-600"
            />
            <span className="text-[13px] leading-relaxed">
              <Link
                href="/policy"
                className="underline"
                style={{ color: 'var(--accent)' }}
                target="_blank"
              >
                利用規約
              </Link>
              に同意します
            </span>
          </label>
        </div>

        {/* 注意事項 */}
        <div
          className="p-4 rounded-[var(--radius-sm)] text-[12px] leading-relaxed space-y-2"
          style={{
            backgroundColor: 'var(--surface-subtle)',
            color: 'var(--text-muted)',
            border: '1px solid var(--border)'
          }}
        >
          <p className="font-medium" style={{ color: 'var(--text)' }}>
            ログインすることで、以下に同意したものとします：
          </p>
          <ul className="list-disc list-inside space-y-1 ml-2">
            <li>レポート本文（個人情報をマスキング後）がOpenAI APIに送信されること</li>
            <li>データがSupabaseに保存されること</li>
            <li>データは暗号化されて保存されること</li>
            <li>ユーザーはいつでもデータを削除できること</li>
          </ul>
        </div>

        {/* フッター */}
        <div
          className="mt-6 text-center text-[12px]"
          style={{ color: 'var(--text-muted-light)' }}
        >
          <p>
            Phase 1 MVP - 経営戦略論教授専用
          </p>
        </div>
      </div>
    </div>
  )
}
