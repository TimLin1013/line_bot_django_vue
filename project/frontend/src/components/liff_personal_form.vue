<template>
  <div class="row" style="margin: 10px">
    <div class="col-12" style="margin: 10px">
      <label >User_ID</label>
      <input v-model="personal_id" type="text" class="form-control" />
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
      <select v-model="transaction" class="form-control" >
        <option value="expenditure">支出</option>
        <option value="income">收入</option>
      </select>
      <br />
      <label>類別</label>
      <select v-model="formData.category" class="form-control">
        <option v-for="category in this.tmp_list" :key="category" :value="category">
          {{ category.category_name }}
        </option>
      </select>
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
        personal_id: this.$root.$personal_id,
        currentTime: this.formatCurrentTime(),
        category_list: [],
        tmp_list:[],
        transaction:this.formData.transaction_type
      };
    },
    watch: {
      transaction(newValue) {
        console.log('Transaction type changed to:', newValue);
        if (newValue === 'expenditure') {
          console.log("ok")
          this.handleExpenditure();
        } else if (newValue === 'income') {
          this.handleIncome();
        }
    }
  },
    mounted(){
      this.catchcategory()
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
      //抓取使用者類別
      catchcategory(){
        const apiUrl = `${this.$apiUrl}/api/returncategory/`;
        this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id})
          .then(response => {
            console.log(response);
            
            this.category_list = response.data.category.map(category => ({category_name:category.category_name,transaction_type:category.transaction_type}));
          })
          .catch(error => {
            console.error(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      //暫存
      temporary() {
        
        const apiUrl = `${this.$apiUrl}/api/get_keep_temporary/`;
        console.log(apiUrl);
        if(this.formData.category==''){
            Swal.fire({
              title: "請選擇類別或支出!!",
              icon: "warning"
          });
          return;
        }
        this.$axios.post(apiUrl, { 
          userID :this.$root.$personal_id,
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
      //完成確定
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
       
        const apiUrl = `${this.$apiUrl}/api/get_keep_sure/`;
        console.log(apiUrl);
        this.$axios.post(apiUrl, { 
          userID :this.$root.$personal_id,
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
      },
      handleExpenditure() {
        
        
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type==="支出")

        
      },
      handleIncome() {
       
        
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type==="收入")
        
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