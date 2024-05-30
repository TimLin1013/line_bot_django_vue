<template>
    <div class="container">
      <h2 class="text-center" style="margin-bottom: 20px;">創建群組</h2>
      <input type="text" v-model="groupName" class="form-control" placeholder="輸入群組名稱">
      <button @click="handleReserve" class="btn btn-primary">輸入</button>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        groupName: ''
      };
    },
    methods: {
      handleReserve() {
        if (this.groupName.trim() === '') {
          alert("請輸入群組名稱");
          return;
        }
        if (this.groupName.length > 200) {
          alert("群組名稱不能超過200個字符");
          return;
        }
        const msg = this.groupName;
        this.reserve(msg);
      },
      reserve(msg) {
        
      }
    }
  };
  </script>
  
  <style scoped>
  body {
    background-color: #F5F5DC;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
  }
  .container {
    background: white;
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    margin-top: -200px;
  }
  .form-control {
    margin-bottom: 15px;
    border-radius: 10px;
    padding: 10px;
    font-size: 16px;
    border: 1px solid #ced4da;
  }
  .btn {
    width: 100%;
    height: 40px;
    border-radius: 10px;
    font-size: 16px;
  }
  </style>
  