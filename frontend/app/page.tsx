/**
 * ルートページ
 *
 * 認証状態に応じて適切なページにリダイレクトします。
 * - 認証済み: /dashboard
 * - 未認証: /login
 */

import { redirect } from 'next/navigation'

export default function Home() {
  // デフォルトではログインページにリダイレクト
  // クライアント側で認証状態を確認してリダイレクトする
  redirect('/login')
}
