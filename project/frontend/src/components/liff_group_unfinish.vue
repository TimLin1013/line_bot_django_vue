<template>
    <div class="row" style="margin: 10px">
      <div>
        <button type="button" @click="homepage" class="btn-outline-info home-button">
          <img :src="homeimg" class="home" width="30" height="30">
        </button>
      </div>
      <label>付款人</label>
      <select v-model="formData.personal_id" class="form-control">
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
      <input v-model="formData.account_date" type="text" class="form-control" />
      <label>地點</label>
      <input v-model="formData.location" type="text" class="form-control" />
  
      <label>分帳人</label>
      <div v-for="(share, index) in shares" :key="index" class="form-group">
        <select v-model="share.person" class="form-control" @change="checkDuplicate(index)">
          <option value=""disabled>請選擇</option>
          <option v-for="personItem in persons2" :key="personItem.personal_id" :value="personItem.personal_id">
            {{ personItem.personal_name }}
          </option>
        </select>
        <input v-model="share.percentage" type="number" class="form-control" placeholder="分帳比例" @input="updateShares(index)" />
        <input v-model="share.advance_percentage" type="number" class="form-control" placeholder="預先給錢" />
        <button @click="removeShare(index,share)" class="btn btn-danger btn-block">移除</button>
      </div>
      <button @click="addShare" class="btn btn-primary btn-block">添加分帳人</button>
  
      <label>交易類型</label>
      <select v-model="transaction" class="form-control">
        <option value="" disabled>請選擇</option>
        <option value="支出">支出</option>
        <option value="收入">收入</option>
      </select>
      <label>類別</label>
      <select v-model="formData.category_name" class="form-control">
        <option value="" disabled>請選擇</option>
        <option v-for="category in tmp_list" :key="category.category_name" :value="category.category_name">
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
      formData2 :Object,
    },
    data() {
      return {
        currentTime: this.formData.account_date || this.formatCurrentTime(),
        category_list: [],
        tmp_list: [],
        indexList: [],
        persons: [],
        persons2: [],
        shares: [],
        transaction:this.formData.transaction_type,
        homeimg: require("@/assets/homepage.png"),
      }
    },
    watch: {
        transaction(newValue) {
            console.log('Transaction type changed to:', newValue);
            if (newValue === '支出') {
              this.handleExpenditure();
            } else if (newValue === '收入') {
              this.handleIncome();
            }
        },
        'formData.category_name': function(newValue) {
            console.log('Category changed to:', newValue);
        }
    },
    mounted() {
      this.catchcategory();
      this.catchperson();
    },
    methods: {
      homepage(){
        this.$router.push({ name: 'liff_search' });
      },
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
        names.forEach(name => {
          let person_member_id = null;
          this.persons2.forEach(personItem => {
            if (personItem.personal_name === name.personal_name) {
              person_member_id = personItem.personal_id;
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
            this.category_list = response.data.category.map(category => ({category_name: category.category_name,transaction_type: category.transaction_type}));
            this.updateTmpList();
          })
          .catch(error => {
            console.error(error);
          })
          .finally(() => {
            this.loading = false;
          });
      },
      updateTmpList() {
            if (this.formData.transaction_type === '支出') {
                this.handleExpenditure();
            } else if (this.formData.transaction_type === '收入') {
                this.handleIncome();
            }
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
        const newShareAmount = remainingPeopleCount > 0 ? Number((remainingAmount / remainingPeopleCount).toFixed(1)) : 0;
  
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
      addShare() {
        if(this.persons2.length <= this.shares.length){
          Swal.fire({
            title: '警告',
            text: '超過群組人數',
            icon: 'warning'
          });
          return;
        }
        else{
          this.shares.push({ person:'', percentage: null,advance_percentage:null });
          this.updateAllShares()
        }
      },
      removeShare(index,share) {
        this.shares.splice(index, 1);
        this.updateAllShares()
        const apiUrl = `${this.$apiUrl}/api/remove_spliter/`;
        this.$axios.post(apiUrl, {
          group_account_id:this.formData.group_account_id,
          share_person: share.person
        })
      },
      checkDuplicate(index) {
        const selectedPerson = this.shares[index].person;
        const duplicate = this.shares.some((share, idx) => share.person === selectedPerson && idx !== index);
  
        if (duplicate) {
          Swal.fire({
            title: '警告',
            text: '已選擇相同的分帳人',
            icon: 'warning'
          });
          this.shares[index].person = '';
        }
      },
      //暫存
      temporary() {
            if((this.formData.transaction_type==='支出' || this.formData.transaction_type==='收入' )){
                if(this.formData.category_name===''){
                    Swal.fire({
                        title: "請選擇類別!",
                        icon: "warning"
                    });
                    return;
                }
            }
            let total=0
            for (let i = 0; i < this.shares.length; i++) {
              if (this.shares[i].percentage < 0) {
                Swal.fire({
                    title: '警告',
                    text: '分帳金額不能為負值',
                    icon: 'warning'
                });
                return;
              }
              total = total + Number(this.shares[i].percentage)
            }
            if (total>this.formData.payment|| total<this.formData.payment){
                  Swal.fire({
                    title: '警告',
                    text: '分帳金額總和與總金額不符合',
                    icon: 'warning'
                  });
                  return;
            }
            const apiUrl = `${this.$apiUrl}/api/get_group_unfinish_temporary/`;
            this.$axios.post(apiUrl, {
                group_account_id:this.formData.group_account_id,
                group_id:this.formData.group_id,
                payer: this.personal,
                item: this.formData.item,
                payment: this.formData.payment,
                location: this.formData.location,
                transaction_type:this.transaction,
                category: this.formData.category_name,
                time: this.currentTime,
                shares: this.shares
            }).then(response => {
                if(response.data==='ok'){
                    Swal.fire({
                        title: "暫存成功!!",
                        icon: "success"
                    });
                    this.$router.push({ name: 'liff_search' });
                }
                if(response.data==='no'){
                  Swal.fire({
                        title: "請選擇類別!!",
                        icon: "warning"
                    });
                }
            })
                .catch(error => {
                    console.error(error);
                });
        },
      //完成確定
      sure() {
        if (this.formData.personal_id === '' || this.formData.item === '' || this.formData.payment === '' || this.formData.category_name === '' || this.transaction === '' || this.currentTime === '') {
            Swal.fire({
                title: "無法完成(完成確認只有地點可為空)，只能按暫存!",
                icon: "warning"
            });
            return;
        }
        let total=0
        for (let i = 0; i < this.shares.length; i++) {
          if (this.shares[i].percentage < 0) {
            Swal.fire({
                title: '警告',
                text: '分帳金額不能為負值',
                icon: 'warning'
            });
            return;
          }
          total = total + Number(this.shares[i].percentage)
        }
        if (total>this.formData.payment|| total<this.formData.payment){
              Swal.fire({
                title: '警告',
                text: '分帳金額總和與總金額不符合',
                icon: 'warning'
              });
              return;
        }
        const apiUrl = `${this.$apiUrl}/api/get_group_unfinish_sure/`;
        this.$axios.post(apiUrl, {
            group_account_id:this.formData.group_account_id,
            group_id:this.formData.group_id,
            payer: this.personal,
            item: this.formData.item,
            payment: this.formData.payment,
            location: this.formData.location,
            transaction_type:this.transaction,
            category: this.formData.category_name,
            time: this.currentTime,
            shares: this.shares
        }).then(response => {
            if (response.data==='ok'){
                Swal.fire({
                    title: "完成記帳!!",
                    icon: "success"
                });
                this.$router.push({ name: 'liff_search' });
            }
            if(response.data==='no'){
                Swal.fire({
                    title: "請選擇類別!!",
                    icon: "warning"
                });
            }
          })
          .catch(error => {
            console.error(error);
          });
        },
      handleExpenditure() {
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "支出");
      },
      handleIncome() {
        this.tmp_list = this.category_list.filter(category_list => category_list.transaction_type === "收入");
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
.home-button {
    position: absolute;
    top: 10px;
    left: 10px;
}
</style>
  