/**
 * 認証関連のヘルパー関数
 *
 * 認証状態の確認、ユーザー情報の取得などを行います。
 */

import { supabase } from './supabase'

/**
 * 現在のユーザー情報を取得
 *
 * @returns ユーザー情報（未認証の場合はnull）
 */
export async function getCurrentUser() {
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser()

  if (error) {
    console.error('Get user error:', error)
    return null
  }

  return user
}

/**
 * 現在のセッション情報を取得
 *
 * @returns セッション情報（未認証の場合はnull）
 */
export async function getSession() {
  const {
    data: { session },
    error,
  } = await supabase.auth.getSession()

  if (error) {
    console.error('Get session error:', error)
    return null
  }

  return session
}

/**
 * 認証状態を確認
 *
 * @returns 認証済みの場合true
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getSession()
  return session !== null
}

/**
 * ログアウト処理
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut()

  if (error) {
    console.error('Sign out error:', error)
    throw error
  }
}

/**
 * 現在のアクセストークンを取得
 *
 * @returns JWT access token（未認証の場合はnull）
 */
export async function getAccessToken(): Promise<string | null> {
  const session = await getSession()
  return session?.access_token ?? null
}
