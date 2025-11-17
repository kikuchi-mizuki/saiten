'use client'

/**
 * ダッシュボードページ（メイン画面）
 *
 * 認証後のメイン画面。将来的にはレポートコメント生成機能を実装します。
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/auth'
import { generateComment, getStats, type GenerateResponse, type StatsResponse } from '@/lib/api'
import { saveReport, saveFeedback, saveQualityRating } from '@/lib/database'
import type { User } from '@supabase/supabase-js'

type TabType = 'rubric' | 'summary' | 'comment'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<TabType>('rubric')

  // フォーム入力状態
  const [reportType, setReportType] = useState<'reflection' | 'final'>('reflection')
  const [reportText, setReportText] = useState('')
  const [studentId, setStudentId] = useState('')  // 学生ID（データベース保存用）

  // 生成結果状態
  const [result, setResult] = useState<GenerateResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generateError, setGenerateError] = useState<string | null>(null)

  // コメント編集状態
  const [editedComment, setEditedComment] = useState('')

  // 品質評価用の状態
  const [generateTime, setGenerateTime] = useState<number | null>(null) // 生成完了時刻
  const [feedbackId, setFeedbackId] = useState<string | null>(null) // 保存されたfeedbackのID
  const [showSurvey, setShowSurvey] = useState(false) // 満足度アンケートの表示
  const [satisfactionScore, setSatisfactionScore] = useState<number | null>(null)
  const [feedbackText, setFeedbackText] = useState('')

  // 統計情報の状態
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [showStats, setShowStats] = useState(false)

  /**
   * コメントをクリップボードにコピー
   */
  function handleCopyComment() {
    if (editedComment) {
      navigator.clipboard.writeText(editedComment)
      alert('コメントをクリップボードにコピーしました')
    }
  }

  /**
   * コメント保存処理（手直し時間測定 + 満足度アンケート表示）
   */
  async function handleSaveComment() {
    if (!feedbackId || !generateTime) {
      alert('コメントを保存できません')
      return
    }

    // 手直し時間を計算（秒単位）
    const editTimeSeconds = Math.floor((Date.now() - generateTime) / 1000)

    // 満足度アンケートを表示
    setShowSurvey(true)

    // 一時的に手直し時間だけ保存（満足度はアンケート送信時に保存）
    try {
      await saveQualityRating(feedbackId, editTimeSeconds, 0, '')
    } catch (error) {
      console.error('Save edit time error:', error)
    }
  }

  /**
   * 満足度アンケート送信
   */
  async function handleSubmitSurvey() {
    if (!feedbackId || !satisfactionScore) {
      alert('満足度を選択してください')
      return
    }

    try {
      // 手直し時間を再計算
      const editTimeSeconds = generateTime ? Math.floor((Date.now() - generateTime) / 1000) : 0

      // 満足度を保存
      await saveQualityRating(
        feedbackId,
        editTimeSeconds,
        satisfactionScore,
        feedbackText
      )

      alert('フィードバックを保存しました')
      setShowSurvey(false)

      // フォームをリセット
      setSatisfactionScore(null)
      setFeedbackText('')
      setStudentId('')
      setReportText('')
      setResult(null)
      setEditedComment('')
      setGenerateTime(null)
      setFeedbackId(null)
    } catch (error) {
      console.error('Submit survey error:', error)
      alert('フィードバックの保存に失敗しました')
    }
  }

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
      await loadStats()
      setIsLoading(false)
    }

    checkAuth()
  }, [router])

  /**
   * 統計情報を読み込み
   */
  async function loadStats() {
    try {
      const statsData = await getStats()
      setStats(statsData)
    } catch (error) {
      console.error('Load stats error:', error)
      // エラーは無視（統計情報は必須ではない）
    }
  }

  /**
   * コメント生成処理
   */
  async function handleGenerate() {
    // バリデーション
    if (!reportText.trim()) {
      setGenerateError('レポート本文を入力してください')
      return
    }

    setIsGenerating(true)
    setGenerateError(null)

    try {
      // 1. AIコメント生成
      const response = await generateComment(reportText, reportType)
      setResult(response)
      setEditedComment(response.ai_comment)

      // 生成完了時刻を記録（手直し時間測定用）
      setGenerateTime(Date.now())

      // 2. データベースに保存
      try {
        // レポートを保存
        const savedReport = await saveReport(studentId, reportText)

        if (savedReport) {
          // コメント生成結果を保存
          const savedFeedback = await saveFeedback(
            savedReport.id,
            response.ai_comment,
            response.rubric,
            response.summary,
            response.llm_used,
            'gpt-4o-mini',
            response.used_refs
          )

          // feedbackIdを保存（品質評価用）
          if (savedFeedback) {
            setFeedbackId(savedFeedback.id)
          }
        }
      } catch (saveError) {
        console.error('Save error:', saveError)
        // 保存エラーは警告のみ表示（生成は成功しているため）
        alert('データの保存に失敗しました。履歴には記録されません。')
      }

      // 生成成功時は自動的にコメント編集タブに切り替え
      setActiveTab('comment')
    } catch (error) {
      console.error('Generate error:', error)
      setGenerateError(
        error instanceof Error
          ? error.message
          : 'コメント生成に失敗しました。もう一度お試しください。'
      )
    } finally {
      setIsGenerating(false)
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
            {/* 履歴リンク */}
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
              履歴
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

      {/* 統計情報セクション */}
      {stats && (
        <div className="max-w-[1400px] mx-auto px-6 py-4">
          <div
            className="p-4 rounded-[var(--radius)]"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
          >
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-[14px] font-semibold" style={{ color: 'var(--text)' }}>
                統計情報
              </h2>
              <button
                onClick={() => setShowStats(!showStats)}
                className="text-[12px] px-3 py-1 rounded-[var(--radius-sm)]"
                style={{
                  backgroundColor: 'var(--surface-subtle)',
                  color: 'var(--text)',
                }}
              >
                {showStats ? '非表示' : '表示'}
              </button>
            </div>

            {showStats && (
              <div className="grid grid-cols-4 gap-4">
                {/* 総コメント生成数 */}
                <div className="p-3 rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--bg)' }}>
                  <p className="text-[11px] mb-1" style={{ color: 'var(--text-muted)' }}>
                    総コメント生成数
                  </p>
                  <p className="text-[20px] font-semibold" style={{ color: 'var(--accent)' }}>
                    {stats.total_feedbacks}
                  </p>
                </div>

                {/* 平均Rubric点数 */}
                <div className="p-3 rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--bg)' }}>
                  <p className="text-[11px] mb-1" style={{ color: 'var(--text-muted)' }}>
                    平均Rubric点数
                  </p>
                  <div className="space-y-1">
                    {Object.entries(stats.avg_rubric_scores).map(([category, score]) => (
                      <div key={category} className="flex justify-between items-center">
                        <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
                          {category}
                        </span>
                        <span className="text-[12px] font-medium" style={{ color: 'var(--text)' }}>
                          {score.toFixed(1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 平均手直し時間 */}
                <div className="p-3 rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--bg)' }}>
                  <p className="text-[11px] mb-1" style={{ color: 'var(--text-muted)' }}>
                    平均手直し時間
                  </p>
                  <p className="text-[20px] font-semibold" style={{ color: 'var(--accent)' }}>
                    {stats.avg_edit_time_seconds !== null
                      ? `${Math.floor(stats.avg_edit_time_seconds / 60)}分${Math.floor(
                          stats.avg_edit_time_seconds % 60
                        )}秒`
                      : 'N/A'}
                  </p>
                </div>

                {/* 平均満足度 */}
                <div className="p-3 rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--bg)' }}>
                  <p className="text-[11px] mb-1" style={{ color: 'var(--text-muted)' }}>
                    平均満足度
                  </p>
                  <p className="text-[20px] font-semibold" style={{ color: 'var(--accent)' }}>
                    {stats.avg_satisfaction_score !== null
                      ? `${stats.avg_satisfaction_score.toFixed(1)} / 5.0`
                      : 'N/A'}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* メインコンテンツ: 7:5の2カラムレイアウト */}
      <main className="max-w-[1400px] mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* 左カラム（7/12） - レポート入力フォーム */}
          <div className="col-span-7">
            <div
              className="p-6 rounded-[var(--radius)]"
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)'
              }}
            >
              <h2
                className="text-[18px] font-semibold mb-4"
                style={{ color: 'var(--text)' }}
              >
                レポート入力
              </h2>

              {/* レポートタイプ選択 */}
              <div className="mb-4">
                <label
                  className="block text-[13px] font-medium mb-2"
                  style={{ color: 'var(--text)' }}
                >
                  レポートタイプ
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      value="reflection"
                      checked={reportType === 'reflection'}
                      onChange={(e) => setReportType(e.target.value as 'reflection' | 'final')}
                      disabled={isGenerating}
                      className="mr-2"
                      style={{
                        cursor: isGenerating ? 'not-allowed' : 'pointer'
                      }}
                    />
                    <span
                      className="text-[14px]"
                      style={{
                        color: 'var(--text)',
                        opacity: isGenerating ? 0.6 : 1
                      }}
                    >
                      振り返りレポート
                    </span>
                  </label>
                  <label className="flex items-center cursor-pointer">
                    <input
                      type="radio"
                      value="final"
                      checked={reportType === 'final'}
                      onChange={(e) => setReportType(e.target.value as 'reflection' | 'final')}
                      disabled={isGenerating}
                      className="mr-2"
                      style={{
                        cursor: isGenerating ? 'not-allowed' : 'pointer'
                      }}
                    />
                    <span
                      className="text-[14px]"
                      style={{
                        color: 'var(--text)',
                        opacity: isGenerating ? 0.6 : 1
                      }}
                    >
                      最終レポート
                    </span>
                  </label>
                </div>
              </div>

              {/* レポート本文入力 */}
              <div className="mb-4">
                <label
                  className="block text-[13px] font-medium mb-2"
                  style={{ color: 'var(--text)' }}
                >
                  レポート本文
                </label>
                <textarea
                  placeholder="レポートの内容を入力してください..."
                  rows={16}
                  value={reportText}
                  onChange={(e) => setReportText(e.target.value)}
                  disabled={isGenerating}
                  className="w-full px-3 py-2 rounded-[var(--radius-sm)] text-[14px] resize-none"
                  style={{
                    backgroundColor: 'var(--bg)',
                    border: '1px solid var(--border)',
                    color: 'var(--text)',
                    opacity: isGenerating ? 0.6 : 1
                  }}
                />
              </div>

              {/* エラーメッセージ */}
              {generateError && (
                <div
                  className="mb-4 p-3 rounded-[var(--radius-sm)] text-[13px]"
                  style={{
                    backgroundColor: '#FEE2E2',
                    border: '1px solid #FCA5A5',
                    color: '#DC2626'
                  }}
                >
                  {generateError}
                </div>
              )}

              {/* 送信ボタン */}
              <button
                onClick={handleGenerate}
                disabled={isGenerating || !reportText.trim()}
                className="w-full py-3 rounded-[var(--radius-sm)] text-[14px] font-medium transition"
                style={{
                  backgroundColor: isGenerating || !reportText.trim() ? 'var(--border)' : 'var(--accent)',
                  color: 'white',
                  cursor: isGenerating || !reportText.trim() ? 'not-allowed' : 'pointer',
                  opacity: isGenerating || !reportText.trim() ? 0.6 : 1
                }}
                onMouseEnter={(e) => {
                  if (!isGenerating && reportText.trim()) {
                    e.currentTarget.style.opacity = '0.9'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isGenerating && reportText.trim()) {
                    e.currentTarget.style.opacity = '1'
                  }
                }}
              >
                {isGenerating ? '生成中...' : 'コメント生成'}
              </button>
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
                  コメント編集
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

                    {result ? (
                      <div className="space-y-4">
                        {/* Rubric評価項目 */}
                        {['理解度', '論理性', '独自性', '実践性', '表現力'].map((category) => {
                          const item = result.rubric[category as keyof typeof result.rubric]
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
                            {Object.values(result.rubric).reduce((sum, item) => sum + item.score, 0)}/25
                          </p>
                        </div>
                      </div>
                    ) : (
                      <p
                        className="text-[13px] text-center py-12"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        レポートを入力して「コメント生成」ボタンを押してください
                      </p>
                    )}
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

                    {result ? (
                      <>
                        {/* 要約表示エリア */}
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
                            {result.summary.formatted || result.summary.executive}
                          </p>
                        </div>

                        {/* 要約の詳細情報 */}
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
                              {reportText.length}
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
                              {(result.summary.formatted || result.summary.executive).length}
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
                              {Math.round(((result.summary.formatted || result.summary.executive).length / reportText.length) * 100)}%
                            </p>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div
                        className="p-4 rounded-[var(--radius-sm)] min-h-[300px] flex items-center justify-center"
                        style={{
                          backgroundColor: 'var(--surface-subtle)',
                          border: '1px solid var(--border)'
                        }}
                      >
                        <p
                          className="text-[13px] text-center"
                          style={{ color: 'var(--text-muted)' }}
                        >
                          レポートを入力して「コメント生成」ボタンを押すと、
                          <br />
                          AI生成された要約がここに表示されます
                        </p>
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
                        コメント編集
                      </h3>
                      {result && (
                        <div className="flex gap-2">
                          <button
                            onClick={handleCopyComment}
                            disabled={!editedComment}
                            className="px-3 py-1.5 rounded-[var(--radius-sm)] text-[12px] font-medium transition"
                            style={{
                              backgroundColor: 'var(--surface-subtle)',
                              color: 'var(--text)',
                              border: '1px solid var(--border)',
                              opacity: !editedComment ? 0.5 : 1,
                              cursor: !editedComment ? 'not-allowed' : 'pointer'
                            }}
                            onMouseEnter={(e) => {
                              if (editedComment) {
                                e.currentTarget.style.backgroundColor = 'var(--bg)'
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (editedComment) {
                                e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                              }
                            }}
                          >
                            コピー
                          </button>
                          <button
                            onClick={handleSaveComment}
                            disabled={!editedComment || !feedbackId}
                            className="px-3 py-1.5 rounded-[var(--radius-sm)] text-[12px] font-medium transition"
                            style={{
                              backgroundColor: !editedComment || !feedbackId ? 'var(--border)' : 'var(--accent)',
                              color: 'white',
                              opacity: !editedComment || !feedbackId ? 0.5 : 1,
                              cursor: !editedComment || !feedbackId ? 'not-allowed' : 'pointer'
                            }}
                            onMouseEnter={(e) => {
                              if (editedComment && feedbackId) {
                                e.currentTarget.style.opacity = '0.9'
                              }
                            }}
                            onMouseLeave={(e) => {
                              if (editedComment && feedbackId) {
                                e.currentTarget.style.opacity = '1'
                              }
                            }}
                          >
                            保存
                          </button>
                        </div>
                      )}
                    </div>

                    {/* コメント編集エリア */}
                    <textarea
                      placeholder="レポートを入力して「コメント生成」ボタンを押すと、生成されたコメントがここに表示されます。編集して保存できます。"
                      rows={14}
                      value={editedComment}
                      onChange={(e) => setEditedComment(e.target.value)}
                      className="w-full px-3 py-3 rounded-[var(--radius-sm)] text-[13px] leading-relaxed resize-none"
                      style={{
                        backgroundColor: 'var(--surface-subtle)',
                        border: '1px solid var(--border)',
                        color: 'var(--text)'
                      }}
                    />

                    {/* 文字数カウント */}
                    <div className="mt-2 flex justify-between items-center">
                      <p
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {result ? 'AI生成後、自由に編集できます' : 'レポートを入力してコメント生成してください'}
                      </p>
                      <p
                        className="text-[11px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        {editedComment.length}文字
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* 満足度アンケートモーダル */}
      {showSurvey && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
          onClick={() => setShowSurvey(false)}
        >
          <div
            className="w-full max-w-md p-6 rounded-[var(--radius)]"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              className="text-[18px] font-semibold mb-4"
              style={{ color: 'var(--text)' }}
            >
              品質評価アンケート
            </h2>
            <p
              className="text-[13px] mb-6"
              style={{ color: 'var(--text-muted)' }}
            >
              生成されたコメントの品質を評価してください。
              今後の改善に役立てます。
            </p>

            {/* 満足度 */}
            <div className="mb-6">
              <label
                className="block text-[13px] font-medium mb-3"
                style={{ color: 'var(--text)' }}
              >
                満足度（1-5点）
              </label>
              <div className="flex gap-2 justify-center">
                {[1, 2, 3, 4, 5].map((score) => (
                  <button
                    key={score}
                    onClick={() => setSatisfactionScore(score)}
                    className="w-12 h-12 rounded-full text-[16px] font-semibold transition"
                    style={{
                      backgroundColor:
                        satisfactionScore === score
                          ? 'var(--accent)'
                          : 'var(--surface-subtle)',
                      color:
                        satisfactionScore === score ? 'white' : 'var(--text)',
                      border: '1px solid var(--border)',
                    }}
                  >
                    {score}
                  </button>
                ))}
              </div>
            </div>

            {/* フィードバックテキスト */}
            <div className="mb-6">
              <label
                className="block text-[13px] font-medium mb-2"
                style={{ color: 'var(--text)' }}
              >
                改善点・コメント（任意）
              </label>
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 rounded-[var(--radius-sm)] text-[13px]"
                style={{
                  backgroundColor: 'var(--bg)',
                  color: 'var(--text)',
                  border: '1px solid var(--border)',
                }}
                placeholder="改善してほしい点、良かった点など..."
              />
            </div>

            {/* ボタン */}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowSurvey(false)}
                className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
                style={{
                  backgroundColor: 'var(--surface-subtle)',
                  color: 'var(--text)',
                  border: '1px solid var(--border)',
                }}
              >
                キャンセル
              </button>
              <button
                type="button"
                onClick={handleSubmitSurvey}
                disabled={!satisfactionScore}
                className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
                style={{
                  backgroundColor: satisfactionScore
                    ? 'var(--accent)'
                    : 'var(--border)',
                  color: 'white',
                  opacity: satisfactionScore ? 1 : 0.5,
                  cursor: satisfactionScore ? 'pointer' : 'not-allowed',
                }}
              >
                送信
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
