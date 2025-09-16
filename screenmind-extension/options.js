// ScreenMind 扩展设置页面脚本
console.log('⚙️ ScreenMind 设置页面已加载');

// DOM 元素
const serverUrlInput = document.getElementById('serverUrl');
const serverStatus = document.getElementById('serverStatus');
const autoAnalyzeToggle = document.getElementById('autoAnalyzeToggle');
const notificationToggle = document.getElementById('notificationToggle');
const saveHistoryToggle = document.getElementById('saveHistoryToggle');
const analysisTimeoutInput = document.getElementById('analysisTimeout');
const maxHistoryItemsInput = document.getElementById('maxHistoryItems');
const saveBtn = document.getElementById('saveBtn');
const resetBtn = document.getElementById('resetBtn');
const successMessage = document.getElementById('successMessage');
const errorMessage = document.getElementById('errorMessage');

// 默认设置
const defaultSettings = {
    serverUrl: 'http://localhost:8000',
    autoAnalyze: true,
    showNotifications: true,
    saveHistory: true,
    analysisTimeout: 30,
    maxHistoryItems: 100
};

// 初始化
document.addEventListener('DOMContentLoaded', async () => {
    await loadSettings();
    await checkServerStatus();
    setupEventListeners();
});

// 加载设置
async function loadSettings() {
    try {
        const settings = await chrome.storage.sync.get(defaultSettings);
        
        serverUrlInput.value = settings.serverUrl;
        analysisTimeoutInput.value = settings.analysisTimeout;
        maxHistoryItemsInput.value = settings.maxHistoryItems;
        
        updateToggle(autoAnalyzeToggle, settings.autoAnalyze);
        updateToggle(notificationToggle, settings.showNotifications);
        updateToggle(saveHistoryToggle, settings.saveHistory);
        
        console.log('✅ 设置加载完成:', settings);
    } catch (error) {
        console.error('❌ 加载设置失败:', error);
        showError('加载设置失败: ' + error.message);
    }
}

// 保存设置
async function saveSettings() {
    try {
        const settings = {
            serverUrl: serverUrlInput.value.trim() || defaultSettings.serverUrl,
            autoAnalyze: autoAnalyzeToggle.classList.contains('active'),
            showNotifications: notificationToggle.classList.contains('active'),
            saveHistory: saveHistoryToggle.classList.contains('active'),
            analysisTimeout: parseInt(analysisTimeoutInput.value) || defaultSettings.analysisTimeout,
            maxHistoryItems: parseInt(maxHistoryItemsInput.value) || defaultSettings.maxHistoryItems
        };
        
        // 验证设置
        if (!isValidUrl(settings.serverUrl)) {
            throw new Error('请输入有效的服务器地址');
        }
        
        if (settings.analysisTimeout < 10 || settings.analysisTimeout > 120) {
            throw new Error('分析超时时间必须在10-120秒之间');
        }
        
        if (settings.maxHistoryItems < 10 || settings.maxHistoryItems > 1000) {
            throw new Error('最大历史记录数必须在10-1000之间');
        }
        
        await chrome.storage.sync.set(settings);
        
        console.log('✅ 设置保存成功:', settings);
        showSuccess('设置已保存成功！');
        
        // 重新检查服务器状态
        setTimeout(checkServerStatus, 500);
        
    } catch (error) {
        console.error('❌ 保存设置失败:', error);
        showError('保存设置失败: ' + error.message);
    }
}

// 重置设置
async function resetSettings() {
    try {
        await chrome.storage.sync.set(defaultSettings);
        await loadSettings();
        
        console.log('✅ 设置已重置为默认值');
        showSuccess('设置已重置为默认值！');
        
        setTimeout(checkServerStatus, 500);
        
    } catch (error) {
        console.error('❌ 重置设置失败:', error);
        showError('重置设置失败: ' + error.message);
    }
}

// 检查服务器状态
async function checkServerStatus() {
    try {
        const serverUrl = serverUrlInput.value.trim() || defaultSettings.serverUrl;
        
        serverStatus.textContent = '🔄 检查中...';
        serverStatus.className = 'status-indicator';
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);
        
        const response = await fetch(`${serverUrl}/api/v1/health`, {
            method: 'GET',
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
            serverStatus.textContent = '🟢 在线';
            serverStatus.className = 'status-indicator status-online';
        } else {
            throw new Error(`服务器响应错误: ${response.status}`);
        }
        
    } catch (error) {
        console.error('服务器检查失败:', error);
        
        if (error.name === 'AbortError') {
            serverStatus.textContent = '🟡 超时';
        } else {
            serverStatus.textContent = '🔴 离线';
        }
        serverStatus.className = 'status-indicator status-offline';
    }
}

// 更新开关状态
function updateToggle(toggle, active) {
    toggle.classList.toggle('active', active);
}

// 设置事件监听器
function setupEventListeners() {
    // 保存按钮
    saveBtn.addEventListener('click', saveSettings);
    
    // 重置按钮
    resetBtn.addEventListener('click', () => {
        if (confirm('确定要重置所有设置为默认值吗？')) {
            resetSettings();
        }
    });
    
    // 开关切换
    [autoAnalyzeToggle, notificationToggle, saveHistoryToggle].forEach(toggle => {
        toggle.addEventListener('click', () => {
            toggle.classList.toggle('active');
        });
    });
    
    // 服务器地址变化时检查状态
    let checkTimeout;
    serverUrlInput.addEventListener('input', () => {
        clearTimeout(checkTimeout);
        checkTimeout = setTimeout(checkServerStatus, 1000);
    });
    
    // 键盘快捷键
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 's') {
            e.preventDefault();
            saveSettings();
        }
    });
}

// 显示成功消息
function showSuccess(message) {
    successMessage.textContent = message;
    successMessage.style.display = 'block';
    errorMessage.style.display = 'none';
    
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 3000);
}

// 显示错误消息
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    successMessage.style.display = 'none';
    
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// 验证URL格式
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

// 监听存储变化
chrome.storage.onChanged.addListener((changes, namespace) => {
    if (namespace === 'sync') {
        console.log('设置已更新:', changes);
    }
});