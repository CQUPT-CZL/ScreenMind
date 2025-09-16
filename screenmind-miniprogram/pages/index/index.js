// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    isLoggedIn: false,
    isConnected: false,
    deviceId: '',
    serverUrl: 'http://localhost:8000',
    loading: false,
    testLoading: false,
    latestNotification: null
  },

  onLoad() {
    this.initPage()
  },

  onShow() {
    this.checkConnectionStatus()
    this.loadLatestNotification()
  },

  // 初始化页面
  initPage() {
    const userInfo = wx.getStorageSync('userInfo')
    const deviceId = wx.getStorageSync('deviceId') || app.globalData.deviceId
    
    this.setData({
      userInfo,
      isLoggedIn: !!userInfo,
      deviceId,
      serverUrl: app.globalData.serverUrl
    })
  },

  // 检查连接状态
  async checkConnectionStatus() {
    if (!this.data.isLoggedIn) {
      this.setData({ isConnected: false })
      return
    }

    try {
      const res = await app.request({
        url: '/api/v1/miniprogram/status',
        method: 'GET',
        data: { deviceId: this.data.deviceId }
      })
      
      this.setData({
        isConnected: res.data.connected || false
      })
    } catch (error) {
      console.error('检查连接状态失败:', error)
      this.setData({ isConnected: false })
    }
  },

  // 加载最新通知
  async loadLatestNotification() {
    if (!this.data.isLoggedIn) return

    try {
      const res = await app.request({
        url: '/api/v1/miniprogram/notifications/latest',
        method: 'GET',
        data: { deviceId: this.data.deviceId }
      })
      
      if (res.data.notification) {
        this.setData({
          latestNotification: {
            ...res.data.notification,
            time: this.formatTime(res.data.notification.created_at)
          }
        })
      }
    } catch (error) {
      console.error('加载最新通知失败:', error)
    }
  },

  // 处理绑定设备
  async handleBind() {
    if (this.data.loading) return

    this.setData({ loading: true })

    try {
      // 微信登录
      const loginRes = await wx.login()
      if (!loginRes.code) {
        throw new Error('微信登录失败')
      }

      // 获取用户信息
      const userProfile = await wx.getUserProfile({
        desc: '用于设备绑定和消息推送'
      })

      // 发送到后端进行绑定
      const bindRes = await app.request({
        url: '/api/v1/miniprogram/bind',
        method: 'POST',
        data: {
          code: loginRes.code,
          deviceId: this.data.deviceId,
          userInfo: userProfile.userInfo
        }
      })

      if (bindRes.data.success) {
        // 保存用户信息
        wx.setStorageSync('userInfo', userProfile.userInfo)
        wx.setStorageSync('openid', bindRes.data.openid)
        
        this.setData({
          userInfo: userProfile.userInfo,
          isLoggedIn: true,
          isConnected: true
        })

        wx.showToast({
          title: '绑定成功！',
          icon: 'success'
        })
      } else {
        throw new Error(bindRes.data.message || '绑定失败')
      }
    } catch (error) {
      console.error('绑定失败:', error)
      wx.showToast({
        title: error.message || '绑定失败',
        icon: 'error'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 处理解除绑定
  async handleUnbind() {
    const result = await wx.showModal({
      title: '确认解绑',
      content: '解绑后将无法接收通知消息，确定要解绑吗？'
    })

    if (!result.confirm) return

    this.setData({ loading: true })

    try {
      await app.request({
        url: '/api/v1/miniprogram/unbind',
        method: 'POST',
        data: {
          deviceId: this.data.deviceId,
          openid: wx.getStorageSync('openid')
        }
      })

      // 清除本地数据
      wx.removeStorageSync('userInfo')
      wx.removeStorageSync('openid')

      this.setData({
        userInfo: null,
        isLoggedIn: false,
        isConnected: false,
        latestNotification: null
      })

      wx.showToast({
        title: '解绑成功',
        icon: 'success'
      })
    } catch (error) {
      console.error('解绑失败:', error)
      wx.showToast({
        title: '解绑失败',
        icon: 'error'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 测试通知
  async handleTestNotification() {
    if (this.data.testLoading) return

    this.setData({ testLoading: true })

    try {
      await app.request({
        url: '/api/v1/miniprogram/test-notification',
        method: 'POST',
        data: {
          deviceId: this.data.deviceId,
          openid: wx.getStorageSync('openid')
        }
      })

      wx.showToast({
        title: '测试通知已发送',
        icon: 'success'
      })

      // 延迟刷新最新通知
      setTimeout(() => {
        this.loadLatestNotification()
      }, 2000)
    } catch (error) {
      console.error('发送测试通知失败:', error)
      wx.showToast({
        title: '发送失败',
        icon: 'error'
      })
    } finally {
      this.setData({ testLoading: false })
    }
  },

  // 查看历史记录
  handleViewHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    })
  },

  // 查看详情
  handleViewDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  },

  // 格式化时间
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) { // 1分钟内
      return '刚刚'
    } else if (diff < 3600000) { // 1小时内
      return `${Math.floor(diff / 60000)}分钟前`
    } else if (diff < 86400000) { // 24小时内
      return `${Math.floor(diff / 3600000)}小时前`
    } else {
      return `${date.getMonth() + 1}月${date.getDate()}日`
    }
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await Promise.all([
      this.checkConnectionStatus(),
      this.loadLatestNotification()
    ])
    wx.stopPullDownRefresh()
  }
})