<template>
    <div class="row" style="margin: 10px">
        <label>群組id</label>
        <input v-model="formData.group_id" readonly type="text" class="form-control" />
        <label >付款人</label>
        <select v-model="person" class="form-control" >
          <option v-for="personItem in persons" :key="personItem" :value="personItem">
            {{ personItem.personal_name}}
          </option>
        </select>
        <label >項目</label>
        <input v-model="formData.item" type="text" class="form-control" />
        <label>金額</label>
        <input v-model="formData.payment" type="number" class="form-control" />
        <label>時間</label>
        <input v-model="currentTime" type="text" class="form-control" />
        <label>地點</label>
        <input v-model="formData.location" type="text" class="form-control" />
        <label>分帳人</label>
        <select v-model="person2" class="form-control" >
          <option v-for="personItem in persons2" :key="personItem.personal_id" :value="personItem.personal_id">
            {{ personItem.personal_name }}
          </option>
        </select>
        <label>交易類型</label>
        <select v-model="transaction" class="form-control" >
          <option value="expenditure">支出</option>
          <option value="income">收入</option>
        </select>
        <label>類別</label>
        <select v-model="category_temp" class="form-control">
          <option v-for="category in this.tmp_list" :key="category" :value="category">
            {{ category.category_name }}
          </option>
        </select>
        <button @click="temporary" class="btn btn-warning btn-block">暫存</button>
        <button @click="sure" class="btn btn-warning btn-block">完成確定</button>
    </div>
  </template>
<script>
import Swal from 'sweetalert2';
export default {
    props: {
      formData : Object
    },
    data(){
      return{
        currentTime: this.formatCurrentTime(),
        category_list: [],
        tmp_list:[],
        person:null,
        person2:null,
        persons: [],
        persons2:[],
        transaction:'',
        category_temp:'',
      }
    },
    mounted(){
      this.catchcategory()
      this.catchperson()
    },
    watch: {
        transaction(newValue) {
          if (newValue === 'expenditure') {
            this.handleExpenditure();
          } else if (newValue === 'income') {
            this.handleIncome();
          }
        }
    },
    methods:{
      formatCurrentTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      },
      //抓類別
      catchcategory(){
        const apiUrl = `${this.$apiUrl}/api/return_group_category/`;
        this.$axios.post(apiUrl, { group_id: this.formData.group_id})
          .then(response => {
            this.category_list = response.data.category.map(category => ({category_name:category.category_name,transaction_type:category.transaction_type}));
          })
          .catch(error => {
            console.error(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      //抓人
      catchperson(){
        const apiUrl = `${this.$apiUrl}/api/catch_member/`;
        this.$axios.post(apiUrl, { group_id: this.formData.group_id})
          .then(response => {
            const responseData = JSON.parse(response.data);
            console.log(responseData)
            this.persons = responseData.personal_name_list
            this.persons2 = responseData.personal_name_list
          })
          .catch(error => {
            console.error(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      handleExpenditure() {
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type==="支出")
      },
      handleIncome() {
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type==="收入")
      },
      temporary() {
        // Implement temporary save logic here
      },
      sure() {
        // Implement sure save logic here
      },
    }
}

</script>
<style scoped>
.form-control {
  font-size: 16px;
  color: black;
  padding: 0.5rem;
  border: 1px solid #ced4da;
  border-radius: 0.25rem;
  width: 100%;
  margin-bottom: 0.5rem;
  top: 0;
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