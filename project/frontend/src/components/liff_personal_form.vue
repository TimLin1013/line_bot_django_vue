<template>
  <div class="row" style="margin: 10px">
    <div class="col-12" style="margin: 10px">
      <label >User_ID</label>
      <input v-model="formData.user_id" type="text" class="form-control" />
      <br />
      <label >項目</label>
      <input v-model="formData.item" type="text" class="form-control" />
      <br />
      <label>金額</label>
      <input v-model="formData.payment" type="number" class="form-control" />
      <br />
      <label>時間</label>
      <input v-model="currentTime" type="text" class="form-control" />
      <br />
      <label>地點</label>
      <input v-model="formData.location" type="text" class="form-control" />
      <br />
      <label>交易類型</label>
      <input v-model="formData.transaction_type" type="text" class="form-control" />
      <br />
      <label>類別</label>
      <input v-model="formData.category" type="text" class="form-control" />
      <br />
      <button @click="temporary" class="btn btn-warning btn-block">暫存</button>
      <button @click="sure" class="btn btn-warning btn-block">完成確定</button>
    </div>
  </div>
</template>
<script>
import Swal from 'sweetalert2';
export default {
    props: {
      formData : Object
    },
    data() {
      return {
        currentTime: this.formatCurrentTime(),
      };
    },
    methods: {
      formatCurrentTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        //const hours = String(now.getHours()).padStart(2, '0');
        //const minutes = String(now.getMinutes()).padStart(2, '0');
        //const seconds = String(now.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      },
      temporary() {
        this.currentTime = this.formatCurrentTime();
        const apiUrl = `${this.$apiUrl}/api/get_keep_temporary/`;
        console.log(apiUrl);
        this.$axios.post(apiUrl, { 
          userID :this.formData.user_id,
          item:this.formData.item,
          payment:this.formData.payment,
          location:this.formData.location,
          category:this.formData.category,
          time:this.currentTime
        }).then(response => {
          console.log(response);
          Swal.fire({
              title: "暫存成功!!",
              icon: "success"
          });
          this.$router.push({ name: 'liff_search'});
        })
        .catch(error => {
          console.error(error);
        });
      },
      sure(){
        for (let key in this.formData) {
          if (!this.formData[key]) {
            Swal.fire({
              title: "有空白無法完成確認，只能按暫存!",
              icon: "warning"
            });
            return;
          }
        }
        this.currentTime = this.formatCurrentTime();
        const apiUrl = `${this.$apiUrl}/api/get_keep_sure/`;
        console.log(apiUrl);
        this.$axios.post(apiUrl, { 
          userID :this.formData.user_id,
          item:this.formData.item,
          payment:this.formData.payment,
          location:this.formData.location,
          category:this.formData.category,
          time:this.currentTime
        }).then(response => {
          console.log(response);
          Swal.fire({
              title: "完成記帳!!",
              icon: "success"
          });
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