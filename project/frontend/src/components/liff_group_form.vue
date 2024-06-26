<template>
  <div class="row" style="margin: 10px">
    <label>付款人</label>
    <select v-model="personal" class="form-control">
      <option value="" disabled>請選擇</option>
      <option v-for="personItem in persons" :key="personItem.personal_id" :value="personItem.personal_id">
        {{ personItem.personal_name }}
      </option>
    </select>
    <label>項目</label>
    <input v-model="formData.item" type="text" class="form-control" />
    <label>金額</label>
    <input v-model="formData.payment" type="number" class="form-control" />
    <label>時間</label>
    <input v-model="currentTime" type="text" class="form-control" />
    <label>地點</label>
    <input v-model="formData.location" type="text" class="form-control" />

    <label>分帳人</label>
    <div v-for="(share, index) in shares" :key="index" class="form-group">
      <select v-model="share.person" class="form-control">
        <option value=""disabled>請選擇</option>
        <option v-for="personItem in persons2" :key="personItem.personal_id" :value="personItem.personal_id">
          {{ personItem.personal_name }}
        </option>
      </select>
      <input v-model="share.percentage" type="number" class="form-control" placeholder="分帳比例" @input="updateShares(index)" />
      <input v-model="share.advance_percentage" type="number" class="form-control" placeholder="預先給錢" />
      <button @click="removeShare(index)" class="btn btn-danger btn-block">移除</button>
    </div>
    <button @click="addShare" class="btn btn-primary btn-block">添加分帳人</button>

    <label>交易類型</label>
    <select v-model="transaction" class="form-control">
      <option value="" disabled>請選擇</option>
      <option value="expenditure">支出</option>
      <option value="income">收入</option>
    </select>
    <label>類別</label>
    <select v-model="category_temp" class="form-control">
      <option value="" disabled>請選擇</option>
      <option v-for="category in tmp_list" :key="category" :value="category">
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
    formData: Object,
    formData2 :Array
  },
  data() {
    return {
      currentTime: this.formatCurrentTime(),
      category_list: [],
      tmp_list: [],
      personal: this.$root.$personal_id,
      indexList: [],
      person2: '',
      persons: [],
      persons2: [],
      transaction: '',
      category_temp: '',
      shares: []
    }
  },
  mounted() {
    this.catchcategory();
    this.catchperson();
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
  methods: {
    formatCurrentTime() {
      const now = new Date();
      const year = now.getFullYear();
      const month = String(now.getMonth() + 1).padStart(2, '0');
      const day = String(now.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    initializeShares() {
      const counter = this.formData2.length;
      const divide = this.formData.payment / counter;
      const names = this.formData2;
      console.log(this.persons2)
      console.log(names)
      names.forEach(name => {
        let person_member_id = null;
        this.persons2.forEach(personItem => {
          if (personItem.personal_name === name) {
            person_member_id = personItem.personal_id;
            console.log(person_member_id);
          }
        });
        if (person_member_id !== null) {
          this.shares.push({ person: person_member_id, percentage: divide ,advance_percentage:null});
        }
      });
    },
    //抓類別
    catchcategory() {
      const apiUrl = `${this.$apiUrl}/api/return_group_category/`;
      this.$axios.post(apiUrl, { group_id: this.formData.group_id })
        .then(response => {
          this.category_list = response.data.category.map(category => ({
            category_name: category.category_name,
            transaction_type: category.transaction_type
          }));
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    //抓人
    catchperson() {
      const apiUrl = `${this.$apiUrl}/api/catch_member/`;
      this.$axios.post(apiUrl, { group_id: this.formData.group_id })
        .then(response => {
          const responseData = JSON.parse(response.data);
          this.persons = responseData.personal_name_list;
          this.persons2 = responseData.personal_name_list;
          this.initializeShares()
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    updateShares(index) {
      if (!this.indexList.includes(index)) {
        this.indexList.push(index);
      }
      const totalAmount = this.formData.payment;
      // 計算已修改的總金額
      const totalModifiedAmount = this.indexList.reduce((sum, idx) => sum + Number(this.shares[idx].percentage), 0);
      // 剩餘金額
      const remainingAmount = totalAmount - totalModifiedAmount;
      // 剩餘未修改的人數
      const remainingPeopleCount = this.shares.length - this.indexList.length;
      // 計算其他人的分帳金額
      const newShareAmount = remainingPeopleCount > 0 ? remainingAmount / remainingPeopleCount : 0;

      for (let i = 0; i < this.shares.length; i++) {
        if (!this.indexList.includes(i)) {
          this.shares[i].percentage = newShareAmount;
        }
      }
    },
    updateAllShares() {
      const totalShares = this.shares.length;
      const equalShare = this.formData.payment / totalShares;
      for(let i=0;i<this.shares.length;i++){
        this.shares[i].percentage = equalShare
      }
    },
    handleExpenditure() {
      this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "支出");
    },
    handleIncome() {
      this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "收入");
    },
    addShare() {
      this.shares.push({ person:'', percentage: null,advance_percentage:null });
      this.updateAllShares()
    },
    removeShare(index) {
      this.shares.splice(index, 1);
      this.updateAllShares()
    },
    temporary() {
      const apiUrl = `${this.$apiUrl}/api/get_group_keep_temporary/`;
      this.$axios.post(apiUrl, {
        group_id: this.formData.group_id,
        payer: this.personal,
        item: this.formData.item,
        payment: this.formData.payment,
        location: this.formData.location,
        category: this.category_temp,
        time: this.currentTime,
        shares: this.shares
      }).then(response => {
        console.log(response);
        Swal.fire({
          title: "暫存成功!!",
          icon: "success"
        });
        this.$router.push({ name: 'liff_search' });
      })
        .catch(error => {
          console.error(error);
        });
    },
    sure() {
      if (this.formData.item === '' || this.formData.payment === '' || this.category_temp === '' || this.transaction === '' || this.currentTime === '') {
        Swal.fire({
          title: "無法完成(完成確認只有地點可為空)，只能按暫存!",
          icon: "warning"
        });
        return;
      }
      const apiUrl = `${this.$apiUrl}/api/get_group_keep_sure/`;
      console.log(apiUrl);
      this.$axios.post(apiUrl, {
        group_id: this.formData.group_id,
        payer: this.personal,
        item: this.formData.item,
        payment: this.formData.payment,
        location: this.formData.location,
        category: this.category_temp,
        time: this.currentTime,
        shares: this.shares
      }).then(response => {
        console.log(response);
        Swal.fire({
          title: "完成記帳!!",
          icon: "success"
        });
        this.$router.push({ name: 'liff_search' });
      })
        .catch(error => {
          console.error(error);
        });
    }
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

.btn-primary {
  font-size: 16px;
  color: white;
  background-color: #007bff;
  border-color: #007bff;
  padding: 0.5rem;
  width: 100%;
  margin-bottom: 1rem;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #004085;
}

.btn-danger {
  font-size: 16px;
  color: white;
  background-color: #dc3545;
  border-color: #dc3545;
  padding: 0.5rem;
  width: 100%;
  margin-bottom: 1rem;
}

.btn-danger:hover {
  background-color: #c82333;
  border-color: #bd2130;
}
</style>
