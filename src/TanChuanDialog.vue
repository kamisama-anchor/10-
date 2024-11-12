<template>
  <div>
    <!-- 这里没有按钮，所有的通知通过状态变化自动触发 -->
  </div>
</template>

<script>
export default {
  data() {
    return {
      isAttacked: false,           // 是否收到攻击
      defendedSuccessfully: false, // 是否防御成功
    };
  },
  methods: {
    // 模拟收到攻击（后台收到攻击时触发）
    simulateAttack() {
      // 设置收到攻击状态
      this.isAttacked = true;
      this.defendedSuccessfully = false;  // 防御状态设为false

      // 显示警告通知
      this.showWarningNotification();
    },

    // 模拟防御成功（防御成功时触发）
    simulateDefense() {
      // 设置防御成功状态
      this.isAttacked = false;
      this.defendedSuccessfully = true;

      // 显示成功通知
      this.showSuccessNotification();
    },

    // 显示警告通知
    showWarningNotification() {
      this.$notify({
        title: '警告',
        message: '系统受到DDoS攻击',
        type: 'warning'
      });
    },

    // 显示成功通知
    showSuccessNotification() {
      this.$notify({
        title: '成功',
        message: '成功防御了此次攻击',
        type: 'success'
      });
    }
  },

  watch: {
    // 监听是否收到攻击
    isAttacked(newValue) {
      if (newValue) {
        // 如果收到攻击，显示警告通知
        this.showWarningNotification();
      }
    },

    // 监听防御成功
    defendedSuccessfully(newValue) {
      if (newValue) {
        // 如果防御成功，显示成功通知
        this.showSuccessNotification();
      }
    }
  },

  mounted() {
    // 模拟收到攻击事件，2秒后模拟防御成功
    setTimeout(() => {
      this.simulateAttack(); // 模拟收到攻击
    }, 1000); // 1秒后开始攻击

    setTimeout(() => {
      this.simulateDefense(); // 模拟防御成功
    }, 5000); // 5秒后防御成功
  }
}
</script>

<style scoped>
/* 可选：样式部分 */
</style>
