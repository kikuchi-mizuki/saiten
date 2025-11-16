/**
 * Supabase Client Configuration
 *
 * このファイルでは、Supabaseのクライアント接続を設定します。
 * 環境変数から必要な情報を取得し、型安全なクライアントを提供します。
 */

import { createClient } from '@supabase/supabase-js'

// 環境変数の取得と型安全性の確保
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_URL')
}

if (!supabaseAnonKey) {
  throw new Error('Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY')
}

/**
 * Supabaseクライアント（ブラウザ用）
 *
 * このクライアントは、フロントエンドのコンポーネントから直接使用できます。
 * Row Level Security (RLS)により、ユーザーは自分のデータのみにアクセス可能です。
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey)
