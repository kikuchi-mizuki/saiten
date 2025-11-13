import streamlit as st
import requests
import json
import os

try:
	API = st.secrets["API_URL"]
except Exception:
	API = os.environ.get("API_URL")

st.set_page_config(page_title="教授コメント自動化 - MVP", layout="wide")

# ========================================
# Academic Minimal UI - Load CSS Files
# ========================================
def load_css_file(file_path):
	"""Load CSS file content"""
	try:
		with open(file_path, 'r', encoding='utf-8') as f:
			return f.read()
	except FileNotFoundError:
		st.error(f"CSS file not found: {file_path}")
		return ""

# Load design tokens and base styles
CSS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ui')
DESIGN_TOKENS_CSS = load_css_file(os.path.join(CSS_DIR, 'design-tokens.css'))
BASE_CSS = load_css_file(os.path.join(CSS_DIR, 'base.css'))

# Academic Minimal UI - Streamlit Overrides
ACADEMIC_MINIMAL_CSS = """
<style>
/* === Streamlit Overrides for Academic Minimal === */

/* Base */
.main {
  background-color: var(--bg);
}

.main .block-container {
  max-width: 1280px;
  padding: 24px;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--bg);
}

/* === Grid Layout (7:5) === */
[data-testid="column"] {
  padding: 0 12px; /* ガター 24px 相当（左右12pxずつ） */
  display: flex !important;
  flex-direction: column !important;
  align-items: stretch !important;
  height: calc(100vh - 160px) !important; /* ヘッダ/余白を差し引き、高さを統一 */
  min-height: calc(100vh - 160px) !important;
  overflow: hidden;
}

[data-testid="column"]:first-child {
  flex: 0 0 58.333% !important;
}

[data-testid="column"]:last-child {
  flex: 0 0 41.667% !important;
}

/* 右上ボタン行（コピー/クリア）の下罫線＆余白統一 */
[data-testid="column"]:last-child > div:first-child:not([data-testid="stTabs"]) {
  margin-bottom: 12px !important;
  padding-bottom: 12px !important;
  border-bottom: 1px solid #E5E7EB !important;
  flex: 0 0 auto !important;
}

/* マージン用のdivは無視（JavaScriptで処理） */

/* === Typography === */
h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  color: var(--text);
  margin: 0;
}

h1 {
  font-size: 22px;
  line-height: 28px;
  font-weight: var(--font-weight-semibold);
  color: var(--text);
  margin: 0 0 12px 0;
}

h2 {
  font-size: 18px;
  line-height: 26px;
  font-weight: 600;
  color: #1F2937;
  margin: 0 0 12px 0;
}

h3 {
  font-size: 16px !important;
  line-height: 24px;
  font-weight: 600;
  color: #1F2937 !important;
  margin: 0 0 var(--space-3) 0 !important;
}

/* タブパネル先頭のh2の上マージンを消す（重複を避けるため、より詳細なセレクタに統合） */

/* === Textarea === */
.stTextArea {
  background-color: var(--surface-subtle) !important;
  border-radius: 12px !important;
  padding: 0 !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
}

.stTextArea textarea {
  font-family: var(--font-body) !important;
  font-size: var(--font-size-base) !important;
  line-height: var(--line-height-base) !important;
  color: var(--text) !important;
  background-color: var(--surface-subtle) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: var(--space-3) !important; /* 16px相当 */
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
  resize: none !important;
  transition: border-color var(--transition) !important;
  height: 56vh !important; /* 画面に収まる読み書き視野 */
  overflow-y: auto !important;
}

/* コメントエリアのテキストエリアもカード風に */
[data-testid="stTabs"] .stTextArea {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  display: flex !important;
  flex-direction: column !important;
}

[data-testid="stTabs"] .stTextArea textarea {
  background-color: var(--surface-subtle) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
  padding: var(--space-3) !important; /* 16px相当 */
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow-y: auto !important;
}

.stTextArea textarea:focus {
	outline: none !important;
  border: 2px solid var(--accent) !important;
}

.stTextArea textarea::placeholder {
  color: var(--text-muted) !important;
}

/* === Buttons === */
.stButton > button {
  font-family: var(--font-body) !important;
  font-size: var(--font-size-base) !important;
  font-weight: var(--font-weight-medium) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  padding: 0 var(--space-5) !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  line-height: 48px !important;
  box-sizing: border-box !important;
  transition: all var(--transition) !important;
  background-color: var(--surface) !important;
  color: var(--text) !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.stButton > button:not([kind="primary"]):hover:not(:disabled) {
  background-color: #F3F4F6 !important;
  border-color: var(--accent) !important;
}

.stButton > button[kind="primary"] {
  background: #1E3A8A !important;
	color: white !important;
  border-color: #1E3A8A !important;
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  line-height: 48px !important;
  padding: 0 var(--g3) !important;
  border-radius: 12px !important;
  font-weight: var(--font-weight-semibold) !important;
  letter-spacing: 0.01em !important;
  transition: background-color 0.2s ease !important;
  box-sizing: border-box !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

/* CTAボタンは中央揃え・均等幅 */
.bottomCta-content {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  gap: var(--space-4) !important;
  width: 100% !important;
}

.bottomCta-content .stButton {
  flex: 1 1 0 !important;
  max-width: none !important;
  min-width: 0 !important;
}

.bottomCta-content .stButton > button {
  width: 100% !important;
  max-width: 100% !important;
}

/* ====== スマホ/タブレット：縦積み＆視野高の自動化 ====== */
@media (max-width: 1024px) {
  [data-testid="column"] {
    flex: 1 1 auto !important;
    min-height: auto !important;
  }
  
  .stTextArea textarea,
  [data-testid="column"]:last-child [data-testid="stTabs"] > div:last-child {
    height: auto !important;
    max-height: none !important;
  }
  
  .bottomCta-content {
    grid-template-columns: 1fr !important; /* ボタンを縦に */
  }
  
  .bottomCta-content .stButton:first-child {
    width: 100% !important;
  }
  
  .bottomCta-content .stButton {
    width: 100% !important;
  }
  
  .bottomCta-content .stButton > button {
    width: 100% !important;
  }
}

.stButton > button[kind="primary"]:hover:not(:disabled) {
  background: #1B357F !important;
  border-color: #1B357F !important;
}

.stButton > button:focus-visible {
  outline: 2px solid #3B82F6 !important;
  outline-offset: 2px !important;
}

.stButton > button:disabled {
  opacity: 0.5 !important;
  cursor: not-allowed !important;
}

/* === Tabs (Academic Minimal Style) === */
/* Streamlitのタブ構造を尊重しつつ、スタイルを適用 */
[data-testid="stTabs"] {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow: hidden !important;
  margin: 0 !important;
  height: 100%;
}

/* タブボタン行：確実に掴む（role="tablist"で直接指定） */
[data-testid="stTabs"] [role="tablist"] {
  display: flex !important;
  gap: 12px !important;
  height: 48px !important;
  align-items: flex-end !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 2 !important;
  background: var(--surface) !important;
  border-bottom: 1px solid var(--border) !important;
  padding: 0 12px !important;
  margin: 0 !important;
  flex-shrink: 0 !important;
}

/* 右カラムのタブ見出しは固定、パネルはスクロール */
[data-testid="column"]:last-child [data-testid="stTabs"] [role="tablist"] {
  position: sticky !important;
  top: 0 !important;
  z-index: 2 !important;
  background: var(--surface) !important;
}

[data-testid="column"]:last-child [data-testid="stTabs"] > div:last-child {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  max-height: calc(100vh - 208px) !important; /* 1画面に収まる高さ（160pxヘッダー + 48pxタブ） */
  height: calc(100% - 48px) !important; /* タブヘッダー（48px）を除く */
}

/* タブボタン：線で見せる（role="tab"で直接指定） */
[data-testid="stTabs"] [role="tab"] {
  font-family: var(--font-body) !important;
  font-size: 15px !important;
  font-weight: 600 !important;
  color: #6B7280 !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  margin: 0 !important;
  padding: 10px 0 !important;
  transition: all var(--transition) !important;
  height: auto !important;
  min-height: auto !important;
  cursor: pointer !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="false"]:hover {
  color: var(--text) !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: #111827 !important;
  font-weight: 600 !important;
  border-bottom-color: #3B82F6 !important;
  border-bottom-width: 2px !important;
}

[data-testid="stTabs"] [role="tab"]:focus-visible {
  outline: 2px solid var(--accent) !important;
  outline-offset: 2px !important;
}

/* タブパネルコンテナ：残り高さを使い、中だけスクロール */
[data-testid="stTabs"] > div:last-child {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding: var(--space-3) !important; /* 16px相当 */
  border: 1px solid #E5E7EB !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
  background-color: #FFFFFF !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  display: flex !important;
  flex-direction: column !important;
  height: calc(100% - 48px) !important; /* タブヘッダー（48px）を除く */
  max-height: calc(100vh - 208px) !important; /* 1画面に収まる高さ（160px + 48pxタブヘッダー） */
}

/* タブ直下の余白打ち消し */
[data-testid="stTabs"] > div:last-child > div[role="tabpanel"] > :first-child {
  margin-top: 0 !important;
}

/* タブパネル最下部の余白を削除 */
[data-testid="stTabs"] > div:last-child > div[role="tabpanel"] > :last-child {
  margin-bottom: 0 !important;
}

/* 要約タブと評価タブのコンテンツもスクロール可能に */
[data-testid="stTabs"] [role="tabpanel"] {
  max-height: 100% !important;
  overflow-y: visible !important; /* 親コンテナでスクロールを制御 */
  overflow-x: hidden !important;
  height: auto !important;
}

/* 右カラム内のタブコンテナの高さ制御 */
[data-testid="column"]:last-child [data-testid="stTabs"] {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  height: 100% !important;
  max-height: calc(100vh - 160px) !important; /* 1画面に収まる高さ */
  overflow: hidden !important;
  align-self: stretch !important;
}

/* 左カラムのコンテンツエリア */
[data-testid="column"]:first-child > div {
  display: flex !important;
  flex-direction: column !important;
  height: 100% !important;
  flex: 1 1 auto !important;
  min-height: 0 !important;
  justify-content: flex-start !important;
}

/* 左カラムの見出し */
[data-testid="column"]:first-child h3 {
  flex-shrink: 0 !important;
  margin-top: 0 !important;
  margin-bottom: 12px !important;
}

/* 左カラムのテキストエリア */
[data-testid="column"]:first-child .stTextArea {
  flex: 1 1 auto !important;
  min-height: 0 !important;
  margin-bottom: 0 !important;
}

/* 左カラムのボタンエリアを最下部に配置 */
[data-testid="column"]:first-child .bottomCta {
  flex-shrink: 0 !important;
  margin-top: auto !important;
  margin-bottom: 0 !important;
  align-self: stretch !important;
}


/* タブパネル内の見出しスタイル */
[data-testid="stTabs"] > div:last-child h2 {
  font-size: 18px !important;
  line-height: 26px !important;
  font-weight: 600 !important;
  margin: 0 0 var(--g2) 0 !important;
  color: #1F2937 !important;
}

[data-testid="stTabs"] > div:last-child h3 {
  font-size: 16px !important;
  line-height: 24px !important;
  font-weight: 600 !important;
  margin: 0 0 var(--space-3) 0 !important;
  color: #1F2937 !important;
}

/* === Cards === */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"]:last-child,
[data-testid="stVerticalBlock"] > div > [data-testid="stContainer"] {
  background-color: #FFFFFF !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 12px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
  padding: var(--space-3) !important; /* 16px相当 */
}

/* カードの柔らかいバリエーション */
.card--subtle {
  background: #F9FAFB !important;
  border: 1px solid #E5E7EB !important;
  border-radius: 12px !important;
  padding: var(--space-3) !important; /* 16px相当 */
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
}

/* === Metrics (Total Score) === */
.totalScoreLabel {
  text-align: center !important;
  margin-bottom: var(--space-2) !important;
}

.totalScore {
  font-size: 36px !important;
  font-weight: var(--font-weight-bold) !important;
  line-height: 1.2 !important;
  color: var(--text) !important;
  margin-bottom: var(--space-5) !important;
  font-variant-numeric: tabular-nums;
  text-align: center !important;
}

[data-testid="stMetricValue"] {
  color: var(--text) !important;
  font-weight: var(--font-weight-bold) !important;
  font-size: 36px !important;
  line-height: 1.2 !important;
}

[data-testid="stMetricLabel"] {
  color: var(--text-muted) !important;
  font-size: var(--font-size-sm) !important;
  font-weight: var(--font-weight-medium) !important;
  margin-bottom: var(--space-2) !important;
}

/* === Progress Bar === */
.stProgress > div > div > div {
  background-color: var(--accent) !important;
  border-radius: var(--radius-sm) !important;
}

/* === KPI Bar (Rubric) === */
.kpiRow {
  margin-bottom: var(--space-3) !important; /* 16px相当 */
}

.kpiBar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.kpiLabel {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--text);
  min-width: 88px;
}

.kpiBarTrack {
  flex: 1;
  height: 8px;
  background-color: #EEF2FF;
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.kpiBarFill {
  height: 100%;
  background-color: var(--accent);
  border-radius: var(--radius-sm);
  transition: width 0.3s ease;
}

.kpiVal {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--text);
  min-width: 50px;
  text-align: right;
  font-variant-numeric: tabular-nums;
  line-height: 22px;
}

.kpiReason {
  margin-top: var(--space-2);
  padding: var(--space-3);
  background-color: var(--surface-subtle);
  border-radius: var(--radius-sm);
  font-size: 14px;
  line-height: 22px;
  color: var(--text);
}

/* === Paragraph spacing === */
p {
  margin: 0 0 12px !important;
}

/* === Summary === */
.summary {
  max-width: var(--measure);
  color: var(--text);
  line-height: var(--line-height-base) !important;
  margin-top: var(--space-3) !important;
}

.summary p {
  margin: 0 0 var(--space-4) !important;
  line-height: var(--line-height-base) !important;
}

.summary p:first-of-type {
  margin-top: 0 !important;
}

.summary h2 {
  font-size: 18px !important;
  font-weight: 600 !important;
  margin-bottom: var(--space-3) !important;
}

.summary h2 + p,
.summary h3 + p,
.summary h4 + p {
  margin-top: var(--space-4) !important;
}

/* === Bottom CTA (統一された下部ボタン行) === */
.bottomCta {
  position: static !important; /* stickyをやめて行レイアウトに */
  box-shadow: none !important;
  padding: 0 !important;
  background: transparent !important;
  border-top: none !important;
  flex-shrink: 0 !important;
  width: 100% !important;
}

.bottomCta-content {
  width: 100% !important;
  display: grid !important;
  grid-template-columns: 1fr 160px !important; /* 左：生成ボタン、右：クリア */
  gap: var(--g2) !important;
  align-items: center !important;
  margin: 0 !important;
}

/* 生成ボタンは左カラム幅で中央寄せ */
.bottomCta-content .stButton:first-child {
  justify-self: center !important;
  width: min(640px, 100%) !important;
}

.bottomCta-content .stButton {
  flex: 0 0 auto !important;
}

.bottomCta-content .stButton > button {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  line-height: 48px !important;
  padding: 0 16px !important;
  border-radius: 8px !important;
  box-shadow: 0 1px 2px rgba(16, 24, 40, 0.06) !important;
  box-sizing: border-box !important;
  width: 100% !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  vertical-align: middle !important;
}

/* クリアボタンのスタイル統一（primary以外） */
.bottomCta-content .stButton > button:not([kind="primary"]) {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  line-height: 48px !important;
  padding: 0 16px !important;
  box-sizing: border-box !important;
}

/* 生成ボタンのスタイル統一（primary） */
.bottomCta-content .stButton > button[kind="primary"] {
  height: 48px !important;
  min-height: 48px !important;
  max-height: 48px !important;
  line-height: 48px !important;
  padding: 0 16px !important;
  box-sizing: border-box !important;
}


/* === Info Boxes === */
.stAlert {
  border-radius: var(--radius) !important;
  padding: var(--space-4) !important;
  border: 1px solid var(--border) !important;
  background-color: var(--surface-subtle) !important;
}

/* === Radio Buttons === */
[data-testid="stRadio"] {
  background-color: var(--surface) !important;
  padding: var(--space-4) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border) !important;
  margin-bottom: var(--space-3) !important;
  box-shadow: var(--shadow-subtle) !important;
}

[data-testid="stRadio"] label {
  margin-right: var(--space-4) !important;
}

/* === Spinner === */
.stSpinner > div {
  border-color: var(--accent) transparent transparent transparent !important;
}

/* === Divider === */
.kpiDivider {
  height: 1px;
  background-color: #E5E7EB !important;
  margin: var(--space-2) 0 !important; /* 8px相当 */
  width: 100%;
  border: none !important;
}

/* === Scrollbar === */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background-color: var(--border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: var(--text-muted);
}

/* === Responsive === */
@media (max-width: 1024px) {
  .main .block-container {
    padding: var(--space-4);
  }
  
	[data-testid="column"] {
		width: 100% !important;
    flex: 1 1 auto !important;
    height: calc(100vh - 140px);
  }
}

@media (max-width: 768px) {
  .main .block-container {
    padding: var(--space-3);
  }
  
  [data-testid="column"] {
    height: calc(100vh - 120px);
  }
  
  [data-testid="stTabs"] [role="tab"] {
    font-size: var(--font-size-sm) !important;
    padding: var(--space-2) var(--space-3) !important;
    min-height: 40px !important;
  }
  
  h2, h3 {
    font-size: var(--font-size-base) !important;
  }
}

/* === Clear Button Styling (via JS) === */
</style>
"""

# JavaScript for Academic Minimal enhancements
ACADEMIC_MINIMAL_JS = """
<script>
(function() {
  'use strict';
  
  // Style clear button as danger and ensure button heights are aligned
  function styleClearButton() {
    const buttons = document.querySelectorAll('.stButton > button');
    const dangerColor = '#EF4444';
    const targetHeight = '48px';
    
    buttons.forEach(btn => {
      // Ensure all buttons have the same height
      btn.style.setProperty('height', targetHeight, 'important');
      btn.style.setProperty('min-height', targetHeight, 'important');
      btn.style.setProperty('max-height', targetHeight, 'important');
      btn.style.setProperty('line-height', targetHeight, 'important');
      btn.style.setProperty('box-sizing', 'border-box', 'important');
      btn.style.setProperty('display', 'inline-flex', 'important');
      btn.style.setProperty('align-items', 'center', 'important');
      btn.style.setProperty('justify-content', 'center', 'important');
      
      if (btn.textContent && btn.textContent.includes('クリア') && !btn.dataset.styled) {
        btn.dataset.styled = 'true';
        btn.style.setProperty('color', dangerColor, 'important');
        btn.style.setProperty('border-color', dangerColor, 'important');
        
        btn.addEventListener('mouseenter', function() {
          this.style.setProperty('background-color', '#FEF2F2', 'important');
          this.style.setProperty('border-color', dangerColor, 'important');
        });
        
        btn.addEventListener('mouseleave', function() {
          this.style.removeProperty('background-color');
          this.style.setProperty('border-color', dangerColor, 'important');
        });
      }
    });
  }
  
  // Enhanced keyboard navigation for tabs
  function enhanceTabsKeyboardNav() {
    const tabsButtons = document.querySelectorAll('[data-testid="stTabs"] [role="tab"]');
    
    tabsButtons.forEach((button, index) => {
      if (button.dataset.keyboardNav) return;
      button.dataset.keyboardNav = 'true';
      
      button.addEventListener('keydown', (e) => {
        const buttons = Array.from(document.querySelectorAll('[data-testid="stTabs"] [role="tab"]'));
        let targetIndex = index;
        
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
          e.preventDefault();
          targetIndex = (index + 1) % buttons.length;
          buttons[targetIndex].focus();
          buttons[targetIndex].click();
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
          e.preventDefault();
          targetIndex = (index - 1 + buttons.length) % buttons.length;
          buttons[targetIndex].focus();
          buttons[targetIndex].click();
        } else if (e.key === 'Home') {
          e.preventDefault();
          buttons[0].focus();
          buttons[0].click();
        } else if (e.key === 'End') {
          e.preventDefault();
          buttons[buttons.length - 1].focus();
          buttons[buttons.length - 1].click();
        }
      });
    });
  }
  
  // Align bottom edges of left and right columns
  function alignColumnBottoms() {
    const leftColumn = document.querySelector('[data-testid="column"]:first-child');
    const rightColumn = document.querySelector('[data-testid="column"]:last-child');
    
    if (!leftColumn || !rightColumn) return;
    
    // Reset to base height first
    const baseHeight = 'calc(100vh - 160px)';
    leftColumn.style.height = baseHeight;
    leftColumn.style.minHeight = baseHeight;
    rightColumn.style.height = baseHeight;
    rightColumn.style.minHeight = baseHeight;
    
    // Ensure left column content area uses full height and flex layout
    const leftContent = leftColumn.querySelector('> div:first-child');
    if (leftContent) {
      leftContent.style.height = '100%';
      leftContent.style.display = 'flex';
      leftContent.style.flexDirection = 'column';
      leftContent.style.flex = '1 1 auto';
      leftContent.style.minHeight = '0';
    }
    
    // Ensure right column tabs use full height
    const rightTabs = rightColumn.querySelector('[data-testid="stTabs"]');
    if (rightTabs) {
      rightTabs.style.height = '100%';
      rightTabs.style.display = 'flex';
      rightTabs.style.flexDirection = 'column';
      rightTabs.style.flex = '1 1 auto';
      rightTabs.style.minHeight = '0';
    }
    
    // Get button element (bottom of left column) - find the actual button container
    const leftButton = leftColumn.querySelector('.bottomCta');
    // Get tab panel container (bottom of right column)
    const rightTabPanel = rightColumn.querySelector('[data-testid="stTabs"] > div:last-child');
    
    // Ensure button area is at the bottom of left column
    if (leftButton && leftContent) {
      leftButton.style.marginTop = 'auto';
      leftButton.style.flexShrink = '0';
      leftButton.style.marginBottom = '0';
    }
    
    // Measure and align after layout settles
    const alignOnce = () => {
      if (!leftButton || !rightTabPanel) return;
      
      // Force layout recalculation
      void leftColumn.offsetHeight;
      void rightColumn.offsetHeight;
      
      // Get absolute bottom positions in viewport
      const leftButtonRect = leftButton.getBoundingClientRect();
      const rightTabPanelRect = rightTabPanel.getBoundingClientRect();
      
      // Calculate the difference in absolute bottom positions
      const diff = leftButtonRect.bottom - rightTabPanelRect.bottom;
      
      // If difference is significant (more than 1px), adjust
      if (Math.abs(diff) > 1) {
        const currentLeftHeight = leftColumn.offsetHeight;
        const currentRightHeight = rightColumn.offsetHeight;
        
        if (diff > 0) {
          // Left button is lower, increase right column height to match
          const newRightHeight = currentRightHeight + diff;
          rightColumn.style.height = newRightHeight + 'px';
          rightColumn.style.minHeight = newRightHeight + 'px';
        } else {
          // Right panel is lower, increase left column height to match
          const newLeftHeight = currentLeftHeight + Math.abs(diff);
          leftColumn.style.height = newLeftHeight + 'px';
          leftColumn.style.minHeight = newLeftHeight + 'px';
        }
        
        // Verify alignment after adjustment
        setTimeout(() => {
          const leftButtonRect2 = leftButton.getBoundingClientRect();
          const rightTabPanelRect2 = rightTabPanel.getBoundingClientRect();
          const diff2 = leftButtonRect2.bottom - rightTabPanelRect2.bottom;
          if (Math.abs(diff2) > 1) {
            // Fine-tune if still not aligned
            if (diff2 > 0) {
              rightColumn.style.height = (rightColumn.offsetHeight + diff2) + 'px';
            } else {
              leftColumn.style.height = (leftColumn.offsetHeight + Math.abs(diff2)) + 'px';
            }
          }
        }, 50);
      }
    };
    
    // Try multiple times to ensure alignment
    requestAnimationFrame(() => {
      setTimeout(alignOnce, 100);
      setTimeout(alignOnce, 300);
      setTimeout(alignOnce, 500);
    });
  }
  
  // Fix tabs layout: Minimal intervention to preserve Streamlit functionality
  function fixTabsLayout() {
    const leftColumn = document.querySelector('[data-testid="column"]:first-child');
    const rightColumn = document.querySelector('[data-testid="column"]:last-child');
    
    if (!leftColumn || !rightColumn) return;
    
    // Ensure both columns have consistent layout
    leftColumn.style.display = 'flex';
    leftColumn.style.flexDirection = 'column';
    leftColumn.style.height = 'calc(100vh - 160px)';
    leftColumn.style.minHeight = 'calc(100vh - 160px)';
    leftColumn.style.overflow = 'hidden';
    
    rightColumn.style.display = 'flex';
    rightColumn.style.flexDirection = 'column';
    rightColumn.style.height = 'calc(100vh - 160px)';
    rightColumn.style.minHeight = 'calc(100vh - 160px)';
    rightColumn.style.overflow = 'hidden';
    
    // Ensure left column content uses full height
    const leftContent = leftColumn.querySelector('> div:first-child');
    if (leftContent) {
      leftContent.style.display = 'flex';
      leftContent.style.flexDirection = 'column';
      leftContent.style.height = '100%';
      leftContent.style.flex = '1 1 auto';
      leftContent.style.minHeight = '0';
    }
    
    const tabsContainer = rightColumn.querySelector('[data-testid="stTabs"]');
    if (!tabsContainer) return;
    
    // Ensure tabs container is flex column and uses full height
    tabsContainer.style.display = 'flex';
    tabsContainer.style.flexDirection = 'column';
    tabsContainer.style.flex = '1 1 auto';
    tabsContainer.style.minHeight = '0';
    tabsContainer.style.overflow = 'hidden';
    tabsContainer.style.height = '100%';
    
    // Ensure tab buttons row (role="tablist") is sticky and fixed height
    const tabList = tabsContainer.querySelector('[role="tablist"]');
    if (tabList) {
      tabList.style.position = 'sticky';
      tabList.style.top = '0';
      tabList.style.zIndex = '100';
      tabList.style.backgroundColor = '#FFFFFF';
      tabList.style.flexShrink = '0';
      tabList.style.height = '48px';
    }
    
    // Ensure tab panels container (last child) takes remaining space with flex
    const tabPanelsRow = tabsContainer.querySelector('> div:last-child');
    if (tabPanelsRow) {
      tabPanelsRow.style.flex = '1 1 auto';
      tabPanelsRow.style.minHeight = '0';
      tabPanelsRow.style.overflowY = 'auto';
      tabPanelsRow.style.overflowX = 'hidden';
      tabPanelsRow.style.height = '100%';
    }
    
    // Align column bottoms after layout is fixed
    setTimeout(alignColumnBottoms, 100);
  }
  
  // Set aria-busy on generating button
  function setAriaBusyOnGenerating() {
    const generatingButtons = document.querySelectorAll('.stButton > button');
    generatingButtons.forEach(btn => {
      if (btn.textContent && btn.textContent.includes('生成') && btn.disabled) {
        btn.setAttribute('aria-busy', 'true');
      } else if (btn.hasAttribute('aria-busy')) {
        btn.removeAttribute('aria-busy');
      }
    });
  }
  
  // Initialize
  function init() {
    styleClearButton();
    enhanceTabsKeyboardNav();
    setAriaBusyOnGenerating();
    fixTabsLayout();
    alignColumnBottoms();
  }
  
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Watch for DOM changes - minimal intervention
  const observer = new MutationObserver(() => {
    setTimeout(() => {
      styleClearButton();
      enhanceTabsKeyboardNav();
      setAriaBusyOnGenerating();
      fixTabsLayout();
      alignColumnBottoms();
    }, 100);
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: true,
    attributeFilter: ['style', 'class']
  });
  
  // Also align on window resize
  window.addEventListener('resize', () => {
    setTimeout(alignColumnBottoms, 100);
  });
  
  // Periodically check alignment (for dynamic content changes)
  let alignmentInterval = setInterval(() => {
    alignColumnBottoms();
  }, 300);
  
  // Stop interval after 15 seconds (initial layout should be stable by then)
  setTimeout(() => {
    clearInterval(alignmentInterval);
    // Final alignment check
    alignColumnBottoms();
  }, 15000);
})();
</script>
"""

# Inject Academic Minimal styles (design tokens + base + Streamlit overrides)
st.markdown(f"<style>{DESIGN_TOKENS_CSS}{BASE_CSS}</style>", unsafe_allow_html=True)
st.markdown(ACADEMIC_MINIMAL_CSS + ACADEMIC_MINIMAL_JS, unsafe_allow_html=True)

# APIベースURLの自動検出（8010→8001→8000）
if "API_BASE" not in st.session_state:
	candidate = API
	if not candidate:
		for base in [
			"http://127.0.0.1:8010", "http://localhost:8010",
			"http://127.0.0.1:8001", "http://localhost:8001",
			"http://127.0.0.1:8000", "http://localhost:8000",
		]:
			try:
				r = requests.get(f"{base}/health", timeout=3.0)
				if r.ok:
					candidate = base
					break
			except Exception:
				continue
	st.session_state.API_BASE = candidate or "http://127.0.0.1:8010"

API_BASE = st.session_state.API_BASE

# ---- レイアウト
col1, col2 = st.columns([7, 5], gap="medium")

with col1:
	# レポート本文エリア（flex: 1で伸縮可能）
	st.markdown("### レポート本文")
	report_text = st.text_area(
		"貼り付けてください",
		height=400,
		label_visibility="collapsed",
		placeholder="学生のレポート本文をここに貼り付け…\n\n（複数行の長文も対応できます）",
		key="report_input"
	)
	
	# 生成ボタンとクリアボタン（Bottom CTA - 横並び、sticky bottom）
	st.markdown('<div class="bottomCta"><div class="bottomCta-content">', unsafe_allow_html=True)
	cta_col1, cta_col2 = st.columns([3, 1], gap="small")
	with cta_col1:
		generate = st.button("採点＆下書きを生成", type="primary", use_container_width=True, key="generate_button")
	with cta_col2:
		clear_all_bottom = st.button("クリア", use_container_width=True, key="clear_bottom")
	st.markdown('</div></div>', unsafe_allow_html=True)
	
	# クリアボタンの処理（下部CTAから）
	if clear_all_bottom:
		st.session_state.ai_comment = ""
		st.session_state.rubric = {}
		st.session_state.summary = None
		st.session_state.llm_used = None
		st.session_state.llm_error = None
		st.session_state.summary_llm_used = None
		st.session_state.summary_error = None
		st.session_state.comment_update_count = st.session_state.get("comment_update_count", 0) + 1
		st.rerun()

with col2:
	# セッションステートの初期化
	if "ai_comment" not in st.session_state:
		st.session_state.ai_comment = ""
		st.session_state.rubric = {}
		st.session_state.summary = None
		st.session_state.llm_used = None
		st.session_state.llm_error = None
		st.session_state.summary_llm_used = None  # 要約生成でLLMが使われたか
		st.session_state.summary_error = None  # 要約生成のエラーメッセージ
		st.session_state.generated = False
		st.session_state.active_tab = "コメント"
		st.session_state.is_generating = False
	
	
	# タブ選択（順番：要約、コメント、評価）
	tab1, tab2, tab3 = st.tabs(["要約", "コメント", "評価"])
	
	# タブ1: 要約
	with tab1:
		st.session_state.active_tab = "要約"
		st.markdown("### レポート要約")
		
		if st.session_state.summary:
			summary = st.session_state.summary
			summary_error = st.session_state.get("summary_error")
			
			# エラーがある場合はエラーメッセージを表示
			if summary_error:
				st.error(f"要約生成エラー: {summary_error}")
			
			# フォーマット済み要約またはエグゼクティブサマリーを表示
			summary_text = summary.get("formatted") or summary.get("executive", "要約を生成中...")
			if summary_text and summary_text != "要約を生成中...":
				# Markdown形式で表示（改行や太字が正しく表示される）
				# HTMLのdivタグで囲みつつ、Markdownを処理
				st.markdown(f'<div class="summary">', unsafe_allow_html=True)
				st.markdown(summary_text)  # Markdownテキストを直接表示
				st.markdown('</div>', unsafe_allow_html=True)
				
				# LLM使用状況を表示（エラーがない場合のみ）
				summary_llm_used = st.session_state.get("summary_llm_used")
				if summary_llm_used is not None and not summary_error:
					status_text = "要約: AI使用"
					status_color = "#10B981"
					st.markdown(
						f'<div style="position: relative; text-align: right; margin-top: var(--space-2); font-size: 13px; color: {status_color}; font-weight: 500;">{status_text}</div>',
						unsafe_allow_html=True
					)
			else:
				if not summary_error:
					st.info("要約を生成中...")
		else:
			st.info("レポートを生成すると、要約が表示されます。")
	
	# タブ2: コメント
	with tab2:
		st.session_state.active_tab = "コメント"
		st.markdown("### AI下書き（教授コメント）")
		
		# コメントエリアの表示（常に表示）
		if st.session_state.get("generated", False) and st.session_state.ai_comment:
			st.session_state.generated = False
			st.session_state.comment_update_count = st.session_state.get("comment_update_count", 0) + 1

		current_comment = st.session_state.get("ai_comment", "") or ""
		
		if current_comment:
			comment_key = f"comment_textarea_{st.session_state.get('comment_update_count', 0)}"
			comment_area = st.text_area(
				"生成結果（編集可能）",
				value=current_comment,
				height=300,
				label_visibility="collapsed",
				key=comment_key
			)
		else:
			comment_area = st.text_area(
				"生成結果（編集可能）",
				value="",
				height=300,
				label_visibility="collapsed",
				placeholder="生成されたコメントがここに表示されます…",
				key="comment_textarea_empty"
			)
		
		if comment_area and comment_area != current_comment:
			st.session_state.ai_comment = comment_area
		
		# LLMステータスラベル（右下に固定）
		if st.session_state.llm_used is not None:
			status_text = "LLM: 有効" if st.session_state.llm_used else "LLM: 未使用"
			status_color = "#10B981" if st.session_state.llm_used else "#9CA3AF"
			st.markdown(
				f'<div style="position: relative; text-align: right; margin-top: var(--space-2); font-size: 13px; color: {status_color}; font-weight: 500;">{status_text}</div>',
				unsafe_allow_html=True
			)
		
		
	
	# タブ3: 評価（Rubric）
	with tab3:
		st.session_state.active_tab = "評価"
		st.markdown("### Rubric採点結果")
		
		if st.session_state.rubric:
			rubric = st.session_state.rubric
			
			def get_score_value(category):
				value = rubric.get(category, 0)
				if isinstance(value, dict):
					return value.get("score", 0)
				return value
			
			def get_reason(category):
				value = rubric.get(category, {})
				if isinstance(value, dict):
					return value.get("reason", "")
				return ""
			
			categories = ["理解度", "論理性", "独自性", "実践性", "表現力"]
			total = sum(get_score_value(cat) for cat in categories)
			
			# 合計スコア（.totalScoreスタイル）
			st.markdown(f'<div class="totalScoreLabel">合計スコア</div><div class="totalScore">{total} / 25</div>', unsafe_allow_html=True)
			st.markdown('<div class="kpiDivider"></div>', unsafe_allow_html=True)
			
			# KPI行
			for i, category in enumerate(categories):
				score = get_score_value(category)
				reason = get_reason(category)
				progress_width = (score / 5.0) * 100
				
				# KPI Bar HTML
				kpi_html = f'''
				<div class="kpiRow">
					<div class="kpiBar">
						<span class="kpiLabel">{category}</span>
						<div class="kpiBarTrack">
							<div class="kpiBarFill" style="width: {progress_width}%"></div>
						</div>
						<span class="kpiVal">{score} / 5</span>
					</div>
				'''
				
				if reason:
					kpi_html += f'<div class="kpiReason">{reason}</div>'
				else:
					if score >= 4:
						reason_text = f"{category}が高い水準にあります"
					elif score >= 3:
						reason_text = f"{category}が標準的な水準です"
					else:
						reason_text = f"{category}の向上の余地があります"
					kpi_html += f'<div class="kpiReason">{reason_text}</div>'
				
				kpi_html += '</div>'
				st.markdown(kpi_html, unsafe_allow_html=True)
				
				# 最後の項目以外はdividerを追加
				if i < len(categories) - 1:
					st.markdown('<div class="kpiDivider"></div>', unsafe_allow_html=True)
		else:
			st.info("レポートを生成すると、Rubric採点結果が表示されます。")

# ---- 動作
if generate:
	if not report_text.strip():
		st.error("レポート本文を貼り付けてください。")
	else:
		st.session_state.is_generating = True
		with st.spinner("AIがコメントを生成中です..."):
			success = False
			error_message = None
			
			try:
				r = requests.post(f"{API_BASE}/generate_direct", json={"text": report_text, "type":"reflection"}, timeout=60)
				if r.status_code == 200:
					success = True
				elif r.status_code == 404:
					for alt in [
						"http://127.0.0.1:8010", "http://localhost:8010",
						"http://127.0.0.1:8001", "http://localhost:8001",
						"http://127.0.0.1:8000", "http://localhost:8000",
					]:
						try:
							alt_health = requests.get(f"{alt}/health", timeout=3.0)
							if alt_health.ok:
								st.session_state.API_BASE = alt
								API_BASE = alt
								r = requests.post(f"{API_BASE}/generate_direct", json={"text": report_text, "type":"reflection"}, timeout=60)
								if r.status_code == 200:
									success = True
								break
						except Exception as e:
							error_message = f"API接続エラー ({alt}): {str(e)}"
							continue
				else:
					error_message = f"APIエラー: ステータスコード {r.status_code}"
					
				if success:
					data = r.json()
					
					st.session_state.ai_comment = data.get("ai_comment", "")
					st.session_state.rubric = data.get("rubric", {})
					st.session_state.summary = data.get("summary")
					st.session_state.llm_used = data.get("llm_used")
					st.session_state.llm_error = data.get("llm_error")
					st.session_state.summary_llm_used = data.get("summary_llm_used", False)  # 要約生成でLLMが使われたか
					st.session_state.summary_error = data.get("summary_error")  # 要約生成のエラーメッセージ（あれば）
					st.session_state.generated = True
					st.session_state.comment_update_count = st.session_state.get("comment_update_count", 0) + 1
					st.session_state.is_generating = False
					
					if st.session_state.ai_comment:
						st.success("コメントが生成されました！")
					else:
						st.warning("コメントが空です。APIレスポンスを確認してください。")
					
					st.rerun()
				else:
					st.session_state.is_generating = False
					if not error_message:
						error_message = f"APIレスポンスの処理に失敗しました (ステータス: {r.status_code})"
					st.error(f"生成に失敗しました\n\n**エラー**: {error_message}\n\n**API URL**: {API_BASE}")
					
			except requests.exceptions.ConnectionError as e:
				st.session_state.is_generating = False
				st.error(f"APIサーバーに接続できません\n\n**API URL**: {API_BASE}\n\n**解決方法**: APIサーバーを起動してください")
			except requests.exceptions.Timeout as e:
				st.session_state.is_generating = False
				st.error(f"APIリクエストがタイムアウトしました\n\n**API URL**: {API_BASE}")
			except Exception as e:
				st.session_state.is_generating = False
				st.error(f"予期しないエラーが発生しました\n\n**エラー**: {str(e)}\n\n**API URL**: {API_BASE}")
