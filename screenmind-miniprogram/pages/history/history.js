// pages/history/history.js
const app = getApp()

Page({
  data: {
    historyList: [],
    currentFilter: 'all',
    loading: false,
    hasMore: true,
    page: 1,
    pageSize: 20,
    totalCount: 0,
    todayCount: 0,
    weekCount: 0
  },

  onLoad() {
    this.loadStatistics()
    this.loadHistoryList()
  },

  // 加载统计数据
  async loadStatistics() {
    try {
      const deviceId = wx.getStorageSync('deviceId') || app.globalData.deviceId
      const res = await app.request({
        url: '/api/v1/miniprogram/statistics',
        method: 'GET',
        data: { deviceId }
      })

      this.setData({
        totalCount: res.data.total || 0,
        todayCount: res.data.today || 0,
        weekCount: res.data.week || 0
      })
    } catch (error) {
      console.error('加载统计数据失败:', error)
    }
  },

  // 加载历史记录列表
  async loadHistoryList(reset = false) {
    if (this.data.loading) return

    this.setData({ loading: true })

    try {
      const deviceId = wx.getStorageSync('deviceId') || app.globalData.deviceId
      const page = reset ? 1 : this.data.page
      
      const res = await app.request({
        url: '/api/v1/miniprogram/history',
        method: 'GET',
        data: {
          deviceId,
          page,
          pageSize: this.data.pageSize,
          filter: this.data.currentFilter
        }
      })

      const newList = res.data.list.map(item => ({
        ...item,
        typeText: this.getTypeText(item.type),
        timeText: this.formatTime(item.created_at),
        confidence: item.confidence ? Math.round(item.confidence * 100) : null
      }))

      this.setData({
        historyList: reset ? newList : [...this.data.historyList, ...newList],
        hasMore: res.data.hasMore,
        page: page + 1
      })
    } catch (error) {
      console.error('加载历史记录失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    } finally {
      this.setData({ loading: false })
    }
  },

  // 处理筛选器变化
  handleFilterChange(e) {
    const filter = e.currentTarget.dataset.filter
    if (filter === this.data.currentFilter) return

    this.setData({
      currentFilter: filter,
      page: 1,
      hasMore: true
    })

    this.loadHistoryList(true)
  },

  // 处理项目点击
  handleItemClick(e) {
    const item = e.currentTarget.dataset.item
    wx.navigateTo({
      url: `/pages/detail/detail?id=${item.id}`
    })
  },

  // 处理分享
  handleShare(e) {
    const item = e.currentTarget.dataset.item
    
    wx.showActionSheet({
      itemList: ['复制答案', '分享给朋友'],
      success: (res) => {
        if (res.tapIndex === 0) {
          // 复制答案
          wx.setClipboardData({
            data: `题目: ${item.question}\n答案: ${item.answer}`,
            success: () => {
              wx.showToast({
                title: '已复制到剪贴板',
                icon: 'success'
              })
            }
          })
        } else if (res.tapIndex === 1) {
          // 分享给朋友
          this.shareToFriend(item)
        }
      }
    })
  },

  // 分享给朋友
  shareToFriend(item) {
    // 这里可以实现分享逻辑
    wx.showToast({
      title: '分享功能开发中',
      icon: 'none'
    })
  },

  // 加载更多
  handleLoadMore() {
    this.loadHistoryList()
  },

  // 获取类型文本
  getTypeText(type) {
    const typeMap = {
      'math': '数学题',
      'text': '文本题',
      'image': '图像题',
      'code': '代码题',
      'other': '其他'
    }
    return typeMap[type] || '未知'
  },

  // 格式化时间
  formatTime(timestamp) {
    const date = new Date(timestamp)
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
    const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)

    if (date >= today) {
      // 今天
      return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    } else if (date >= yesterday) {
      // 昨天
      return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    } else {
      // 更早
      return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
    }
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await Promise.all([
      this.loadStatistics(),
      this.loadHistoryList(true)
    ])
    wx.stopPullDownRefresh()
  },

  // 触底加载更多
  onReachBottom() {
    if (this.data.hasMore && !this.data.loading) {
      this.handleLoadMore()
    }
  }
})