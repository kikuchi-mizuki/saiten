'use client'

/**
 * 参照例管理ページ
 *
 * 教授の過去のコメントを参照例として管理します。
 */

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser, signOut } from '@/lib/auth'
import {
  getAllReferences,
  createReference,
  updateReference,
  deleteReference,
  type ReferenceExample,
  type ReferenceCreateRequest,
} from '@/lib/references'
import type { User } from '@supabase/supabase-js'

type ModalMode = 'add' | 'edit' | null

export default function ReferencesPage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [references, setReferences] = useState<ReferenceExample[]>([])
  const [filterType, setFilterType] = useState<'all' | 'reflection' | 'final'>('all')
  const [searchQuery, setSearchQuery] = useState('')

  // Phase 2: ページネーション対応
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [totalCount, setTotalCount] = useState(0)
  const perPage = 20

  // モーダル状態
  const [modalMode, setModalMode] = useState<ModalMode>(null)
  const [editingReference, setEditingReference] = useState<ReferenceExample | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // フォーム状態
  const [formType, setFormType] = useState<'reflection' | 'final'>('reflection')
  const [formText, setFormText] = useState('')
  const [formTags, setFormTags] = useState('')
  const [autoTagged, setAutoTagged] = useState(false)  // Phase 2: LLM自動タグ付け


  useEffect(() => {
    async function checkAuth() {
      const currentUser = await getCurrentUser()

      if (!currentUser) {
        router.push('/login')
        return
      }

      setUser(currentUser)
      await loadReferences()
      setIsLoading(false)
    }

    checkAuth()
  }, [router])

  // Phase 2: サーバーサイド検索・フィルタ・ページネーション
  useEffect(() => {
    if (user) {
      loadReferences()
    }
  }, [user, filterType, searchQuery, currentPage])

  async function loadReferences() {
    try {
      const data = await getAllReferences({
        search: searchQuery || undefined,
        type: filterType !== 'all' ? filterType : undefined,
        page: currentPage,
        per_page: perPage,
        sort: 'created_desc',
      })
      setReferences(data.references)
      setTotalPages(data.total_pages)
      setTotalCount(data.total)
    } catch (error) {
      console.error('Load references error:', error)
      alert('参照例の読み込みに失敗しました')
    }
  }

  async function handleSignOut() {
    try {
      await signOut()
      router.push('/login')
    } catch (error) {
      console.error('Sign out error:', error)
      alert('ログアウトに失敗しました')
    }
  }

  function openAddModal() {
    setModalMode('add')
    setFormType('reflection')
    setFormText('')
    setFormTags('')
  }

  function openEditModal(reference: ReferenceExample) {
    setModalMode('edit')
    setEditingReference(reference)
    setFormType(reference.type)
    setFormText(reference.text)
    setFormTags(reference.tags.join(', '))
  }

  function closeModal() {
    setModalMode(null)
    setEditingReference(null)
    setFormType('reflection')
    setFormText('')
    setFormTags('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      const tags = formTags
        .split(',')
        .map((t) => t.trim())
        .filter((t) => t)

      if (modalMode === 'add') {
        const data: ReferenceCreateRequest = {
          type: formType,
          text: formText,
          tags: tags,
          source: 'professor_custom',
        }
        await createReference(data)
        alert('参照例を追加しました')
      } else if (modalMode === 'edit' && editingReference) {
        await updateReference(editingReference.id, {
          type: formType,
          text: formText,
          tags: tags,
        })
        alert('参照例を更新しました')
      }

      await loadReferences()
      closeModal()
    } catch (error) {
      console.error('Submit error:', error)
      alert('操作に失敗しました')
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleDelete(id: string) {
    if (!confirm('この参照例を削除しますか？この操作は取り消せません。')) {
      return
    }

    try {
      await deleteReference(id)
      alert('参照例を削除しました')
      await loadReferences()
    } catch (error) {
      console.error('Delete error:', error)
      alert('削除に失敗しました')
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
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* ヘッダー */}
      <header
        className="border-b"
        style={{
          backgroundColor: 'var(--surface)',
          borderColor: 'var(--border)',
        }}
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1
            className="text-[18px] font-semibold"
            style={{ color: 'var(--text)' }}
          >
            参照例管理
          </h1>

          <div className="flex items-center gap-4">
            <Link
              href="/references/upload"
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--accent)',
                color: 'white',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1'
              }}
            >
              📎 ファイルアップロード
            </Link>

            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--surface-subtle)',
                color: 'var(--text)',
                border: '1px solid var(--border)',
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

            <Link
              href="/history"
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--surface-subtle)',
                color: 'var(--text)',
                border: '1px solid var(--border)',
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

            <div className="text-right">
              <p
                className="text-[13px] font-medium"
                style={{ color: 'var(--text)' }}
              >
                {user?.email}
              </p>
              <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                ログイン中
              </p>
            </div>

            <button
              onClick={handleSignOut}
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--surface-subtle)',
                color: 'var(--text-muted)',
                border: '1px solid var(--border)',
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
        {/* アクションバー */}
        <div className="flex justify-between items-center mb-6">
          <div className="flex gap-3">
            <button
              onClick={openAddModal}
              className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
              style={{
                backgroundColor: 'var(--accent)',
                color: 'white',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '0.9'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '1'
              }}
            >
              + 参照例を追加
            </button>
          </div>

          <div className="flex items-center gap-3">
            {/* タイプフィルター */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as any)}
              className="px-3 py-2 rounded-[var(--radius-sm)] text-[13px]"
              style={{
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                border: '1px solid var(--border)',
              }}
            >
              <option value="all">全て</option>
              <option value="reflection">振り返り</option>
              <option value="final">最終レポート</option>
            </select>

            {/* 検索 */}
            <input
              type="text"
              placeholder="検索..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="px-3 py-2 rounded-[var(--radius-sm)] text-[13px] w-64"
              style={{
                backgroundColor: 'var(--surface)',
                color: 'var(--text)',
                border: '1px solid var(--border)',
              }}
            />
          </div>
        </div>

        {/* 統計 */}
        <div className="mb-6 flex gap-4">
          <div
            className="px-4 py-3 rounded-[var(--radius-sm)]"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
          >
            <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
              全参照例数
            </p>
            <p
              className="text-[20px] font-semibold"
              style={{ color: 'var(--accent)' }}
            >
              {references.length}件
            </p>
          </div>
          <div
            className="px-4 py-3 rounded-[var(--radius-sm)]"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
          >
            <p className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
              表示中
            </p>
            <p
              className="text-[20px] font-semibold"
              style={{ color: 'var(--accent)' }}
            >
              {totalCount}件（ページ {currentPage}/{totalPages}）
            </p>
          </div>
        </div>

        {/* 参照例一覧 */}
        {references.length === 0 ? (
          <div
            className="p-12 rounded-[var(--radius)] text-center"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
          >
            <p className="text-[15px]" style={{ color: 'var(--text-muted)' }}>
              {searchQuery || filterType !== 'all'
                ? '条件に一致する参照例がありません'
                : '参照例はまだありません。「+ 参照例を追加」ボタンから追加してください。'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {references.map((ref) => (
              <div
                key={ref.id}
                className="p-6 rounded-[var(--radius)]"
                style={{
                  backgroundColor: 'var(--surface)',
                  border: '1px solid var(--border)',
                }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span
                        className="px-2 py-1 rounded text-[11px] font-medium"
                        style={{
                          backgroundColor:
                            ref.type === 'reflection'
                              ? 'var(--accent)'
                              : 'var(--text-muted)',
                          color: 'white',
                        }}
                      >
                        {ref.type === 'reflection' ? '振り返り' : '最終'}
                      </span>
                      <span
                        className="text-[12px]"
                        style={{ color: 'var(--text-muted)' }}
                      >
                        ID: {ref.id}
                      </span>
                    </div>
                    <p
                      className="text-[14px] mb-2"
                      style={{ color: 'var(--text)' }}
                    >
                      {ref.text.substring(0, 200)}
                      {ref.text.length > 200 ? '...' : ''}
                    </p>
                    {ref.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {ref.tags.map((tag, i) => (
                          <span
                            key={i}
                            className="px-2 py-1 rounded text-[11px]"
                            style={{
                              backgroundColor: 'var(--bg)',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <button
                      onClick={() => openEditModal(ref)}
                      className="px-3 py-1 rounded text-[12px] transition"
                      style={{
                        backgroundColor: 'var(--surface-subtle)',
                        color: 'var(--text)',
                        border: '1px solid var(--border)',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--bg)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor =
                          'var(--surface-subtle)'
                      }}
                    >
                      編集
                    </button>
                    <button
                      onClick={() => handleDelete(ref.id)}
                      className="px-3 py-1 rounded text-[12px] transition"
                      style={{
                        backgroundColor: 'var(--surface-subtle)',
                        color: '#dc2626',
                        border: '1px solid var(--border)',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = '#fef2f2'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor =
                          'var(--surface-subtle)'
                      }}
                    >
                      削除
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Phase 2: ページネーション */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-4 mt-8">
            <button
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 rounded transition disabled:opacity-50"
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)',
                color: 'var(--text)',
              }}
            >
              ← 前へ
            </button>
            <span style={{ color: 'var(--text-subtle)' }}>
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 rounded transition disabled:opacity-50"
              style={{
                backgroundColor: 'var(--surface)',
                border: '1px solid var(--border)',
                color: 'var(--text)',
              }}
            >
              次へ →
            </button>
          </div>
        )}
      </main>

      {/* 追加/編集モーダル */}
      {(modalMode === 'add' || modalMode === 'edit') && (
        <div
          className="fixed inset-0 flex items-center justify-center z-50"
          style={{ backgroundColor: 'rgba(0, 0, 0, 0.5)' }}
          onClick={closeModal}
        >
          <div
            className="w-full max-w-2xl p-6 rounded-[var(--radius)]"
            style={{
              backgroundColor: 'var(--surface)',
              border: '1px solid var(--border)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2
              className="text-[18px] font-semibold mb-6"
              style={{ color: 'var(--text)' }}
            >
              {modalMode === 'add' ? '参照例を追加' : '参照例を編集'}
            </h2>

            <form onSubmit={handleSubmit}>
              {/* タイプ選択 */}
              <div className="mb-4">
                <label
                  className="block text-[13px] font-medium mb-2"
                  style={{ color: 'var(--text)' }}
                >
                  タイプ
                </label>
                <select
                  value={formType}
                  onChange={(e) => setFormType(e.target.value as any)}
                  required
                  className="w-full px-3 py-2 rounded-[var(--radius-sm)] text-[14px]"
                  style={{
                    backgroundColor: 'var(--bg)',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                >
                  <option value="reflection">振り返り</option>
                  <option value="final">最終レポート</option>
                </select>
              </div>

              {/* コメント本文 */}
              <div className="mb-4">
                <label
                  className="block text-[13px] font-medium mb-2"
                  style={{ color: 'var(--text)' }}
                >
                  コメント本文
                </label>
                <textarea
                  value={formText}
                  onChange={(e) => setFormText(e.target.value)}
                  required
                  rows={8}
                  className="w-full px-3 py-2 rounded-[var(--radius-sm)] text-[14px]"
                  style={{
                    backgroundColor: 'var(--bg)',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                  placeholder="参照例として使用するコメントを入力してください"
                />
              </div>

              {/* タグ */}
              <div className="mb-6">
                <label
                  className="block text-[13px] font-medium mb-2"
                  style={{ color: 'var(--text)' }}
                >
                  タグ（カンマ区切り）
                </label>
                <input
                  type="text"
                  value={formTags}
                  onChange={(e) => setFormTags(e.target.value)}
                  className="w-full px-3 py-2 rounded-[var(--radius-sm)] text-[14px]"
                  style={{
                    backgroundColor: 'var(--bg)',
                    color: 'var(--text)',
                    border: '1px solid var(--border)',
                  }}
                  placeholder="例: 経営理念, 組織, 戦略"
                />
              </div>

              {/* ボタン */}
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={closeModal}
                  disabled={isSubmitting}
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
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
                  style={{
                    backgroundColor: 'var(--accent)',
                    color: 'white',
                    opacity: isSubmitting ? 0.5 : 1,
                  }}
                >
                  {isSubmitting
                    ? '処理中...'
                    : modalMode === 'add'
                    ? '追加'
                    : '更新'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
