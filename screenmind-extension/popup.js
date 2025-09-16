// ScreenMind 扩展弹窗脚本
console.log('🎯 ScreenMind 弹窗已加载');

// DOM 元素
const captureBtn = document.getElementById('captureBtn');
const captureIcon = document.getElementById('captureIcon');
const captureText = document.getElementById('captureText');
const serverStatus = document.getElementById('serverStatus');
const lastCapture = document.getElementById('lastCapture');
const resultSection = document.getElementById('resultSection');
const resultContent = document.getElementById('resultContent');
const autoAnalyzeToggle = document.getElementById('autoAnalyzeToggle');
const notificationToggle = document.getElementById('notificationToggle');

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    await checkServerStatus();
    await loadLastResult();
    setupEventListeners();
});

// 加载设置
async function loadSettings() {
    try {
        const settings = await chrome.storage.sync.get({
            autoAnalyze: true,
            showNotifications: true
        });
        
        autoAnalyzeToggle.classList.toggle('active', settings.autoAnalyze);
        notificationToggle.classList.toggle('active', settings.showNotifications);
    } catch (error) {
        console.error('加载设置失败:', error);
    }
}

// 检查服务器状态
async function checkServerStatus() {
    try {
        const settings = await chrome.storage.sync.get({ serverUrl: 'http://localhost:8000' });
        
        const response = await fetch(`${settings.serverUrl}/api/v1/health`, {
            method: 'GET',
            timeout: 3000
        });
        
        if (response.ok) {
            serverStatus.textContent = '🟢 在线';
            serverStatus.style.background = 'rgba(34, 197, 94, 0.3)';
        } else {
            throw new Error('服务器响应异常');
        }
    } catch (error) {
        console.error('服务器检查失败:', error);
        serverStatus.textContent = '🔴 离线';
        serverStatus.style.background = 'rgba(239, 68, 68, 0.3)';
    }
}

// 加载最后的结果
async function loadLastResult() {
    try {
        const data = await chrome.storage.local.get([
            'lastScreenshot', 
            'lastAnalysis', 
            'lastAnalysisTime',
            'lastError'
        ]);
        
        if (data.lastAnalysisTime) {
            const time = new Date(data.lastAnalysisTime);
            lastCapture.textContent = formatTime(time);
            
            if (data.lastAnalysis) {
                showResult(data.lastAnalysis);
            } else if (data.lastError) {
                showError(data.lastError);
            }
        }
    } catch (error) {
        console.error('加载结果失败:', error);
    }
}

// 显示分析结果
function showResult(result) {
    if (result && result.data) {
        resultContent.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong>📝 分析内容：</strong><br>
                ${result.data.analysis || '无分析内容'}
            </div>
            ${result.data.answer ? `
                <div style="margin-bottom: 10px;">
                    <strong>💡 答案解析：</strong><br>
                    ${result.data.answer}
                </div>
            ` : ''}
            <div style="font-size: 11px; color: #666; text-align: center;">
                ⏱️ 分析耗时：${result.data.analysis_time}秒
            </div>
        `;
        resultSection.classList.add('show');
    }
}

// 显示错误信息
function showError(error) {
    resultContent.innerHTML = `
        <div style="color: #dc2626;">
            <strong>❌ 错误：</strong><br>
            ${error}
        </div>
    `;
    resultSection.classList.add('show');
}

// 格式化时间
function formatTime(date) {
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) { // 1分钟内
        return '刚刚';
    } else if (diff < 3600000) { // 1小时内
        return `${Math.floor(diff / 60000)}分钟前`;
    } else if (diff < 86400000) { // 24小时内
        return `${Math.floor(diff / 3600000)}小时前`;
    } else {
        return date.toLocaleDateString();
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 截屏按钮
    captureBtn.addEventListener('click', async () => {
        await captureScreen();
    });
    
    // 自动分析开关
    autoAnalyzeToggle.addEventListener('click', async () => {
        const isActive = autoAnalyzeToggle.classList.contains('active');
        autoAnalyzeToggle.classList.toggle('active', !isActive);
        
        await chrome.storage.sync.set({ autoAnalyze: !isActive });
    });
    
    // 通知开关
    notificationToggle.addEventListener('click', async () => {
        const isActive = notificationToggle.classList.contains('active');
        notificationToggle.classList.toggle('active', !isActive);
        
        await chrome.storage.sync.set({ showNotifications: !isActive });
    });
}

// 截屏功能
async function captureScreen() {
    try {
        // 更新按钮状态
        captureBtn.disabled = true;
        captureIcon.innerHTML = '<div class="loading"></div>';
        captureText.textContent = '截屏中...';
        
        // 发送截屏消息给背景脚本
        const response = await chrome.runtime.sendMessage({ type: 'CAPTURE_SCREEN' });
        
        if (response.success) {
            captureText.textContent = '截屏成功！';
            
            // 1秒后刷新结果
            setTimeout(async () => {
                await loadLastResult();
                await checkServerStatus();
            }, 1000);
        } else {
            throw new Error(response.error || '截屏失败');
        }
        
    } catch (error) {
        console.error('截屏失败:', error);
        captureText.textContent = '截屏失败';
        showError(error.message);
    } finally {
        // 恢复按钮状态
        setTimeout(() => {
            captureBtn.disabled = false;
            captureIcon.textContent = '📸';
            captureText.textContent = '开始截屏分析';
        }, 2000);
    }
}

// 监听存储变化
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'local') {
        if (changes.lastAnalysis || changes.lastError) {
            loadLastResult();
        }
    }
});

// 监听来自背景脚本的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'UPDATE_POPUP') {
        loadLastResult();
        checkServerStatus();
    }
});