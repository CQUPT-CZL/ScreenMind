// pages/detail/detail.js
const app = getApp()

Page({
  data: {
    detail: null,
    loading: true,
    recordId: ''
  },

  onLoad(options) {
    const id = options.id
    if (id) {
      this.setData({ recordId: id })
      this.loadDetail(id)
    } else {
      wx.showToast({
        title: '参数错误',
        icon: 'error'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  // 加载详情数据
  async loadDetail(id) {
    this.setData({ loading: true })

    try {
      const deviceId = wx.getStorageSync('deviceId') || app.globalData.deviceId
      const res = await app.request({
        url: '/api/v1/miniprogram/detail',
        method: 'GET',
        data: { id, deviceId }
      })

      const detail = res.data.detail
      if (detail) {
        this.setData({
          detail: {
            ...detail,
            typeText: this.getTypeText(detail.type),
            timeText: this.formatTime(detail.created_at),
            confidence: detail.confidence ? Math.round(detail.confidence * 100) : null,
            steps: detail.steps ? JSON.parse(detail.steps) : [],
            knowledge: detail.knowledge ? JSON.parse(detail.knowledge) : []
          }
        })
      } else {
        throw new Error('记录不存在')
      }
    } catch (error) {
      console.error('加载详情失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } finally {
      this.setData({ loading: false })
    }
  },

  // 预览图片
  handlePreviewImage() {
    if (this.data.detail && this.data.detail.imageUrl) {
      wx.previewImage({
        urls: [this.data.detail.imageUrl],
        current: this.data.detail.imageUrl
      })
    }
  },

  // 复制题目
  handleCopyQuestion() {
    if (this.data.detail && this.data.detail.question) {
      wx.setClipboardData({
        data: this.data.detail.question,
        success: () => {
          wx.showToast({
            title: '题目已复制',
            icon: 'success'
          })
        }
      })
    }
  },

  // 复制答案
  handleCopyAnswer() {
    if (this.data.detail && this.data.detail.answer) {
      wx.setClipboardData({
        data: this.data.detail.answer,
        success: () => {
          wx.showToast({
            title: '答案已复制',
            icon: 'success'
          })
        }
      })
    }
  },

  // 分享完整内容
  handleShareAll() {
    const detail = this.data.detail
    if (!detail) return

    let shareContent = `📚 ScreenMind分析结果\n\n`
    shareContent += `🤔 题目:\n${detail.question}\n\n`
    shareContent += `✅ 答案:\n${detail.answer}\n\n`
    
    if (detail.steps && detail.steps.length > 0) {
      shareContent += `📝 解题步骤:\n`
      detail.steps.forEach((step, index) => {
        shareContent += `${index + 1}. ${step}\n`
      })
      shareContent += `\n`
    }

    if (detail.knowledge && detail.knowledge.length > 0) {
      shareContent += `💡 相关知识点: ${detail.knowledge.join(', ')}\n\n`
    }

    shareContent += `⏰ 分析时间: ${detail.timeText}`
    if (detail.confidence) {
      shareContent += `\n🎯 置信度: ${detail.confidence}%`
    }

    wx.setClipboardData({
      data: shareContent,
      success: () => {
        wx.showToast({
          title: '内容已复制到剪贴板',
          icon: 'success'
        })
      }
    })
  },

  // 保存图片
  async handleSaveImage() {
    if (!this.data.detail || !this.data.detail.imageUrl) return

    try {
      // 下载图片
      const downloadRes = await wx.downloadFile({
        url: this.data.detail.imageUrl
      })

      if (downloadRes.statusCode === 200) {
        // 保存到相册
        await wx.saveImageToPhotosAlbum({
          filePath: downloadRes.tempFilePath
        })

        wx.showToast({
          title: '图片已保存',
          icon: 'success'
        })
      } else {
        throw new Error('下载失败')
      }
    } catch (error) {
      console.error('保存图片失败:', error)
      
      if (error.errMsg && error.errMsg.includes('auth')) {
        wx.showModal({
          title: '需要授权',
          content: '保存图片需要访问您的相册权限，请在设置中开启',
          showCancel: false
        })
      } else {
        wx.showToast({
          title: '保存失败',
          icon: 'error'
        })
      }
    }
  },

  // 重新分析
  async handleReAnalyze() {
    const result = await wx.showModal({
      title: '重新分析',
      content: '确定要重新分析这个题目吗？这可能需要一些时间。'
    })

    if (!result.confirm) return

    try {
      wx.showLoading({
        title: '分析中...',
        mask: true
      })

      const deviceId = wx.getStorageSync('deviceId') || app.globalData.deviceId
      await app.request({
        url: '/api/v1/miniprogram/reanalyze',
        method: 'POST',
        data: {
          id: this.data.recordId,
          deviceId
        }
      })

      wx.hideLoading()
      wx.showToast({
        title: '重新分析完成',
        icon: 'success'
      })

      // 重新加载详情
      setTimeout(() => {
        this.loadDetail(this.data.recordId)
      }, 1000)
    } catch (error) {
      wx.hideLoading()
      console.error('重新分析失败:', error)
      wx.showToast({
        title: '分析失败',
        icon: 'error'
      })
    }
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
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  },

  // 分享给朋友
  onShareAppMessage() {
    const detail = this.data.detail
    if (!detail) return {}

    return {
      title: `ScreenMind分析结果: ${detail.question.substring(0, 20)}...`,
      path: `/pages/detail/detail?id=${this.data.recordId}`,
      imageUrl: detail.imageUrl || ''
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    const detail = this.data.detail
    if (!detail) return {}

    return {
      title: `ScreenMind帮我解决了这个问题: ${detail.question.substring(0, 30)}...`,
      imageUrl: detail.imageUrl || ''
    }
  }
})