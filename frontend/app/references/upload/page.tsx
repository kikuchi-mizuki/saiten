'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { getCurrentUser } from '@/lib/auth'
import { getAccessToken } from '@/lib/auth'
import type { User } from '@supabase/supabase-js'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://saiten-production.up.railway.app'

interface Section {
  title: string
  content: string
}

export default function UploadFilePage() {
  const router = useRouter()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // ファイルアップロード状態
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [splitByTopic, setSplitByTopic] = useState(true) // デフォルトで分割ON

  // 抽出結果
  const [extractedText, setExtractedText] = useState('')
  const [suggestedTags, setSuggestedTags] = useState<string[]>([])
  const [fileType, setFileType] = useState<'audio' | 'text' | null>(null)
  const [sections, setSections] = useState<Section[]>([])
  const [isSplit, setIsSplit] = useState(false)

  useEffect(() => {
    async function checkAuth() {
      const currentUser = await getCurrentUser()
      if (!currentUser) {
        router.push('/login')
        return
      }
      setUser(currentUser)
      setIsLoading(false)
    }
    checkAuth()
  }, [router])

  // ドラッグ&ドロップ処理
  function handleDragEnter(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(true)
  }

  function handleDragLeave(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setIsDragging(false)
    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  // ファイル選択処理
  function handleFileSelect(file: File) {
    const validAudioExtensions = ['.mp3', '.wav', '.m4a']
    const validTextExtensions = ['.txt']
    const fileName = file.name.toLowerCase()

    const isValidAudio = validAudioExtensions.some(ext => fileName.endsWith(ext))
    const isValidText = validTextExtensions.some(ext => fileName.endsWith(ext))

    if (!isValidAudio && !isValidText) {
      alert('対応していないファイル形式です。mp3, wav, m4a, txt のみ対応しています。')
      return
    }

    const maxSize = isValidAudio ? 100 * 1024 * 1024 : 1 * 1024 * 1024
    if (file.size > maxSize) {
      alert(`ファイルサイズが大きすぎます。${isValidAudio ? '100MB' : '1MB'}以下にしてください。`)
      return
    }

    setSelectedFile(file)
  }

  // アップロード処理
  async function handleUpload() {
    if (!selectedFile) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('split_by_topic', splitByTopic.toString())

      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90))
      }, 200)

      const token = await getAccessToken()
      const response = await fetch(`${API_BASE}/upload-file?split_by_topic=${splitByTopic}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      clearInterval(progressInterval)
      setUploadProgress(100)

      if (!response.ok) {
        throw new Error('ファイルのアップロードに失敗しました')
      }

      const data = await response.json()
      setExtractedText(data.text)
      setSuggestedTags(data.suggested_tags || [])
      setFileType(data.file_type)
      setIsSplit(data.split || false)
      setSections(data.sections || [])
    } catch (error) {
      console.error('Upload error:', error)
      alert('ファイルのアップロードに失敗しました')
    } finally {
      setIsUploading(false)
    }
  }

  // セクションを個別に保存
  async function handleSaveSection(section: Section, index: number) {
    try {
      const token = await getAccessToken()
      const response = await fetch(`${API_BASE}/references`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text: section.content,
          tags: [...suggestedTags, section.title], // 全体タグ + セクションタイトル
          type: 'reflection',
          source: fileType === 'audio' ? 'audio_upload' : 'text_upload'
        })
      })

      if (!response.ok) {
        throw new Error('保存に失敗しました')
      }

      alert(`セクション${index + 1}「${section.title}」を保存しました！`)
    } catch (error) {
      console.error('Save error:', error)
      alert('保存に失敗しました')
    }
  }

  // 全セクションを一括保存
  async function handleSaveAllSections() {
    if (sections.length === 0) return

    try {
      for (let i = 0; i < sections.length; i++) {
        await handleSaveSection(sections[i], i)
      }

      alert(`${sections.length}個のセクションをすべて保存しました！`)
      router.push('/references')
    } catch (error) {
      console.error('Save all error:', error)
      alert('一括保存に失敗しました')
    }
  }

  // ナレッジベースに保存（分割なしの場合）
  async function handleSaveToKnowledgeBase() {
    if (!extractedText) return

    try {
      const token = await getAccessToken()
      const response = await fetch(`${API_BASE}/references`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          text: extractedText,
          tags: suggestedTags,
          type: 'reflection',
          source: fileType === 'audio' ? 'audio_upload' : 'text_upload'
        })
      })

      if (!response.ok) {
        throw new Error('保存に失敗しました')
      }

      alert('ナレッジベースに保存しました！')
      router.push('/references')
    } catch (error) {
      console.error('Save error:', error)
      alert('保存に失敗しました')
    }
  }

  if (isLoading) {
    return <div>読み込み中...</div>
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--bg)' }}>
      {/* ヘッダー */}
      <header className="border-b" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-[18px] font-semibold" style={{ color: 'var(--text)' }}>
            ファイルアップロード
          </h1>
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
            ← 戻る
          </Link>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {!selectedFile && !extractedText && (
          <>
            {/* 分割オプション */}
            <div className="mb-6 p-4 border rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={splitByTopic}
                  onChange={(e) => setSplitByTopic(e.target.checked)}
                  className="w-4 h-4"
                />
                <div>
                  <div className="text-[14px] font-medium" style={{ color: 'var(--text)' }}>
                    🔀 LLMで意味のあるまとまりに分割する
                  </div>
                  <div className="text-[12px]" style={{ color: 'var(--text-muted)' }}>
                    長い音声・テキストを自動的にトピックごとに分割します（推奨）
                  </div>
                </div>
              </label>
            </div>

            {/* ファイル選択エリア */}
            <div
              className={`text-center p-12 border-2 border-dashed rounded-[var(--radius-sm)] ${isDragging ? 'bg-blue-50' : ''}`}
              style={{
                borderColor: isDragging ? 'var(--accent)' : 'var(--border)',
                backgroundColor: isDragging ? 'var(--surface-hover)' : 'var(--surface)'
              }}
              onDragEnter={handleDragEnter}
              onDragOver={(e) => e.preventDefault()}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="text-[48px] mb-4">📁</div>
              <p className="text-[16px] mb-4" style={{ color: 'var(--text)' }}>
                ファイルをドラッグ&ドロップ
              </p>
              <p className="text-[14px] mb-6" style={{ color: 'var(--text-subtle)' }}>
                または
              </p>
              <label className="px-6 py-3 rounded-[var(--radius-sm)] text-[14px] font-medium cursor-pointer inline-block transition hover:opacity-90" style={{ backgroundColor: 'var(--accent)', color: 'white' }}>
                📎 ファイルを選択
                <input
                  type="file"
                  accept=".mp3,.wav,.m4a,.txt"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files.length > 0) {
                      handleFileSelect(e.target.files[0])
                    }
                  }}
                />
              </label>
              <p className="text-[12px] mt-6 text-center" style={{ color: 'var(--text-muted)' }}>
                対応形式:<br />
                • 音声: mp3, wav, m4a（最大100MB）<br />
                • テキスト: txt（最大1MB）
              </p>
            </div>
          </>
        )}

        {selectedFile && !extractedText && (
          <div className="text-center p-12 border rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
            <div className="text-[48px] mb-4">✅</div>
            <p className="text-[18px] mb-2" style={{ color: 'var(--text)' }}>
              ファイル選択: {selectedFile.name}
            </p>
            <p className="text-[14px] mb-2" style={{ color: 'var(--text-subtle)' }}>
              サイズ: {(selectedFile.size / 1024 / 1024).toFixed(2)}MB
            </p>
            <p className="text-[14px] mb-6" style={{ color: 'var(--text-subtle)' }}>
              {splitByTopic ? '🔀 LLMで意味のあるまとまりに分割します' : '分割せずに全文を処理します'}
            </p>

            {!isUploading && (
              <button
                onClick={handleUpload}
                className="px-6 py-3 rounded-[var(--radius-sm)] text-[14px] font-medium transition hover:opacity-90"
                style={{ backgroundColor: 'var(--accent)', color: 'white' }}
              >
                🚀 アップロード開始
              </button>
            )}

            {isUploading && (
              <div>
                <p className="text-[16px] mb-4" style={{ color: 'var(--text)' }}>🔄 処理中...</p>
                <div className="w-full rounded h-4 mb-4" style={{ backgroundColor: 'var(--surface-subtle)' }}>
                  <div
                    className="h-4 rounded transition-all"
                    style={{
                      width: `${uploadProgress}%`,
                      backgroundColor: 'var(--accent)'
                    }}
                  />
                </div>
                <p className="text-[14px]" style={{ color: 'var(--text-muted)' }}>
                  {uploadProgress < 100 ? 'アップロード中...' :
                   selectedFile.name.toLowerCase().endsWith('.txt') ? 'テキスト処理中...' :
                   '🔄 Whisper APIで文字起こし中...'}
                  {splitByTopic && uploadProgress === 100 && <><br />🔀 LLMで分割中...</>}
                </p>
              </div>
            )}
          </div>
        )}

        {extractedText && isSplit && sections.length > 0 && (
          <div>
            <div className="mb-6 p-4 border rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
              <h2 className="text-[16px] font-semibold mb-2" style={{ color: 'var(--text)' }}>
                ✅ {sections.length}個のセクションに分割しました
              </h2>
              <p className="text-[14px] mb-4" style={{ color: 'var(--text-subtle)' }}>
                各セクションを個別に確認・保存できます
              </p>
              <div className="flex gap-4">
                <button
                  onClick={handleSaveAllSections}
                  className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition hover:opacity-90"
                  style={{ backgroundColor: 'var(--accent)', color: 'white' }}
                >
                  すべてのセクションを一括保存
                </button>
                <button
                  onClick={() => {
                    setSelectedFile(null)
                    setExtractedText('')
                    setSections([])
                    setSuggestedTags([])
                  }}
                  className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
                  style={{
                    backgroundColor: 'var(--surface-subtle)',
                    border: '1px solid var(--border)',
                    color: 'var(--text)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--bg)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                  }}
                >
                  やり直し
                </button>
              </div>
            </div>

            {/* セクション一覧 */}
            <div className="space-y-6">
              {sections.map((section, index) => (
                <div key={index} className="p-6 border rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
                  <h3 className="text-[16px] font-semibold mb-3" style={{ color: 'var(--text)' }}>
                    セクション{index + 1}: {section.title}
                  </h3>
                  <div className="mb-4 p-4 rounded-[var(--radius-sm)] text-[14px] leading-relaxed" style={{ backgroundColor: 'var(--bg)', color: 'var(--text)' }}>
                    {section.content.substring(0, 300)}
                    {section.content.length > 300 && '...'}
                    <div className="mt-2 text-[12px]" style={{ color: 'var(--text-muted)' }}>
                      {section.content.length}文字
                    </div>
                  </div>
                  <button
                    onClick={() => handleSaveSection(section, index)}
                    className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition hover:opacity-90"
                    style={{ backgroundColor: 'var(--accent)', color: 'white' }}
                  >
                    このセクションを保存
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {extractedText && !isSplit && (
          <div className="p-6 border rounded-[var(--radius-sm)]" style={{ backgroundColor: 'var(--surface)', borderColor: 'var(--border)' }}>
            <p className="text-[14px] mb-2" style={{ color: 'var(--text)' }}>抽出されたテキスト:</p>
            <textarea
              value={extractedText}
              onChange={(e) => setExtractedText(e.target.value)}
              className="w-full h-64 p-3 border rounded-[var(--radius-sm)] mb-4"
              style={{ borderColor: 'var(--border)', color: 'var(--text)', backgroundColor: 'var(--bg)' }}
            />

            <p className="text-[14px] mb-2" style={{ color: 'var(--text)' }}>提案タグ:</p>
            <div className="flex gap-2 flex-wrap mb-4">
              {suggestedTags.map((tag, index) => (
                <span
                  key={index}
                  className="px-3 py-1 text-[13px] rounded-[var(--radius-sm)] border"
                  style={{ backgroundColor: 'var(--surface-subtle)', borderColor: 'var(--border)', color: 'var(--text)' }}
                >
                  {tag}
                </span>
              ))}
            </div>

            <div className="mt-4 flex gap-4">
              <button
                onClick={handleSaveToKnowledgeBase}
                className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition hover:opacity-90"
                style={{ backgroundColor: 'var(--accent)', color: 'white' }}
              >
                ナレッジベースに保存
              </button>
              <button
                onClick={() => {
                  setSelectedFile(null)
                  setExtractedText('')
                  setSuggestedTags([])
                  setFileType(null)
                }}
                className="px-4 py-2 rounded-[var(--radius-sm)] text-[13px] font-medium transition"
                style={{
                  backgroundColor: 'var(--surface-subtle)',
                  border: '1px solid var(--border)',
                  color: 'var(--text)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--bg)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--surface-subtle)'
                }}
              >
                やり直し
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
