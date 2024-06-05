<template>
    <div class="row" style="margin: 10px">
      <div class="col-12" style="margin: 10px">
        <label >User_ID</label>
        <input v-model="datas" type="text" class="form-control" />
        <br />
        <label >項目</label>
        <input v-model="item" type="text" class="form-control" />
        <br />
        <label>金額</label>
        <input v-model="payment" type="number" class="form-control" />
        <br />
        <label>時間</label>
        <input v-model="currentTime" type="text" class="form-control" />
        <br />
        <label>地點</label>
        <input v-model="location" type="text" class="form-control" />
        <br />
        <label>交易類型</label>
        <input v-model="transaction_type" type="text" class="form-control" />
        <br />
        <label>類別</label>
        <input v-model="category" type="text" class="form-control" />
        <br />
        <button @click="temporary" class="btn btn-warning btn-block">暫存</button>
        <button @click="sure" class="btn btn-warning btn-block">完成確定</button>
      </div>
    </div>
  </template>
  <script>
  export default {
    props: {
        formData : Object
    },
    data() {
        return {
            currentTime:this.formatCurrentTime(),
            datas:this.$route.params.formData
        };
    },
    mounted(){
        const formData = this.$route.params.formData;
        console.log('Received formData:', formData); // 確認收到的 formData

    },
    methods: {
        formatCurrentTime() {
          const now = new Date();
          const year = now.getFullYear();
          const month = String(now.getMonth() + 1).padStart(2, '0');
          const day = String(now.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        },
        temporary() {
          this.currentTime = this.formatCurrentTime();
          const apiUrl = `${this.$apiUrl}/api/get_keep_temporary/`;
          console.log(apiUrl);
          this.$axios.post(apiUrl, { 
            userID :this.formData.personal_id,
            item:this.item,
            payment:this.payment,
            location:this.location,
            category:this.category,
            time:this.currentTime
          }).then(response => {
            console.log(response);
            alert('暫存成功');
            this.$router.push({ name: 'liff_search'});
          })
          .catch(error => {
            console.error(error);
          });
        },
        sure(){
          for (let key in this.formData) {
            if (!this.formData[key]) {
              alert("有空白無法完成確認，只能按暫存，謝謝!");
              return; 
            }
          }
          this.currentTime = this.formatCurrentTime();
          const apiUrl = `${this.$apiUrl}/api/get_keep_sure/`;
          console.log(apiUrl);
          this.$axios.post(apiUrl, { 
            userID :this.formData.perosnal_id,
            item:this.item,
            payment:this.payment,
            location:this.location,
            category:this.category,
            time:this.currentTime
          }).then(response => {
            console.log(response);
            alert('完成');
            this.$router.push({ name: 'liff_search'});
          })
          .catch(error => {
            console.error(error);
          });
        }
      },
      
  };
  </script>
    
  <style scoped>
  .form-control {
    font-size: 16px;
    color: black;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 0.25rem;
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .btn-warning {
    font-size: 16px;
    color: #0e0303;
    background-color: #ffc107;
    border-color: #ffc107;
    padding: 0.5rem;
    width: 100%;
    margin-bottom: 1rem;
  }
  
  .btn-warning:hover {
    color: #0e0303;
    background-color: #e0a800;
    border-color: #d39e00;
  }
  </style>