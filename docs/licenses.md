# OSSライセンス一覧

**最終更新**: 2025-11-11
**バージョン**: 1.0

本システムで使用しているオープンソースソフトウェア（OSS）とそのライセンス情報を記載します。

---

## Frontend（Next.js）

| パッケージ名 | バージョン | ライセンス | リポジトリURL |
|------------|----------|-----------|-------------|
| Next.js | 14.x | MIT License | https://github.com/vercel/next.js |
| React | 18.x | MIT License | https://github.com/facebook/react |
| React DOM | 18.x | MIT License | https://github.com/facebook/react |
| TypeScript | 5.x | Apache License 2.0 | https://github.com/microsoft/TypeScript |
| TailwindCSS | 3.x | MIT License | https://github.com/tailwindlabs/tailwindcss |
| @supabase/supabase-js | latest | MIT License | https://github.com/supabase/supabase-js |
| @supabase/ssr | latest | MIT License | https://github.com/supabase/auth-helpers |

### 開発依存パッケージ

| パッケージ名 | バージョン | ライセンス | リポジトリURL |
|------------|----------|-----------|-------------|
| ESLint | 8.x | MIT License | https://github.com/eslint/eslint |
| Prettier | latest | MIT License | https://github.com/prettier/prettier |
| PostCSS | 8.x | MIT License | https://github.com/postcss/postcss |
| Autoprefixer | 10.x | MIT License | https://github.com/postcss/autoprefixer |

---

## Backend（FastAPI）

| パッケージ名 | バージョン | ライセンス | リポジトリURL |
|------------|----------|-----------|-------------|
| FastAPI | 0.109+ | MIT License | https://github.com/tiangolo/fastapi |
| Uvicorn | 0.24+ | BSD 3-Clause License | https://github.com/encode/uvicorn |
| Pydantic | 2.x | MIT License | https://github.com/pydantic/pydantic |
| Starlette | latest | BSD 3-Clause License | https://github.com/encode/starlette |
| python-multipart | latest | Apache License 2.0 | https://github.com/andrew-d/python-multipart |
| cryptography | 42+ | Apache License 2.0 / BSD | https://github.com/pyca/cryptography |
| openai | latest | Apache License 2.0 | https://github.com/openai/openai-python |
| httpx | latest | BSD 3-Clause License | https://github.com/encode/httpx |
| supabase | latest | MIT License | https://github.com/supabase-community/supabase-py |
| python-dotenv | latest | BSD 3-Clause License | https://github.com/theskumar/python-dotenv |

### 開発・テスト依存パッケージ

| パッケージ名 | バージョン | ライセンス | リポジトリURL |
|------------|----------|-----------|-------------|
| pytest | latest | MIT License | https://github.com/pytest-dev/pytest |
| pytest-asyncio | latest | Apache License 2.0 | https://github.com/pytest-dev/pytest-asyncio |
| black | latest | MIT License | https://github.com/psf/black |
| flake8 | latest | MIT License | https://github.com/PyCQA/flake8 |
| mypy | latest | MIT License | https://github.com/python/mypy |

---

## Infrastructure & Services

### Supabase

| コンポーネント | ライセンス | リポジトリURL |
|--------------|-----------|-------------|
| Supabase（総合） | Apache License 2.0 | https://github.com/supabase/supabase |
| PostgreSQL | PostgreSQL License | https://www.postgresql.org/about/licence/ |
| PostgREST | MIT License | https://github.com/PostgREST/postgrest |
| GoTrue（Auth） | MIT License | https://github.com/netlify/gotrue |
| Realtime | Apache License 2.0 | https://github.com/supabase/realtime |

### Vercel

- **サービス**: Vercel Platform
- **ライセンス**: プロプライエタリ（商用サービス）
- **利用規約**: https://vercel.com/legal/terms

### OpenAI API

- **サービス**: OpenAI API
- **ライセンス**: プロプライエタリ（商用サービス）
- **利用規約**: https://openai.com/policies/terms-of-use

---

## 既存実装（Streamlit - Phase 1では非使用）

| パッケージ名 | バージョン | ライセンス | リポジトリURL |
|------------|----------|-----------|-------------|
| Streamlit | 1.28+ | Apache License 2.0 | https://github.com/streamlit/streamlit |
| Requests | 2.31+ | Apache License 2.0 | https://github.com/psf/requests |

---

## ライセンス詳細

### MIT License

**許諾内容**:
- 商用利用可能
- 修正可能
- 配布可能
- サブライセンス可能
- 私的使用可能

**条件**:
- ライセンス表示が必要
- 著作権表示が必要

**免責**:
- 無保証

### Apache License 2.0

**許諾内容**:
- 商用利用可能
- 修正可能
- 配布可能
- サブライセンス可能
- 私的使用可能
- 特許使用可能

**条件**:
- ライセンス表示が必要
- 変更箇所の明示が必要
- NOTICE ファイルの保持が必要

**免責**:
- 無保証

### BSD 3-Clause License

**許諾内容**:
- 商用利用可能
- 修正可能
- 配布可能
- 私的使用可能

**条件**:
- ライセンス表示が必要
- 著作権表示が必要

**免責**:
- 無保証

### PostgreSQL License

**概要**: MITライセンスに類似した寛容なライセンス

**許諾内容**:
- 商用利用可能
- 修正可能
- 配布可能
- 私的使用可能

**条件**:
- 著作権表示が必要

**免責**:
- 無保証

---

## ライセンスファイルの保存場所

各OSSのライセンス全文は、以下の場所に保存されています：

- **Frontend**: `frontend/node_modules/<package-name>/LICENSE`
- **Backend**: `backend/.venv/lib/python3.11/site-packages/<package-name>/LICENSE`

または、各パッケージのGitHubリポジトリで確認できます。

---

## ライセンス遵守の確認

本システムは、すべてのOSSライセンスを遵守しています：

1. ✅ **ライセンス表示**: 本ドキュメントで全OSS のライセンスを明示
2. ✅ **著作権表示**: 各パッケージの著作権を尊重
3. ✅ **変更箇所の明示**: ソースコードのコメントで明示（該当する場合）
4. ✅ **ライセンス全文の保持**: 各パッケージのLICENSEファイルを保持

---

## 更新履歴

| 日付 | 変更内容 |
|------|---------|
| 2025-11-11 | 初版作成 |

---

## お問い合わせ

本ライセンス情報に関するお問い合わせは、システム管理者までご連絡ください。
