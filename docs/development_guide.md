# 教授コメント自動化ボット 開発手順書

**最終更新**: 2025-11-11
**バージョン**: 1.0
**対象フェーズ**: Phase 1 MVP

---

## 目次

1. [開発環境セットアップ](#開発環境セットアップ)
2. [Week 0: 準備週間](#week-0-準備週間)
3. [Week 1-2: 環境セットアップ + 認証](#week-1-2-環境セットアップ--認証)
4. [Week 3-4: メイン画面 + UI実装](#week-3-4-メイン画面--ui実装)
5. [Week 5-6: バックエンド強化 + PII検出](#week-5-6-バックエンド強化--pii検出)
6. [Week 7-9: DB連携 + データ管理](#week-7-9-db連携--データ管理)
7. [Week 10-11: 品質評価 + 既存機能完成](#week-10-11-品質評価--既存機能完成)
8. [Week 12: 検証・改善](#week-12-検証改善)
9. [Week 13-14: 最終調整・ドキュメント](#week-13-14-最終調整ドキュメント)
10. [コーディング規約](#コーディング規約)
11. [テスト手順](#テスト手順)
12. [トラブルシューティング](#トラブルシューティング)

---

## 開発環境セットアップ

### 前提条件

| ソフトウェア | バージョン | 用途 |
|------------|----------|------|
| Node.js | 18.x以上 | Next.jsの実行 |
| Python | 3.11以上 | FastAPIの実行 |
| Git | 最新 | バージョン管理 |
| VSCode | 最新（推奨） | コードエディタ |

### 初期セットアップ

```bash
# 1. リポジトリクローン（または作成）
mkdir saiten-mvp
cd saiten-mvp
git init

# 2. ディレクトリ構造作成
mkdir -p frontend backend docs prompts data

# 3. .gitignore作成
cat > .gitignore << EOF
# Next.js
frontend/.next/
frontend/out/
frontend/node_modules/

# Python
backend/__pycache__/
backend/*.pyc
backend/.pytest_cache/
backend/logs/

# 環境変数
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/

# OS
.DS_Store
EOF
```

---

## Week 0: 準備週間

**期間**: 5日間
**目標**: Phase 1開発に必要な準備を完了

### Day 1-2: 利用規約・OSSライセンス整理

#### タスク1: 利用規約作成

**ファイル**: `docs/policy.md`

```bash
touch docs/policy.md
```

**記載内容**:
```markdown
# 教授コメント自動化ボット 利用規約

## 1. サービス概要
本サービスは、経営戦略論の教授がレポートコメント作成を効率化するためのAIアシスタントです。

## 2. 個人情報の取り扱い

### 2.1 収集する情報
- Googleアカウント情報（メールアドレス）
- レポート本文（暗号化して保存）
- 生成されたコメント
- 利用統計情報

### 2.2 データ保存期間
- 無期限保存（ただし、ユーザーはいつでも削除可能）

### 2.3 第三者へのデータ提供
- OpenAI API: レポート本文（個人情報をマスキング後）を送信
  - 参考: https://openai.com/policies/privacy-policy
  - OpenAIはAPIリクエストのデータを30日間保持（学習には使用しない）

## 3. セキュリティ対策
- レポート本文は暗号化して保存
- Google OAuth認証
- Row Level Security（RLS）によるデータ分離

## 4. 利用者の同意
初回ログイン時に、以下に同意したものとします：
- レポート本文がOpenAI APIに送信されること
- データがSupabaseに保存されること

## 5. OSSライセンス
本サービスで使用しているOSSライセンスは `docs/licenses.md` を参照してください。
```

#### タスク2: OSSライセンス一覧作成

**ファイル**: `docs/licenses.md`

```bash
touch docs/licenses.md
```

**記載内容**:
```markdown
# OSSライセンス一覧

本サービスで使用しているOSSとそのライセンス情報

## Frontend

| パッケージ | ライセンス | URL |
|-----------|----------|-----|
| Next.js | MIT | https://github.com/vercel/next.js |
| React | MIT | https://github.com/facebook/react |
| TailwindCSS | MIT | https://github.com/tailwindlabs/tailwindcss |
| TypeScript | Apache 2.0 | https://github.com/microsoft/TypeScript |
| @supabase/supabase-js | MIT | https://github.com/supabase/supabase-js |

## Backend

| パッケージ | ライセンス | URL |
|-----------|----------|-----|
| FastAPI | MIT | https://github.com/tiangolo/fastapi |
| Pydantic | MIT | https://github.com/pydantic/pydantic |
| Uvicorn | BSD-3-Clause | https://github.com/encode/uvicorn |
| cryptography | Apache 2.0 / BSD | https://github.com/pyca/cryptography |
| openai | Apache 2.0 | https://github.com/openai/openai-python |

## Infrastructure

| サービス | ライセンス | URL |
|---------|----------|-----|
| Supabase | Apache 2.0 | https://github.com/supabase/supabase |
| PostgreSQL | PostgreSQL License | https://www.postgresql.org/about/licence/ |
```

### Day 3: 学内審査資料準備（必要に応じて）

**成果物**: `docs/approval_request.md`

- システム概要説明
- セキュリティ対策説明
- 個人情報保護対策説明

### Day 4: ナレッジベース整理

#### タスク1: sample_comments.json の確認

```bash
# 現在のコメント例を確認
cat data/sample_comments.json | jq '.[0:5]'
```

#### タスク2: reflection / final の分類確認

```python
# スクリプトで確認
import json

with open('data/sample_comments.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)

# 文字数分布を確認
lengths = [len(c['comment_text']) for c in comments]
print(f"平均文字数: {sum(lengths) / len(lengths)}")
print(f"最小文字数: {min(lengths)}")
print(f"最大文字数: {max(lengths)}")

# reflection / final に分類（仮）
# ※ 実際の分類基準は教授と相談
```

#### タスク3: Phase移行基準の合意

教授と打ち合わせを行い、以下を合意:
- [ ] Phase 1 → Phase 2-A 移行条件
- [ ] ベースライン測定の方法
- [ ] UAT実施方法

### Day 5: 開発環境準備

#### タスク1: GitHubリポジトリ作成

```bash
# GitHubでリポジトリ作成後
git remote add origin https://github.com/your-username/saiten-mvp.git
git add .
git commit -m "Initial commit: Week 0 preparation"
git push -u origin main
```

#### タスク2: Vercelアカウント作成

1. https://vercel.com/ にアクセス
2. GitHubアカウントでサインアップ
3. リポジトリ連携（後で実施）

#### タスク3: Supabaseアカウント作成

1. https://supabase.com/ にアクセス
2. GitHubアカウントでサインアップ
3. プロジェクト作成（Week 1で実施）

#### タスク4: OpenAI APIキー確認

```bash
# .envファイルにAPIキーが存在することを確認
cat .env | grep OPENAI_API_KEY
```

---

## Week 1-2: 環境セットアップ + 認証

**期間**: 2週間
**目標**: Next.js + Supabase + Google OAuth が動作する

### Week 1, Day 1-3: Next.jsプロジェクトセットアップ

#### Step 1: Next.jsプロジェクト作成

```bash
cd frontend
npx create-next-app@14 . --typescript --tailwind --app --no-src-dir
```

**選択肢**:
- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- `src/` directory: No
- App Router: Yes
- Import alias: Yes (`@/*`)

#### Step 2: TailwindCSS設定 + design-tokens.css作成

```bash
# design-tokens.css作成
cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Academic Minimal UI Design Tokens */
:root {
  /* Colors */
  --color-bg-primary: #fefefe;
  --color-bg-secondary: #f7f7f7;
  --color-text-primary: #2c2c2c;
  --color-text-secondary: #6b6b6b;
  --color-accent: #4a90e2;
  --color-accent-hover: #357abd;
  --color-border: #e0e0e0;
  --color-success: #5cb85c;
  --color-warning: #f0ad4e;
  --color-error: #d9534f;

  /* Typography */
  --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", sans-serif;
  --font-mono: "SF Mono", "Monaco", "Inconsolata", monospace;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border Radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

body {
  font-family: var(--font-sans);
  color: var(--color-text-primary);
  background-color: var(--color-bg-primary);
}
EOF
```

#### Step 3: Supabaseクライアント設定

```bash
npm install @supabase/supabase-js
```

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
```

### Week 1, Day 4-5: Supabaseプロジェクト作成

#### Step 1: プロジェクト作成

1. https://supabase.com/dashboard にアクセス
2. 「New Project」をクリック
3. 以下を入力:
   - Name: `saiten-mvp`
   - Database Password: （強力なパスワードを生成）
   - Region: `Asia Pacific (Tokyo)`
4. 「Create new project」をクリック

#### Step 2: 環境変数取得

プロジェクトSettings > API から以下を取得:

```bash
# frontend/.env.local
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Week 2, Day 1-3: Google OAuth設定

#### Step 1: Google Cloud Console設定

1. https://console.cloud.google.com/ にアクセス
2. 新しいプロジェクトを作成（例: `saiten-mvp`）
3. 「APIとサービス」 > 「認証情報」
4. 「認証情報を作成」 > 「OAuth 2.0 クライアント ID」
5. 以下を入力:
   - アプリケーションの種類: ウェブアプリケーション
   - 名前: `Saiten MVP`
   - 承認済みのリダイレクト URI: `https://xxx.supabase.co/auth/v1/callback`
6. Client ID と Client Secret を取得

#### Step 2: Supabase Auth設定

1. Supabase Dashboard > Authentication > Providers
2. Google を有効化
3. Client ID と Client Secret を入力
4. 「Save」をクリック

### Week 2, Day 4-5: ログイン画面実装

#### Step 1: ログインページ作成

```typescript
// app/(auth)/login/page.tsx
'use client'

import { supabase } from '@/lib/supabase'
import { useEffect, useState } from 'react'

export default function LoginPage() {
  const [isLoading, setIsLoading] = useState(false)

  async function handleGoogleLogin() {
    setIsLoading(true)
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`
      }
    })
    if (error) {
      console.error('Login error:', error)
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-primary)]">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow-md">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-[var(--color-text-primary)]">
            教授コメント自動化ボット
          </h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
            経営戦略論のレポートコメント作成をサポート
          </p>
        </div>

        <button
          onClick={handleGoogleLogin}
          disabled={isLoading}
          className="w-full flex items-center justify-center px-4 py-3 border border-transparent text-base font-medium rounded-md text-white bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] disabled:opacity-50 transition"
        >
          {isLoading ? 'ログイン中...' : 'Googleでログイン'}
        </button>

        <div className="mt-4 text-xs text-[var(--color-text-secondary)] space-y-2">
          <p>ログインすることで、以下に同意したものとします：</p>
          <ul className="list-disc list-inside space-y-1">
            <li>レポート本文がOpenAI APIに送信されること</li>
            <li>データがSupabaseに保存されること</li>
          </ul>
          <p>
            詳細は
            <a href="/policy" className="text-[var(--color-accent)] underline">利用規約</a>
            を参照してください。
          </p>
        </div>
      </div>
    </div>
  )
}
```

#### Step 2: コールバック処理

```typescript
// app/auth/callback/route.ts
import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')

  if (code) {
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )
    await supabase.auth.exchangeCodeForSession(code)
  }

  return NextResponse.redirect(new URL('/', request.url))
}
```

### Week 2 完了チェック

- [ ] Next.jsプロジェクトが起動する（`npm run dev`）
- [ ] Supabaseプロジェクトが作成されている
- [ ] Google OAuthでログインできる
- [ ] ログイン後にトップページにリダイレクトされる

---

## Week 3-4: メイン画面 + UI実装

**期間**: 2週間
**目標**: Academic Minimal UIでメイン画面を実装

### Week 3, Day 1-2: 共通UIコンポーネント

#### Button コンポーネント

```typescript
// components/ui/Button.tsx
import { ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
}

export function Button({ variant = 'primary', children, ...props }: ButtonProps) {
  const baseClasses = 'px-4 py-2 rounded-md font-medium transition disabled:opacity-50'

  const variantClasses = {
    primary: 'bg-[var(--color-accent)] text-white hover:bg-[var(--color-accent-hover)]',
    secondary: 'bg-[var(--color-bg-secondary)] text-[var(--color-text-primary)] hover:bg-gray-300',
    danger: 'bg-[var(--color-error)] text-white hover:bg-red-600'
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]}`}
      {...props}
    >
      {children}
    </button>
  )
}
```

#### TextArea コンポーネント

```typescript
// components/ui/TextArea.tsx
import { TextareaHTMLAttributes, forwardRef } from 'react'

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
}

export const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ label, error, className, ...props }, ref) => {
    return (
      <div className="space-y-1">
        {label && (
          <label className="block text-sm font-medium text-[var(--color-text-primary)]">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={`w-full p-3 border rounded-md focus:ring-2 focus:ring-[var(--color-accent)] focus:border-transparent ${
            error ? 'border-[var(--color-error)]' : 'border-[var(--color-border)]'
          } ${className}`}
          {...props}
        />
        {error && (
          <p className="text-sm text-[var(--color-error)]">{error}</p>
        )}
      </div>
    )
  }
)

TextArea.displayName = 'TextArea'
```

#### Card コンポーネント

```typescript
// components/ui/Card.tsx
import { ReactNode } from 'react'

interface CardProps {
  children: ReactNode
  className?: string
}

export function Card({ children, className = '' }: CardProps) {
  return (
    <div className={`bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-lg p-4 shadow-sm ${className}`}>
      {children}
    </div>
  )
}
```

#### Tabs コンポーネント

```typescript
// components/ui/Tabs.tsx
'use client'

import { useState, ReactNode } from 'react'

interface Tab {
  label: string
  content: ReactNode
}

interface TabsProps {
  tabs: Tab[]
}

export function Tabs({ tabs }: TabsProps) {
  const [activeIndex, setActiveIndex] = useState(0)

  return (
    <div>
      <div className="flex border-b border-[var(--color-border)]">
        {tabs.map((tab, index) => (
          <button
            key={index}
            onClick={() => setActiveIndex(index)}
            className={`px-4 py-2 font-medium transition ${
              index === activeIndex
                ? 'border-b-2 border-[var(--color-accent)] text-[var(--color-accent)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="mt-4">
        {tabs[activeIndex].content}
      </div>
    </div>
  )
}
```

### Week 3, Day 3-5: メイン画面レイアウト

```typescript
// app/(dashboard)/page.tsx
'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { TextArea } from '@/components/ui/TextArea'
import { Card } from '@/components/ui/Card'
import { Tabs } from '@/components/ui/Tabs'

export default function DashboardPage() {
  const [reportText, setReportText] = useState('')
  const [reportType, setReportType] = useState<'reflection' | 'final'>('reflection')
  const [isGenerating, setIsGenerating] = useState(false)
  const [result, setResult] = useState(null)

  async function handleGenerate() {
    setIsGenerating(true)
    // TODO: API呼び出し実装（Week 5-6）
    setIsGenerating(false)
  }

  return (
    <div className="min-h-screen p-8 bg-[var(--color-bg-primary)]">
      <h1 className="text-3xl font-bold mb-8 text-[var(--color-text-primary)]">
        レポートコメント生成
      </h1>

      <div className="grid grid-cols-12 gap-6">
        {/* 左カラム: 入力エリア */}
        <div className="col-span-7 space-y-4">
          <Card>
            <div className="space-y-4">
              {/* レポート種別選択 */}
              <div>
                <label className="block text-sm font-medium mb-2 text-[var(--color-text-primary)]">
                  レポート種別
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="reflection"
                      checked={reportType === 'reflection'}
                      onChange={(e) => setReportType(e.target.value as any)}
                      className="mr-2"
                    />
                    Reflection（週次）
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      value="final"
                      checked={reportType === 'final'}
                      onChange={(e) => setReportType(e.target.value as any)}
                      className="mr-2"
                    />
                    Final（最終）
                  </label>
                </div>
              </div>

              {/* レポート本文入力 */}
              <TextArea
                label="レポート本文"
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
                rows={12}
                placeholder="レポート本文を入力してください..."
                maxLength={5000}
              />

              {/* 文字数カウンター */}
              <div className="text-right text-sm text-[var(--color-text-secondary)]">
                {reportText.length} / 5000 文字
              </div>

              {/* ボタン */}
              <div className="flex gap-2">
                <Button onClick={handleGenerate} disabled={!reportText || isGenerating}>
                  {isGenerating ? '生成中...' : '生成'}
                </Button>
                <Button variant="secondary" onClick={() => setReportText('')}>
                  クリア
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* 右カラム: 結果表示エリア */}
        <div className="col-span-5">
          <Card>
            {result ? (
              <Tabs
                tabs={[
                  {
                    label: 'Rubric',
                    content: <div>Rubric採点結果</div>
                  },
                  {
                    label: '要約',
                    content: <div>要約表示</div>
                  },
                  {
                    label: 'コメント',
                    content: <div>コメント表示</div>
                  }
                ]}
              />
            ) : (
              <div className="text-center py-12 text-[var(--color-text-secondary)]">
                レポートを入力して「生成」をクリックしてください
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
```

### Week 4, Day 1-3: ローディングUX実装

```typescript
// components/LoadingProgress.tsx
'use client'

interface LoadingProgressProps {
  steps: { label: string; completed: boolean }[]
}

export function LoadingProgress({ steps }: LoadingProgressProps) {
  return (
    <div className="space-y-2">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center gap-2">
          {step.completed ? (
            <svg className="w-5 h-5 text-[var(--color-success)]" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          ) : (
            <div className="w-5 h-5 border-2 border-[var(--color-accent)] border-t-transparent rounded-full animate-spin" />
          )}
          <span className={step.completed ? 'text-[var(--color-text-secondary)]' : 'text-[var(--color-text-primary)]'}>
            {step.label}
          </span>
        </div>
      ))}
    </div>
  )
}
```

### Week 4, Day 4-5: エラーメッセージガイドライン

**ファイル**: `docs/error_messages.md`

```markdown
# エラーメッセージガイドライン

## 基本原則
1. ユーザーフレンドリーな言葉遣い
2. 具体的な対処法を提示
3. 技術的な詳細は最小限に

## エラーメッセージ一覧

### 認証エラー
- **エラー**: ログインに失敗しました
- **メッセージ**: 「ログインに失敗しました。もう一度お試しください。」
- **対処法**: リトライボタン表示

### API エラー
- **エラー**: OpenAI API エラー
- **メッセージ**: 「コメント生成に失敗しました。ヒューリスティック生成を使用します。」
- **対処法**: フォールバック実行

### ネットワークエラー
- **エラー**: ネットワーク接続エラー
- **メッセージ**: 「ネットワーク接続を確認してください。」
- **対処法**: リトライボタン表示

### 入力エラー
- **エラー**: 文字数超過
- **メッセージ**: 「レポート本文は5000文字以内で入力してください。」
- **対処法**: 文字数カウンター表示
```

---

## Week 5-6: バックエンド強化 + PII検出

**期間**: 2週間
**目標**: FastAPI + PII検出 + final対応

### Week 5, Day 1-2: FastAPIセットアップ

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn pydantic python-dotenv cryptography openai httpx
pip freeze > requirements.txt
```

**ディレクトリ構造作成**:
```bash
mkdir -p api
touch api/__init__.py
touch api/main.py
touch api/auth.py
touch api/pii_detector.py
touch api/models.py
```

#### api/main.py（基本構造）

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api.models import GenerateRequest, GenerateResponse
from api.auth import verify_token

app = FastAPI(title="Saiten MVP API")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js開発環境
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティヘッダ
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_comment(
    req: GenerateRequest,
    user_id: str = Depends(verify_token)
):
    # TODO: 実装
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)
```

### Week 5, Day 3-5: PII検出機能実装

**ファイル**: `api/pii_detector.py`

技術仕様書の実装をそのまま使用（architecture.md参照）

### Week 6, Day 1-2: final対応

#### prompts/final.txt 作成

```bash
cat > prompts/final.txt << 'EOF'
あなたは経営戦略論の教授です。以下のfinalレポートを読み、敬意と温かさを保ちつつ、考えを深めるコメントを作成してください。

【制約】
- 文字数: 参照例が提供されている場合は、参照例の平均文字数の±10%の範囲で生成してください（厳守）。参照例がない場合は400〜500文字（厳守）
- 形式: 1つのまとまった文章ブロックとして出力してください（段落分けや箇条書きは不要）
- 語り口: です・ます調、伴走する姿勢。温かみと示唆の両立。
- 内容には以下を含めてください：
  - 学生の成長の軌跡を振り返る
  - 最終レポートの要点の要約と良い点の承認
  - 教授の洞察（「あり方」と実務の往復を意識した示唆）
  - 卒業後のキャリアへの示唆・次のステップへの問い

【禁止事項】
- 断定しすぎる表現（「〜すべき」「〜しなければならない」など）
- 過度な批判や否定
- 具体性のない抽象的な表現のみ
EOF
```

#### コメント生成時の分岐

```python
# api/comment_generator.py
def load_prompt(report_type: str) -> str:
    """プロンプトファイルを読み込む"""
    if report_type == "final":
        with open("prompts/final.txt", "r", encoding="utf-8") as f:
            return f.read()
    else:
        with open("prompts/reflection.txt", "r", encoding="utf-8") as f:
            return f.read()
```

### Week 6, Day 3-5: 認証ミドルウェア実装

**ファイル**: `api/auth.py`

技術仕様書の実装をそのまま使用（architecture.md参照）

---

## Week 7-9: DB連携 + データ管理

**期間**: 3週間
**目標**: Supabase完全統合

### Week 7, Day 1-3: テーブル設計 + マイグレーション

#### SQL実行

Supabase Dashboard > SQL Editorで実行:

```sql
-- 技術仕様書（architecture.md）のCREATE TABLE文を実行
-- 1. histories テーブル作成
-- 2. knowledge_base テーブル作成
-- 3. RLSポリシー設定
```

### Week 7, Day 4-5: データ暗号化実装

**ファイル**: `api/encryption.py`

技術仕様書の実装をそのまま使用（architecture.md参照）

**環境変数追加**:
```bash
# backend/.env
ENCRYPTION_KEY=your-32-byte-encryption-key-here
```

**キー生成**:
```python
import os
import base64

# 32バイトのキーを生成
key = os.urandom(32)
print(base64.b64encode(key).decode())
```

### Week 8: API実装（DB保存処理）

#### Supabase接続

```bash
pip install supabase
```

```python
# api/database.py
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
```

#### POST /generate 実装

```python
# api/main.py
from api.database import supabase
from api.pii_detector import PIIDetector
from api.encryption import encrypt
from api.comment_generator import generate_comment_with_llm
import uuid

detector = PIIDetector()

@app.post("/generate")
async def generate_comment(req: GenerateRequest, user_id: str = Depends(verify_token)):
    # 1. PII検出
    pii_matches = detector.detect(req.report_text)
    masked_text = detector.mask(req.report_text, pii_matches)

    # 2. コメント生成
    result = await generate_comment_with_llm(masked_text, req.report_type)

    # 3. 暗号化
    encrypted_text = encrypt(req.report_text)

    # 4. DB保存
    history_id = str(uuid.uuid4())
    supabase.table("histories").insert({
        "id": history_id,
        "user_id": user_id,
        "report_type": req.report_type,
        "report_text_encrypted": encrypted_text,
        "masked_text": masked_text,
        "rubric_scores": result["rubric"],
        "rubric_reasons": result["rubric_reasons"],
        "summary": result["summary"],
        "comment": result["comment"]
    }).execute()

    return {
        "history_id": history_id,
        "masked_text": masked_text,
        "pii_detected": [{"type": m.type} for m in pii_matches],
        **result
    }
```

### Week 9: 履歴機能実装

```python
# api/main.py

@app.get("/history")
async def get_history(
    page: int = 1,
    limit: int = 10,
    user_id: str = Depends(verify_token)
):
    offset = (page - 1) * limit
    result = supabase.table("histories") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    return {
        "total": len(result.data),
        "page": page,
        "limit": limit,
        "histories": result.data
    }

@app.delete("/history/{history_id}")
async def delete_history(history_id: str, user_id: str = Depends(verify_token)):
    supabase.table("histories") \
        .delete() \
        .eq("id", history_id) \
        .eq("user_id", user_id) \
        .execute()

    return {"message": "History deleted successfully", "id": history_id}

@app.get("/export")
async def export_history(format: str = "json", user_id: str = Depends(verify_token)):
    result = supabase.table("histories") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()

    if format == "csv":
        # CSV変換実装
        pass
    else:
        return result.data
```

---

## Week 10-11: 品質評価 + 既存機能完成

**期間**: 2週間
**目標**: KPI測定機能実装

### Week 10: 手直し時間測定 + 満足度アンケート

#### フロントエンド実装

```typescript
// app/(dashboard)/page.tsx
const [editStartTime, setEditStartTime] = useState<Date | null>(null)
const [editTime, setEditTime] = useState(0)
const [satisfaction, setSatisfaction] = useState<number | null>(null)

// コメント生成完了時
function handleGenerateComplete(result: any) {
  setResult(result)
  setEditStartTime(new Date())
}

// 保存ボタン押下時
async function handleSave() {
  if (!editStartTime) return

  const editTimeSeconds = Math.floor((new Date().getTime() - editStartTime.getTime()) / 1000)
  setEditTime(editTimeSeconds)

  // 満足度アンケートモーダル表示
  setShowSatisfactionModal(true)
}

// 満足度送信
async function handleSubmitSatisfaction(score: number) {
  await fetch(`${API_BASE}/history/${result.history_id}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      edit_time_seconds: editTime,
      satisfaction: score
    })
  })

  setShowSatisfactionModal(false)
}
```

### Week 11: 統計表示 + テスト実装

#### 統計API

```python
# api/main.py
@app.get("/stats")
async def get_stats(user_id: str = Depends(verify_token)):
    result = supabase.table("histories") \
        .select("rubric_scores, edit_time_seconds, satisfaction") \
        .eq("user_id", user_id) \
        .execute()

    if not result.data:
        return {
            "total_comments": 0,
            "avg_rubric_scores": {},
            "avg_edit_time_seconds": 0,
            "avg_satisfaction": 0
        }

    # 平均計算
    total = len(result.data)
    rubric_sums = {"理解度": 0, "論理性": 0, "独自性": 0, "実践性": 0, "表現力": 0}
    edit_time_sum = 0
    satisfaction_sum = 0

    for row in result.data:
        for key in rubric_sums:
            rubric_sums[key] += row["rubric_scores"].get(key, 0)
        if row["edit_time_seconds"]:
            edit_time_sum += row["edit_time_seconds"]
        if row["satisfaction"]:
            satisfaction_sum += row["satisfaction"]

    return {
        "total_comments": total,
        "avg_rubric_scores": {k: v / total for k, v in rubric_sums.items()},
        "avg_edit_time_seconds": edit_time_sum / total,
        "avg_satisfaction": satisfaction_sum / total
    }
```

#### ユニットテスト

```python
# tests/test_pii_detector.py
import pytest
from api.pii_detector import PIIDetector

def test_detect_name():
    detector = PIIDetector()
    text = "山田太郎さんが提出したレポートです。"
    matches = detector.detect(text)
    assert len(matches) > 0
    assert matches[0].type == "name"

def test_mask():
    detector = PIIDetector()
    text = "山田太郎さんのメールアドレスは yamada@example.com です。"
    matches = detector.detect(text)
    masked = detector.mask(text, matches)
    assert "[氏名]" in masked
    assert "[メールアドレス]" in masked
```

```bash
pip install pytest pytest-asyncio
pytest tests/
```

---

## Week 12: 検証・改善

**期間**: 1週間
**目標**: UAT実施 + バグ修正

### UAT計画書作成

**ファイル**: `docs/uat_plan.md`

```markdown
# UAT計画書

## 目的
Phase 1 MVPの機能が要件を満たしていることを確認する

## 実施者
教授

## 期間
Week 12（1週間）

## テスト内容
1. 20件のレポートに対してコメント生成
2. Rubric採点精度の確認（教授の採点と比較）
3. 手直し時間の測定
4. 満足度の記入

## 合格基準
- Rubric採点精度: ±1.0以内 80%以上
- 満足度: 平均4.0以上
- 手直し時間削減率: 30%以上

## テストケース
...
```

### ベースライン測定

教授に5件のレポートについて従来通りコメント作成してもらい、時間を計測。

---

## Week 13-14: 最終調整・ドキュメント

**期間**: 1〜2週間
**目標**: 本番デプロイ準備

### ドキュメント作成

- ユーザーマニュアル（docs/user_manual.md）
- 管理者マニュアル（docs/admin_manual.md）
- 緊急対応手順書（docs/incident_response.md）

### Vercelデプロイ

```bash
cd frontend
npm run build
# Vercel Dashboard で自動デプロイ設定
```

---

## コーディング規約

### TypeScript

- ESLintに従う
- コンポーネント名はPascalCase
- 関数名はcamelCase
- 型を明示的に定義

### Python

- PEP 8に従う
- 型ヒントを使用（Python 3.11+）
- docstringを記述

---

## テスト手順

```bash
# フロントエンド
cd frontend
npm run test

# バックエンド
cd backend
pytest tests/
```

---

## トラブルシューティング

### ポートが使用中

```bash
lsof -ti:8010 | xargs kill -9
```

### Supabase接続エラー

環境変数を確認:
```bash
echo $SUPABASE_URL
```

---

**以上**
