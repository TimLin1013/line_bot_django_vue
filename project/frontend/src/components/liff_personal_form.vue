<template>
    <div class="row" style="margin: 10px">
      <div class="col-12" style="margin: 10px">
        <label>User_ID</label>
        <input type="text" v-model="userId" class="form-control" readonly />
        <br />
        <label>項目</label>
        <input type="text" v-model="formData.item" class="form-control" />
        <br />
        <label>金額</label>
        <input type="number" v-model="formData.payment" class="form-control" />
        <br />
        <label>時間</label>
        <input type="text" v-model="formData.datetime" class="form-control"  />
        <br />
        <label>地點</label>
        <input type="text" v-model="formData.location" class="form-control" />
        <br />
        <label>交易類型</label>
        <input type="text" v-model="formData.transaction_type" class="form-control" />
        <br />
        <label>類別</label>
        <input type="text" v-model="formData.category" class="form-control" />
        <br />
        <button class="btn btn-warning btn-block" @click="temporarySave">暫存</button>
        <button class="btn btn-warning btn-block" @click="confirm">完成確定</button>
      </div>
    </div>
  </template>
  
  <script>

  
  export default {
    props: {
       //formData : Object
    },
    data() {
      return {
        userId : this.$root.$userId,
            formData: {
            item: '',
            payment: '',
            datetime: '',
            location: '',
            transaction_type: '',
            category: ''
        }
      };
    },
    methods: {
      temporarySave() {
        // Add your temporary save logic here
        console.log('Temporary Save:', this.formData);
      },
      confirm() {
        // Add your confirm logic here
        console.log('Confirm:', this.formData);
      }
    },
    mounted() {
      
        
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
  