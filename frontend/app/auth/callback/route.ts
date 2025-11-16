/**
 * OAuth認証コールバックハンドラ
 *
 * Google認証後にSupabaseからリダイレクトされるエンドポイント。
 * 認証コードをセッションに交換し、ダッシュボードにリダイレクトします。
 */

import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'

export async function GET(request: Request) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')

  // 本番環境のホストを取得（X-Forwarded-Hostヘッダーを優先）
  const forwardedHost = request.headers.get('x-forwarded-host')
  const protocol = request.headers.get('x-forwarded-proto') || 'https'
  const host = forwardedHost || requestUrl.host
  const origin = `${protocol}://${host}`

  if (code) {
    // Supabaseクライアントを作成
    const supabase = createClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
    )

    // 認証コードをセッションに交換
    const { error } = await supabase.auth.exchangeCodeForSession(code)

    if (error) {
      console.error('Auth callback error:', error)
      // エラー時はログインページにリダイレクト
      return NextResponse.redirect(new URL('/login?error=auth_failed', origin))
    }
  }

  // 認証成功後はダッシュボードにリダイレクト
  return NextResponse.redirect(new URL('/dashboard', origin))
}
