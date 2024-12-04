Page({
  data: {
    phone: '',
    verifyCode: '',
    countdown: 0
  },

  // 输入手机号
  inputPhone(e) {
    this.setData({
      phone: e.detail.value
    })
  },

  // 输入验证码
  inputCode(e) {
    this.setData({
      verifyCode: e.detail.value
    })
  },

  // 获取验证码
  async getVerifyCode() {
    if (!/^1\d{10}$/.test(this.data.phone)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    try {
      const res = await wx.request({
        url: 'http://your_api_domain/api/send_code',
        method: 'POST',
        data: {
          phone: this.data.phone
        }
      })
      
      // 开始倒计时
      this.startCountdown()
    } catch (err) {
      wx.showToast({
        title: '发送失败，请重试',
        icon: 'none'
      })
    }
  },

  // 登录
  async login() {
    try {
      const res = await wx.request({
        url: 'http://your_api_domain/api/login',
        method: 'POST',
        data: {
          phone: this.data.phone,
          code: this.data.verifyCode
        }
      })

      if (res.data.token) {
        wx.setStorageSync('token', res.data.token)
        wx.redirectTo({
          url: '/pages/reports/reports'
        })
      }
    } catch (err) {
      wx.showToast({
        title: '登录失败，请重试',
        icon: 'none'
      })
    }
  }
}) 