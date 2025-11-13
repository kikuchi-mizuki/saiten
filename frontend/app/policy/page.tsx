/**
 * 利用規約ページ
 *
 * docs/policy.mdの内容を表示します。
 */

import Link from 'next/link'

export default function PolicyPage() {
  return (
    <div
      className="min-h-screen py-12 px-4"
      style={{ backgroundColor: 'var(--bg)' }}
    >
      <div className="max-w-4xl mx-auto">
        {/* ヘッダー */}
        <div className="mb-8">
          <Link
            href="/login"
            className="inline-flex items-center gap-2 text-[14px] mb-4"
            style={{ color: 'var(--accent)' }}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            ログイン画面に戻る
          </Link>
          <h1
            className="text-[22px] font-semibold"
            style={{ color: 'var(--text)' }}
          >
            教授コメント自動化ボット 利用規約
          </h1>
          <p
            className="text-[13px] mt-2"
            style={{ color: 'var(--text-muted)' }}
          >
            最終更新: 2025-11-11 | バージョン: 1.0
          </p>
        </div>

        {/* 利用規約本文 */}
        <div
          className="p-8 rounded-[var(--radius)] prose prose-sm max-w-none"
          style={{
            backgroundColor: 'var(--surface)',
            color: 'var(--text)'
          }}
        >
          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">1. サービス概要</h2>
            <p className="mb-4">
              本サービス（以下「本システム」）は、経営戦略論の教授がレポートコメント作成を効率化するためのAIアシスタントツールです。
            </p>
            <h3 className="text-[16px] font-medium mb-2">主な機能</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>レポート本文に対するコメント自動生成</li>
              <li>Rubric自動採点（5項目、1-5点）</li>
              <li>レポート要約生成</li>
              <li>過去のコメント履歴管理</li>
              <li>コメント品質評価（手直し時間測定、満足度アンケート）</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">2. 利用対象者</h2>
            <p>本システムは、経営戦略論の担当教授のみが利用できます。</p>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">3. 個人情報の取り扱い</h2>

            <h3 className="text-[16px] font-medium mb-2 mt-4">3.1 収集する情報</h3>
            <p className="mb-2">本システムは、以下の情報を収集・保存します：</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Googleアカウント情報（メールアドレス）</li>
              <li>レポート本文（暗号化して保存）</li>
              <li>生成されたコメント</li>
              <li>Rubric採点結果</li>
              <li>手直し時間・満足度評価</li>
            </ul>

            <h3 className="text-[16px] font-medium mb-2 mt-4">3.2 データの保存場所</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>データベース: Supabase (PostgreSQL)</li>
              <li>リージョン: Asia Pacific (Tokyo)</li>
              <li>暗号化: レポート本文はAES-256-GCMで暗号化</li>
            </ul>

            <h3 className="text-[16px] font-medium mb-2 mt-4">3.3 データの保存期間</h3>
            <p>
              無期限保存（ユーザーが削除しない限り）。ユーザーはいつでも履歴画面から個別にデータを削除可能です。
            </p>

            <h3 className="text-[16px] font-medium mb-2 mt-4">3.4 個人情報保護対策</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>Google OAuth 2.0による安全な認証</li>
              <li>データ暗号化（AES-256-GCM）</li>
              <li>Row Level Security (RLS)によるデータ分離</li>
              <li>HTTPS/TLSによる通信の暗号化</li>
              <li>PII検出・マスキング（個人情報の自動検出）</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">4. 第三者へのデータ提供</h2>

            <h3 className="text-[16px] font-medium mb-2 mt-4">4.1 OpenAI API（必須）</h3>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>提供データ: レポート本文（PII検出後、個人情報をマスキング）</li>
              <li>提供目的: コメント生成・Rubric採点・要約生成</li>
              <li>データ取り扱い: 30日間保持、学習には使用されない</li>
            </ul>

            <h3 className="text-[16px] font-medium mb-2 mt-4">4.2 Supabase（必須）</h3>
            <p>すべてのユーザーデータをデータベース・認証サービスとして使用</p>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">5. ユーザーの権利</h2>

            <h3 className="text-[16px] font-medium mb-2 mt-4">5.1 データの閲覧</h3>
            <p>ユーザーは、履歴画面からいつでも自分のデータを閲覧できます。</p>

            <h3 className="text-[16px] font-medium mb-2 mt-4">5.2 データの削除</h3>
            <p>履歴詳細画面の「削除」ボタンから即座に物理削除できます。</p>

            <h3 className="text-[16px] font-medium mb-2 mt-4">5.3 データのエクスポート</h3>
            <p>履歴画面の「エクスポート」ボタンから、JSON/CSV形式でダウンロードできます。</p>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">6. 免責事項</h2>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>本システムは「現状有姿」で提供されます</li>
              <li>サービスの可用性・正確性を保証するものではありません</li>
              <li>AI生成コメントは参考情報であり、最終判断は教授が行います</li>
              <li>システム障害等によりデータが喪失する可能性があります</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">7. 同意の確認</h2>
            <p className="mb-2">本システムを利用することで、以下に同意したものとします：</p>
            <ul className="list-disc list-inside space-y-1 ml-4">
              <li>レポート本文（個人情報をマスキング後）がOpenAI APIに送信されること</li>
              <li>データがSupabase（PostgreSQL）に保存されること</li>
              <li>データが暗号化されて保存されること</li>
              <li>ユーザーはいつでもデータを削除できること</li>
              <li>本利用規約の内容に同意すること</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-[18px] font-semibold mb-4">8. 準拠法・管轄裁判所</h2>
            <p>
              本利用規約は、日本法に準拠します。本システムに関する一切の紛争については、東京地方裁判所を第一審の専属的合意管轄裁判所とします。
            </p>
          </section>

          <div
            className="mt-8 pt-6 text-[12px]"
            style={{
              borderTop: '1px solid var(--border)',
              color: 'var(--text-muted)'
            }}
          >
            <p>制定日: 2025-11-11</p>
            <p>施行日: 2025-11-11</p>
          </div>
        </div>
      </div>
    </div>
  )
}
