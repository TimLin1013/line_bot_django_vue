<template>
  <div class="row" style="margin: 10px">
      <label>個人ID</label>
      <input v-model="personal_id" readonly type="text" class="form-control" />
      <br>
      <label>項目</label>
      <input v-model="formData.item" type="text" class="form-control" />
      <br>
      <label>金額</label>
      <input v-model="formData.payment" type="number" class="form-control" />
      <br>
      <label>時間</label>
      <input v-model="currentTime" type="text" class="form-control" />
      <br>
      <label>地點</label>
      <input v-model="formData.location" type="text" class="form-control" />
      <br>
      <label>交易類型</label>
      <select v-model="transaction" class="form-control">
        <option value="" disabled>請選擇</option>
        <option value="支出">支出</option>
        <option value="收入">收入</option>
      </select>
      <br>
      <label>類別</label>
      <select v-model="formData.category" class="form-control">
        <option value="" disabled>請選擇</option>
        <option v-for="category in tmp_list" :key="category" :value="category.category_name">
          {{ category.category_name }}
        </option>
      </select>
      <br>
      <button @click="temporary" class="btn btn-warning btn-block">暫存</button>
      <button @click="sure" class="btn btn-warning btn-block">完成確定</button>
      <br>
      
  </div>
</template>

<script>
import Swal from 'sweetalert2';
export default {
  props: {
    formData: Object
  },
  data() {
    return {
      personal_id: this.$root.$personal_id,
      category_list: [],
      currentTime: this.formatCurrentTime(),
      tmp_list: [],
      date: '',
      transaction: this.formData.transaction_type,
      selectedCategory: ''
    };
  },
  watch: {
    transaction(newValue) {
      console.log('Transaction type changed to:', newValue);
      if (newValue === '支出') {
        console.log("ok")
        this.handleExpenditure();
      } else if (newValue === '收入') {
        this.handleIncome();
      }
    },
    selectedCategory(newValue) {
      this.formData.category = newValue; 
    }
  },
  mounted() {
    this.catchcategory()
  },
  methods: {
    formatCurrentTime() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      },
    //抓取使用者類別
    catchcategory() {
      const apiUrl = `${this.$apiUrl}/api/returncategory/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          console.log(response);
          this.category_list = response.data.category.map(category => ({ category_name: category.category_name, transaction_type: category.transaction_type }));
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
      this.$axios.post(apiUrl, {
        userID: this.$root.$personal_id,
        item: this.formData.item,
        payment: this.formData.payment,
        location: this.formData.location,
        category: this.formData.category,
        transaction_type:this.transaction,
        time: this.currentTime
      }).then(response => {
        if(response.data==='no'){
            Swal.fire({
                title: "請選擇類別!!",
                icon: "warning"
            });
        }
        if(response.data==='ok'){
          Swal.fire({
            title: "暫存成功!!",
            icon: "success"
        });
        this.$router.push({ name: 'liff_search' });
      }
        })
        .catch(error => {
          console.error(error);
        });
    },
    //完成確定
    sure() {
      if (this.personal_id === '' || this.formData.item === '' || this.formData.payment === '' || this.formData.category === '' || this.transaction === '' || this.currentTime === '') {
        Swal.fire({
          title: "無法完成(完成確認只有地點可為空)，只能按暫存!",
          icon: "warning"
        });
        return;
      }

      const apiUrl = `${this.$apiUrl}/api/get_keep_sure/`;
      console.log(apiUrl);
      this.$axios.post(apiUrl, {
        userID: this.$root.$personal_id,
        item: this.formData.item,
        payment: this.formData.payment,
        location: this.formData.location,
        category: this.formData.category,
        transaction_type:this.transaction,
        time: this.currentTime
      }).then(response => {
        if(response.data==='no'){
            Swal.fire({
                title: "請選擇類別!!",
                icon: "warning"
            });
          return
        }
        if(response.data==='ok'){
          Swal.fire({
            title: "完成記帳!!",
            icon: "success"
          });
          this.$router.push({ name: 'liff_search' });
        }
        })
        .catch(error => {
          console.error(error);
        });
    },
    handleExpenditure() {
      this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "支出")
    },
    handleIncome() {
      this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "收入")
    }
  },
};
</script>

<style scoped>
.form-control {
  font-size: 16px;
  color: black;
  padding: 0.5rem;
  border: 0.5px solid #000000; /* 设置边框颜色为黑色 */
  width: 100%;
  margin-bottom: 0.5rem;
  top: 0;
}

.input-group-text {
  font-size: 16px;
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
