<template>
  <div class="container" style="margin-top: 20vh;">
    <div class="btn-group">
      <input type="radio" id="income" name="type" value="收入" v-model="type" checked>
      <label for="income">收入</label>
  
      <input type="radio" id="expense" name="type" value="支出" v-model="type">
      <label for="expense">支出</label>
    </div>
    <input type="text" v-model="input" class="form-control" placeholder="輸入一段話" style="margin-bottom: 10px; width: 93%; height: 40px; border-radius: 10px; padding: 10px; font-size: 16px; border: 1px solid #ced4da;">
    <button @click="handleReserve" class="btn btn-primary" style="width: 98.5%; height: 40px; border-radius: 10px; font-size: 16px;">
      輸入
    </button>
    <div id="result" style="margin-top: 10px;" v-html="result"></div> 
    <div id="loading" v-if="loading">載入中...</div>
  </div>
</template>

<script>
export default {
  
  data() {
    return {
      type: '收入',
      input: '',
      loading: false,
      result: ''
    };
  },
  methods: {
    handleReserve() {
      const apiUrl = `${this.$apiUrl}/test`;
      this.$axios.post(apiUrl, { 
        user_input : this.input,

       }).then(response => {
          console.log(response);
          this.$router.push({ name: 'liff_personal_form'});//,params: {formData: response.data.formData}
        })
        .catch(error => {
          console.error(error);
        });
    }
  }
};
</script>
  
  <style scoped>
  body {
    background-color: #fff;
  }
  .btn-group {
    display: flex;
  }
  .btn-group label {
    flex: 1;
    margin: 5px;
    padding: 10px;
    border: 1px solid #ced4da;
    border-radius: 5px;
    text-align: center;
    cursor: pointer;
    background-color: #fff;
    transition: background-color 0.3s;
  }
  .btn-group input[type="radio"] {
    display: none;
  }
  .btn-group input[type="radio"]:checked + label {
    background-color: #007bff;
    color: #fff;
    border-color: #007bff;
  }
  </style>
  