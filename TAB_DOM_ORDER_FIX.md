# タブDOM順序固定パッチ - 実装サマリー

## ✅ 問題点と解決策

### 問題
タブがカードの一番下にレンダリングされ、`position: sticky`が効かない。
`position: sticky`は「自分が上にある」ときだけ効くため、DOM順序が下だと機能しない。

### 解決策
1. **CSS `order`プロパティで順序を固定**
   - タブボタン行（`div:first-child`）: `order: 0`（常に上）
   - タブパネル（`div:last-child`）: `order: 1`（常に下）

2. **タブボタン行を`position: sticky`に設定**
   - `top: 0`で常に上部に固定
   - `z-index: 100`で前面に表示

3. **タブパネルの高さ制御**
   - `flex: 1 1 auto`で残りのスペースを占有
   - `overflow: auto`で内部スクロール

## 🎨 実装内容

### ① タブボタン行の固定
```css
[data-testid="stTabs"] > div:first-child {
  order: 0 !important;
  position: sticky !important;
  top: 0 !important;
  height: 48px !important;
  flex: 0 0 48px !important;
  /* ... */
}
```

### ② タブパネルの高さ制御
```css
[data-testid="stTabs"] > div:last-child {
  order: 1 !important;
  flex: 1 1 auto !important;
  overflow: auto !important;
  min-height: 0 !important;
  /* ... */
}
```

### ③ 見出しのマージン調整
- タブパネル先頭要素の上マージンを0に
- タブパネル内のh2/h3を`18px/26px, 600, margin: 0 0 var(--g2)`

### ④ 末端処理
- タブパネル先頭要素: `margin-top: 0`
- タブパネル末尾要素: `margin-bottom: 0`

## 📊 期待効果

- ✅ タブが常に上部に固定される
- ✅ `position: sticky`が正しく機能する
- ✅ タブ下の謎の余白が解消される
- ✅ 見出しの位置が各タブで完全に揃う
- ✅ 右パネルのスクロールがタブの下から始まる

## 🎉 完了

DOM順序をCSS `order`で固定し、タブを常に上部に表示するように修正しました。
機能ロジックは一切変更せず、CSSのみで実現しています。

