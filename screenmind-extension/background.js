// ScreenMind 浏览器扩展 - 背景脚本
console.log('🚀 ScreenMind 扩展已启动');

// 默认设置
const DEFAULT_SETTINGS = {
  serverUrl: 'http://localhost:8000',
  autoAnalyze: true,
  showNotifications: true
};

// 初始化扩展
chrome.runtime.onInstalled.addListener(async () => {
  console.log('📦 ScreenMind 扩展已安装');
  
  // 设置默认配置
  await chrome.storage.sync.set(DEFAULT_SETTINGS);
  
  // 显示欢迎通知
  chrome.notifications.create({
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title: 'ScreenMind 扩展已安装',
    message: '按 Cmd+Shift+S (Mac) 或 Ctrl+Shift+S 开始截屏分析！'
  });
});

// 监听快捷键命令
chrome.commands.onCommand.addListener(async (command) => {
  console.log('⌨️ 快捷键触发:', command);
  
  if (command === 'capture-screen') {
    await captureAndAnalyze();
  }
});

// 截屏并分析函数
async function captureAndAnalyze() {
  try {
    console.log('📸 开始截屏...');
    
    // 获取设置
    const settings = await chrome.storage.sync.get(DEFAULT_SETTINGS);
    
    // 显示开始通知
    if (settings.showNotifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'ScreenMind',
        message: '正在截屏...'
      });
    }
    
    // 获取当前活动标签页
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
      throw new Error('无法获取当前标签页');
    }
    
    // 截取标签页
    const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
      format: 'png',
      quality: 90
    });
    
    console.log('✅ 截屏完成');
    
    if (settings.autoAnalyze) {
      await analyzeScreenshot(dataUrl, settings);
    } else {
      // 存储截屏数据供后续使用
      await chrome.storage.local.set({ lastScreenshot: dataUrl });
      
      if (settings.showNotifications) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: 'ScreenMind',
          message: '截屏完成！点击扩展图标查看结果。'
        });
      }
    }
    
  } catch (error) {
    console.error('❌ 截屏失败:', error);
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'ScreenMind - 错误',
      message: `截屏失败: ${error.message}`
    });
  }
}

// 分析截屏函数
async function analyzeScreenshot(dataUrl, settings) {
  try {
    console.log('🤖 开始AI分析...');
    
    // 显示分析通知
    if (settings.showNotifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'ScreenMind',
        message: '正在AI分析中...'
      });
    }
    
    // 将dataUrl转换为blob
    const response = await fetch(dataUrl);
    const blob = await response.blob();
    
    // 创建FormData
    const formData = new FormData();
    formData.append('image', blob, 'screenshot.png');
    
    // 调用ScreenMind API
    const apiResponse = await fetch(`${settings.serverUrl}/api/v1/analyze`, {
      method: 'POST',
      body: formData
    });
    
    if (!apiResponse.ok) {
      const errorData = await apiResponse.json();
      throw new Error(errorData.detail || `API错误: ${apiResponse.status}`);
    }
    
    const result = await apiResponse.json();
    
    console.log('✅ 分析完成:', result);
    
    // 存储分析结果
    await chrome.storage.local.set({
      lastScreenshot: dataUrl,
      lastAnalysis: result,
      lastAnalysisTime: Date.now()
    });
    
    // 显示结果通知
    if (settings.showNotifications) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'ScreenMind - 分析完成',
        message: '点击扩展图标查看详细结果！'
      });
    }
    
    // 向当前标签页发送结果
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      chrome.tabs.sendMessage(tab.id, {
        type: 'ANALYSIS_COMPLETE',
        data: result
      }).catch(() => {
        // 忽略发送失败（可能页面不支持内容脚本）
      });
    }
    
  } catch (error) {
    console.error('❌ 分析失败:', error);
    
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'ScreenMind - 分析失败',
      message: `分析失败: ${error.message}`
    });
    
    // 存储错误信息
    await chrome.storage.local.set({
      lastError: error.message,
      lastErrorTime: Date.now()
    });
  }
}

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'CAPTURE_SCREEN') {
    captureAndAnalyze().then(() => {
      sendResponse({ success: true });
    }).catch((error) => {
      sendResponse({ success: false, error: error.message });
    });
    return true; // 保持消息通道开放
  }
  
  if (request.type === 'GET_LAST_RESULT') {
    chrome.storage.local.get(['lastScreenshot', 'lastAnalysis', 'lastError']).then((data) => {
      sendResponse(data);
    });
    return true;
  }
});

// 监听通知点击
chrome.notifications.onClicked.addListener((notificationId) => {
  // 打开扩展弹窗或新标签页显示结果
  chrome.action.openPopup();
});