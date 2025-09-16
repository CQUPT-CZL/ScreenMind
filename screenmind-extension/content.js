// ScreenMind 浏览器扩展 - 内容脚本
console.log('📄 ScreenMind 内容脚本已加载');

// 创建结果显示容器
let resultContainer = null;

// 监听来自背景脚本的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'ANALYSIS_COMPLETE') {
    showAnalysisResult(request.data);
    sendResponse({ received: true });
  }
});

// 显示分析结果
function showAnalysisResult(result) {
  try {
    // 移除之前的结果容器
    if (resultContainer) {
      resultContainer.remove();
    }
    
    // 创建结果容器
    resultContainer = document.createElement('div');
    resultContainer.id = 'screenmind-result-container';
    resultContainer.innerHTML = `
      <div id="screenmind-result-panel">
        <div id="screenmind-result-header">
          <h3>🤖 ScreenMind 分析结果</h3>
          <button id="screenmind-close-btn">✕</button>
        </div>
        <div id="screenmind-result-content">
          <div class="screenmind-analysis">
            <h4>📝 分析内容</h4>
            <div class="screenmind-analysis-text">${result.data.analysis}</div>
          </div>
          ${result.data.answer ? `
            <div class="screenmind-answer">
              <h4>💡 答案解析</h4>
              <div class="screenmind-answer-text">${result.data.answer}</div>
            </div>
          ` : ''}
          <div class="screenmind-meta">
            <small>⏱️ 分析耗时：${result.data.analysis_time}秒 | 🚀 ScreenMind AI</small>
          </div>
        </div>
      </div>
    `;
    
    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      #screenmind-result-container {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 400px;
        max-height: 80vh;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-radius: 12px;
        overflow: hidden;
        animation: slideIn 0.3s ease-out;
      }
      
      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
      
      #screenmind-result-panel {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        overflow: hidden;
      }
      
      #screenmind-result-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
      }
      
      #screenmind-result-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
      
      #screenmind-close-btn {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }
      
      #screenmind-close-btn:hover {
        background: rgba(255,255,255,0.3);
      }
      
      #screenmind-result-content {
        padding: 20px;
        max-height: 60vh;
        overflow-y: auto;
        background: rgba(255,255,255,0.95);
        color: #333;
      }
      
      .screenmind-analysis, .screenmind-answer {
        margin-bottom: 20px;
      }
      
      .screenmind-analysis h4, .screenmind-answer h4 {
        margin: 0 0 10px 0;
        font-size: 14px;
        font-weight: 600;
        color: #4a5568;
      }
      
      .screenmind-analysis-text, .screenmind-answer-text {
        background: #f7fafc;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        line-height: 1.6;
        font-size: 14px;
        white-space: pre-wrap;
      }
      
      .screenmind-meta {
        text-align: center;
        color: #718096;
        font-size: 12px;
        margin-top: 15px;
        padding-top: 15px;
        border-top: 1px solid #e2e8f0;
      }
      
      #screenmind-result-content::-webkit-scrollbar {
        width: 6px;
      }
      
      #screenmind-result-content::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }
      
      #screenmind-result-content::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
      }
      
      #screenmind-result-content::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
      }
    `;
    
    // 添加到页面
    document.head.appendChild(style);
    document.body.appendChild(resultContainer);
    
    // 绑定关闭事件
    const closeBtn = document.getElementById('screenmind-close-btn');
    closeBtn.addEventListener('click', () => {
      resultContainer.style.animation = 'slideOut 0.3s ease-in forwards';
      setTimeout(() => {
        if (resultContainer) {
          resultContainer.remove();
          resultContainer = null;
        }
      }, 300);
    });
    
    // 添加滑出动画
    const slideOutStyle = document.createElement('style');
    slideOutStyle.textContent = `
      @keyframes slideOut {
        from {
          transform: translateX(0);
          opacity: 1;
        }
        to {
          transform: translateX(100%);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(slideOutStyle);
    
    // 5秒后自动关闭
    setTimeout(() => {
      if (resultContainer) {
        closeBtn.click();
      }
    }, 8000);
    
    console.log('✅ 分析结果已显示');
    
  } catch (error) {
    console.error('❌ 显示结果失败:', error);
  }
}

// 监听键盘快捷键（作为备用方案）
document.addEventListener('keydown', (event) => {
  // Cmd+Shift+S (Mac) 或 Ctrl+Shift+S (Windows/Linux)
  if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key === 'S') {
    // 这里不处理，让背景脚本处理
    // 只是为了确保快捷键不会被页面拦截
    console.log('⌨️ 检测到快捷键，由背景脚本处理');
  }
});