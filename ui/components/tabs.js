/* ========================================
   Tabs Component - JavaScript (WAI-ARIA)
   ======================================== */

(function() {
  'use strict';

  function initTabs() {
    const tabsContainers = document.querySelectorAll('.commercial-tabs');
    
    tabsContainers.forEach(container => {
      const triggers = container.querySelectorAll('.commercial-tabs-trigger');
      const panels = container.querySelectorAll('.commercial-tabs-panel');
      
      if (triggers.length === 0 || panels.length === 0) return;
      
      // 初期状態を設定
      triggers[0].setAttribute('aria-selected', 'true');
      triggers[0].setAttribute('tabindex', '0');
      panels[0].setAttribute('aria-hidden', 'false');
      
      for (let i = 1; i < triggers.length; i++) {
        triggers[i].setAttribute('aria-selected', 'false');
        triggers[i].setAttribute('tabindex', '-1');
        panels[i].setAttribute('aria-hidden', 'true');
      }
      
      // クリックハンドラ
      triggers.forEach((trigger, index) => {
        trigger.addEventListener('click', () => {
          switchTab(container, index);
        });
        
        // キーボードナビゲーション
        trigger.addEventListener('keydown', (e) => {
          let targetIndex = index;
          
          if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            e.preventDefault();
            targetIndex = (index + 1) % triggers.length;
          } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            targetIndex = (index - 1 + triggers.length) % triggers.length;
          } else if (e.key === 'Home') {
            e.preventDefault();
            targetIndex = 0;
          } else if (e.key === 'End') {
            e.preventDefault();
            targetIndex = triggers.length - 1;
          } else if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            switchTab(container, index);
            return;
          } else {
            return; // 他のキーは処理しない
          }
          
          switchTab(container, targetIndex);
          triggers[targetIndex].focus();
        });
      });
    });
    
    function switchTab(container, index) {
      const triggers = container.querySelectorAll('.commercial-tabs-trigger');
      const panels = container.querySelectorAll('.commercial-tabs-panel');
      
      if (index < 0 || index >= triggers.length) return;
      
      // すべてのタブを非アクティブに
      triggers.forEach((trigger, i) => {
        trigger.setAttribute('aria-selected', 'false');
        trigger.setAttribute('tabindex', '-1');
        if (i < panels.length) {
          panels[i].setAttribute('aria-hidden', 'true');
        }
      });
      
      // 選択されたタブをアクティブに
      triggers[index].setAttribute('aria-selected', 'true');
      triggers[index].setAttribute('tabindex', '0');
      if (index < panels.length) {
        panels[index].setAttribute('aria-hidden', 'false');
      }
      
      // カスタムイベントを発火（Streamlitとの連携用）
      container.dispatchEvent(new CustomEvent('tab-change', {
        detail: { index, tabId: triggers[index].getAttribute('aria-controls') }
      }));
    }
  }
  
  // DOMContentLoaded時に初期化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTabs);
  } else {
    initTabs();
  }
  
  // StreamlitのDOM更新を監視
  const observer = new MutationObserver(() => {
    initTabs();
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();

