'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { useRouter } from 'next/navigation'

interface Voiceprint {
  id: string
  voiceprint_name: string
  audio_duration_seconds: number
  sample_count: number
  confidence_score: number
  created_at: string
  is_active: boolean
}

export default function VoiceprintPage() {
  const router = useRouter()
  const supabase = createClient()

  const [voiceprints, setVoiceprints] = useState<Voiceprint[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState('')
  const [error, setError] = useState('')

  // 登録済み声紋を取得
  useEffect(() => {
    fetchVoiceprints()
  }, [])

  async function fetchVoiceprints() {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010'
      const response = await fetch(`${API_BASE}/voiceprint/list`, {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (!response.ok) {
        throw new Error('声紋リストの取得に失敗しました')
      }

      const data = await response.json()
      setVoiceprints(data.voiceprints || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleFileUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    if (!file) return

    // 音声ファイルの形式チェック
    const validFormats = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/m4a', 'audio/mp4']
    if (!validFormats.includes(file.type) && !file.name.match(/\.(mp3|wav|m4a)$/i)) {
      setError('対応していないファイル形式です。MP3, WAV, M4Aファイルをアップロードしてください。')
      return
    }

    setUploading(true)
    setUploadProgress('🎤 音声ファイルを読み込んでいます...')
    setError('')

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }

      const formData = new FormData()
      formData.append('file', file)

      setUploadProgress('🧠 声紋を抽出しています...')

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010'
      const response = await fetch(`${API_BASE}/voiceprint/register`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        },
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || '声紋登録に失敗しました')
      }

      const result = await response.json()

      setUploadProgress('✅ 声紋を登録しました！')

      // リストを再取得
      await fetchVoiceprints()

      // フォームをリセット
      event.target.value = ''

      setTimeout(() => {
        setUploadProgress('')
      }, 2000)

    } catch (err: any) {
      setError(err.message || '声紋登録に失敗しました')
      setUploadProgress('')
    } finally {
      setUploading(false)
    }
  }

  async function handleDelete(voiceprintId: string) {
    if (!confirm('この声紋を削除してもよろしいですか？')) {
      return
    }

    try {
      const { data: { session } } = await supabase.auth.getSession()
      if (!session) {
        router.push('/login')
        return
      }

      const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8010'
      const response = await fetch(`${API_BASE}/voiceprint/${voiceprintId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      })

      if (!response.ok) {
        throw new Error('声紋の削除に失敗しました')
      }

      // リストを再取得
      await fetchVoiceprints()
    } catch (err: any) {
      setError(err.message)
    }
  }

  function formatDuration(seconds: number): string {
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes}分${secs}秒`
  }

  function formatDate(dateString: string): string {
    const date = new Date(dateString)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <p className="text-gray-600">読み込み中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">教授の声紋管理</h1>
          <p className="text-gray-600">
            教授の声を登録することで、音声ファイルから教授の発言のみを自動抽出できるようになります。
          </p>
        </div>

        {/* 声紋登録セクション */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">新しい声紋を登録</h2>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2">📋 登録のポイント</h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• 3〜5分程度の音声サンプルを用意してください</li>
              <li>• 教授のみが話している音声が最適です</li>
              <li>• クリアな音質の録音を推奨します</li>
              <li>• 対応形式: MP3, WAV, M4A</li>
            </ul>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              accept="audio/*"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
              id="voiceprint-upload"
            />
            <label
              htmlFor="voiceprint-upload"
              className={`inline-block px-6 py-3 rounded-lg font-semibold cursor-pointer transition-colors ${
                uploading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {uploading ? '処理中...' : '🎤 音声ファイルを選択'}
            </label>

            {uploadProgress && (
              <div className="mt-4 text-blue-600 font-medium">{uploadProgress}</div>
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                ❌ {error}
              </div>
            )}
          </div>
        </div>

        {/* 登録済み声紋リスト */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">登録済みの声紋</h2>

          {voiceprints.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg mb-2">まだ声紋が登録されていません</p>
              <p className="text-sm">上のフォームから音声ファイルをアップロードして声紋を登録してください。</p>
            </div>
          ) : (
            <div className="space-y-4">
              {voiceprints.map((vp) => (
                <div
                  key={vp.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">{vp.voiceprint_name}</h3>
                        {vp.is_active && (
                          <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                            ✓ アクティブ
                          </span>
                        )}
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">音声長:</span>{' '}
                          {formatDuration(vp.audio_duration_seconds)}
                        </div>
                        <div>
                          <span className="font-medium">サンプル数:</span> {vp.sample_count}
                        </div>
                        <div>
                          <span className="font-medium">信頼度:</span>{' '}
                          {(vp.confidence_score * 100).toFixed(0)}%
                        </div>
                        <div>
                          <span className="font-medium">登録日:</span>{' '}
                          {formatDate(vp.created_at)}
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => handleDelete(vp.id)}
                      className="ml-4 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
                    >
                      削除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 使い方ガイド */}
        <div className="mt-8 bg-gray-100 rounded-lg p-6">
          <h3 className="font-semibold text-gray-900 mb-3">💡 声紋の使い方</h3>
          <ol className="text-sm text-gray-700 space-y-2">
            <li>1. 教授のみが話している3〜5分程度の音声を用意</li>
            <li>2. 上のフォームから音声ファイルをアップロード</li>
            <li>3. 声紋が自動的に抽出され、データベースに保存されます</li>
            <li>4. 次回から、参照例アップロード時に教授の発言のみを自動抽出</li>
            <li>5. 使うほど精度が向上します（継続学習）</li>
          </ol>
        </div>

        {/* 戻るボタン */}
        <div className="mt-8 text-center">
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← ダッシュボードに戻る
          </button>
        </div>
      </div>
    </div>
  )
}
