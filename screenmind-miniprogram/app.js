// app.js
App({
  globalData: {
    userInfo: null,
    deviceId: null,
    serverUrl: 'http://localhost:8000', // 开发环境，生产环境需要修改
    isLoggedIn: false
  },

  onLaunch() {
    console.log('🚀 ScreenMind小程序启动')
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 生成或获取设备ID
    this.initDeviceId()
    
    // 检查更新
    this.checkForUpdate()
  },

  onShow() {
    console.log('📱 小程序显示')
  },

  onHide() {
    console.log('📱 小程序隐藏')
  },

  onError(msg) {
    console.error('❌ 小程序错误:', msg)
  },

  // 检查登录状态
  checkLoginStatus() {
    const userInfo = wx.getStorageSync('userInfo')
    const deviceId = wx.getStorageSync('deviceId')
    
    if (userInfo && deviceId) {
      this.globalData.userInfo = userInfo
      this.globalData.deviceId = deviceId
      this.globalData.isLoggedIn = true
      console.log('✅ 用户已登录:', userInfo.nickName)
    } else {
      console.log('❌ 用户未登录')
    }
  },

  // 初始化设备ID
  initDeviceId() {
    let deviceId = wx.getStorageSync('deviceId')
    
    if (!deviceId) {
      // 生成唯一设备ID
      deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      wx.setStorageSync('deviceId', deviceId)
      console.log('🆔 生成新设备ID:', deviceId)
    } else {
      console.log('🆔 使用现有设备ID:', deviceId)
    }
    
    this.globalData.deviceId = deviceId
  },

  // 检查小程序更新
  checkForUpdate() {
    if (wx.canIUse('getUpdateManager')) {
      const updateManager = wx.getUpdateManager()
      
      updateManager.onCheckForUpdate((res) => {
        if (res.hasUpdate) {
          console.log('📦 发现新版本')
        }
      })
      
      updateManager.onUpdateReady(() => {
        wx.showModal({
          title: '更新提示',
          content: '新版本已经准备好，是否重启应用？',
          success: (res) => {
            if (res.confirm) {
              updateManager.applyUpdate()
            }
          }
        })
      })
      
      updateManager.onUpdateFailed(() => {
        console.error('❌ 新版本下载失败')
      })
    }
  },

  // 用户登录
  login(userInfo) {
    this.globalData.userInfo = userInfo
    this.globalData.isLoggedIn = true
    
    // 保存到本地存储
    wx.setStorageSync('userInfo', userInfo)
    
    console.log('✅ 用户登录成功:', userInfo.nickName)
    
    // 绑定设备到后端
    this.bindDeviceToServer(userInfo)
  },

  // 绑定设备到服务器
  async bindDeviceToServer(userInfo) {
    try {
      const res = await this.request({
        url: '/api/v1/miniprogram/bind',
        method: 'POST',
        data: {
          deviceId: this.globalData.deviceId,
          userInfo: {
            nickName: userInfo.nickName,
            avatarUrl: userInfo.avatarUrl,
            openId: userInfo.openId || ''
          }
        }
      })
      
      if (res.success) {
        console.log('✅ 设备绑定成功')
        wx.showToast({
          title: '绑定成功',
          icon: 'success'
        })
      }
    } catch (error) {
      console.error('❌ 设备绑定失败:', error)
      wx.showToast({
        title: '绑定失败',
        icon: 'error'
      })
    }
  },

  // 封装请求方法
  request(options) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: this.globalData.serverUrl + options.url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'Content-Type': 'application/json',
          'Device-Id': this.globalData.deviceId,
          ...options.header
        },
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else {
            reject(new Error(`请求失败: ${res.statusCode}`))
          }
        },
        fail: (error) => {
          reject(error)
        }
      })
    })
  },

  // 用户退出登录
  logout() {
    this.globalData.userInfo = null
    this.globalData.isLoggedIn = false
    
    // 清除本地存储
    wx.removeStorageSync('userInfo')
    
    console.log('👋 用户退出登录')
    
    wx.showToast({
      title: '已退出登录',
      icon: 'success'
    })
  }
})