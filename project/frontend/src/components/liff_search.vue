<template>
  <div id="demo">

    <div class="btn-group fixed-buttons">
      <button :class="{ active: isAllExpense }" @click="showAllExpense" :disabled="loading">
        所有花費
      </button>
      <button :class="{ active: isPersonalExpense && !isAllExpense }" @click="showPersonalExpense" :disabled="loading">
        個人帳本
      </button>
      <button :class="{ active: !isPersonalExpense && !isAllExpense }" @click="showGroupExpense" :disabled="loading">
        群組帳本
      </button>
      
    </div>

    <div v-if="!isPersonalExpense && !isAllExpense" class="group-buttons-container">
      <div class="group-buttons">
        <button
          v-for="groups in group"
          :key="groups.group_id"
          :class="{ active: selectedGroupId === groups.group_id }"
          @click="filterByGroup(groups.group_id)"
        >
          {{ groups.group_name }}
        </button>
      </div>
    </div>
    <div class="date-selector">
      <button @click="prevMonth" :disabled="loading">←</button>
      <span>{{ currentYearMonth }}</span>
      <button @click="nextMonth" :disabled="loading">→</button>
    </div>
    
    <div class="fixed-container">
      <div class="scrollable-block">
        <table v-if="selectedAccounts.length > 0" class="account-area">
          <thead>
            <tr>
              <th>項目</th>
              
              <th>金額</th>
              <th>類別</th>
              
              
            </tr>
          </thead>
          <tbody>
            <tr v-for="(account, index) in selectedAccounts" :key="index">
              <td>{{ account.item }}</td>
              
              <td>{{ account.payment }}</td>
              <td>{{ account.category_name }}</td>
              
              
            </tr>
          </tbody>
        </table>
        <div v-else-if="loading" class="loading">載入中...</div>
        <div v-else class="account-area-placeholder"> 
          <h2>當天花費：</h2>
          <p>暫無資料</p>
        </div>
      </div>
    </div>

   

    <div class="bottom-buttons">
      <button @click="navigateToOverview" class="overview-button">
        <img :src="analysisimg" class="analysis" width="36" height="36" style="margin-left:6px;">
      </button>
      <div class="split-button">
        <button @click="manualAccounting" class="manual-accounting">
          <img :src="fromimg" class="form" width="32" height="32">
        </button>
        <button @click="voiceTextAccounting" class="voice-text-accounting">
          <img :src="plusimg" class="plus" width="32" height="32">
        </button>
      </div>
      <button @click="joinGroupAccount" class="group-account-button">
        <img :src="joingroupimg" class="joingroup" width="34" height="34">
      </button>
      <button @click="createGroupAccount" class="group-account-button">
        <img :src="creategroupimg" class="creategroup" width="42" height="42">
      </button>
    </div>
  </div>
</template>





<script>
import Swal from 'sweetalert2';
export default {
  data() {
    return {
      analysisimg: require('@/assets/analysis.png'),
      fromimg: require("@/assets/form.png"),
      plusimg: require("@/assets/plus.png"),
      creategroupimg: require("@/assets/creategroup.png"),
      joingroupimg: require("@/assets/joingroup.png"),
      selectedDate: '',
      accounts: [],
      isPersonalExpense: false,
      currentYearMonth: dayjs().format('YYYY-MM'),
      isAllExpense: true,
      loading: true,
      showCalendar: false,
      personal_id: '',
      categories: [],
      group: [],
      selectedGroupId: null,
      group_account: [],
      
    };
  },
  methods: {
    toggleCalendar() {
      this.showCalendar = !this.showCalendar;
      if (this.showCalendar) {
        const formattedDate = dayjs(new Date()).format('YYYY-MM-DD');
        this.selectedDate = formattedDate;
        console.log(formattedDate)
      }
    },
    onChange(date) {
      const formattedDate = dayjs(date).format('YYYY-MM-DD');
      this.selectedDate = formattedDate;
    },
    fetchAccounts() {

      const apiUrl = `${this.$apiUrl}/api/get_personal_account/`;
      console.log(apiUrl);
      console.log(this.$root.$userId);
      this.$axios.post(apiUrl, { userId: this.$root.$userId, name: this.$root.$userName })
        .then(response => {
          console.log(response);
          this.accounts = response.data.accounts;
          this.personal_id = this.$root.$personal_id
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {

          
        });
    },
    fetchGroup() {

      const apiUrl = `${this.$apiUrl}/api/get_group/`;
      console.log(apiUrl);
      console.log(this.$root.$personal_id);
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          console.log(response);
          this.group = response.data.groups;
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {

          
        });
    },
    fetchGroupAccount() {

      const apiUrl = `${this.$apiUrl}/api/get_group_account/`;
      console.log(apiUrl);
      console.log(this.$root.$personal_id);
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          console.log(response);
          
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {

          
        });
    },
    showAllExpense() {
      this.isPersonalExpense = false;
      this.isAllExpense = true;
      console.log(this.personal_id)
    },
    showPersonalExpense() {
      this.isPersonalExpense = true;
      this.isAllExpense = false;
    },
    showGroupExpense() {
      this.isPersonalExpense = false;
      this.isAllExpense = false;
      console.log(this.group)
    },
    filterByGroup(groupId) {
      this.selectedGroupId = groupId;
    },
    navigateToOverview() {
      this.$router.push({ name: 'account_overview' });
    },
    joinGroupAccount() {
      const { value: groupcode } = Swal.fire({
        title: "輸入群組代碼",
        input: "text",
        confirmButtonText: "加入",
        inputPlaceholder: "請輸入",
        inputValidator: (value) => {
          if (!value) {
            return "請輸入群組代碼!";
          }
        }
      }).then((result) => {
        console.log(result)
        if (result.isConfirmed) {
          const groupcode = result.value;
          const apiUrl = `${this.$apiUrl}/api/joingroup/`;
          this.$axios.post(apiUrl, { GroupCode: groupcode, Personal_ID: this.$root.$personal_id })
            .then(response => {
              console.log(response);
              if (response.data == '查無此群組，請重新輸入') {
                Swal.fire({
                  title: "查無此群組，請重新輸入!",
                  icon: "warning"
                });
              } else if (response.data == '已加入該群組，請重新核對您的群組代碼') {
                Swal.fire({
                  title: "已經有加入該群組，請重新核對您的群組代碼!",
                  icon: "warning"
                });
              } else if (response.data == '成功加入群組') {
                Swal.fire({
                  title: "成功加入群組!",
                  icon: "success"
                });
              }
            })
        }
      })
    },
    createGroupAccount() {
      const { value: groupname } = Swal.fire({
        title: "輸入群組名稱",
        input: "text",
        confirmButtonText: '創建',
        inputPlaceholder: "請輸入",
        inputValidator: (value) => {
          if (!value) {
            return "請輸入群組名稱!";
          } else if (value.length > 200) {
            return "群組名稱不能超過200個字!";
          }
        }
      }).then((result) => {
        console.log(result)
        if (result.isConfirmed) {
          const groupname = result.value;
          this.creategroup_axios(groupname);
          Swal.fire({
            title: "創建成功!",
            icon: "success"
          });
        }

      })
    },
    creategroup_axios(groupname) {
      const apiUrl = `${this.$apiUrl}/api/creategroup/`;
      this.$axios.post(apiUrl, { GroupName: groupname, userId: this.$root.$userId })
        .then(response => {
          console.log(response);
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    manualAccounting() {
      this.$router.push({ name: 'liff_personal_form', params: { formData: { item: '', payment: '', location: '', category: '', transaction_type: '' } } });
    },
    voiceTextAccounting() {
      this.$router.push({ name: 'liff_keep' });
    },
    editAccount(account) {
      // 處理修改帳目的邏輯，例如彈出表單進行編輯
      Swal.fire({
        title: '修改帳目',
        html: `
          <input id="swal-input1" class="swal2-input" placeholder="項目" value="${account.item}">
          <input id="swal-input2" class="swal2-input" placeholder="日期" value="${account.account_date}">
          <input id="swal-input3" class="swal2-input" placeholder="金額" value="${account.payment}">
          <input id="swal-input4" class="swal2-input" placeholder="類別" value="${account.category_name}">
        `,
        focusConfirm: false,
        preConfirm: () => {
          const item = document.getElementById('swal-input1').value;
          const account_date = document.getElementById('swal-input2').value;
          const payment = document.getElementById('swal-input3').value;
          const category_name = document.getElementById('swal-input4').value;
          return { item, account_date, payment, category_name };
        }
      }).then((result) => {
        if (result.isConfirmed) {
          // 處理更新帳目的邏輯，例如發送API請求
          console.log('Updated data:', result.value);
          // 此處可以調用更新帳目的API
        }
      });
    },
    deleteAccount(account) {
      // 處理刪除帳目的邏輯，例如彈出確認對話框
      Swal.fire({
        title: '確定要刪除嗎？',
        text: '此操作無法恢復！',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '是的，刪除它！',
        cancelButtonText: '取消'
      }).then((result) => {
        if (result.isConfirmed) {
          // 處理刪除帳目的邏輯，例如發送API請求
          console.log('Deleted account:', account);
          // 此處可以調用刪除帳目的API
        }
      });
    },
    prevMonth() {
      const newDate = dayjs(this.currentYearMonth).subtract(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
      this.fetchDataForMonth(newDate);
    },
    nextMonth() {
      const newDate = dayjs(this.currentYearMonth).add(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
      this.fetchDataForMonth(newDate);
    },
    fetchDataForMonth(date) {
      // 在這裡添加你獲取特定月份數據的邏輯
      console.log('Fetching data for:', date.format('YYYY-MM'));
    }
  },
  mounted() {
    const checkUserId = () => {
    if (this.$root.$userId === null || this.$root.$personal_id === null) {
      console.log();
      setTimeout(checkUserId, 500);
    } else {
      Promise.all([this.fetchAccounts(), this.fetchGroup(), this.fetchGroupAccount()])
        .then(() => {
          this.loading = false;
        })
        .catch(error => {
          console.error("An error occurred while fetching data:", error);
          this.loading = false; // Optional: set loading to false even if there's an error
        });
    }
  };

  checkUserId();
  },
  computed: {
    selectedAccounts() {
      let filteredAccounts = this.accounts;
      filteredAccounts= filteredAccounts.filter(account => account.flag===1)
      if (this.isAllExpense) {
        if (this.showCalendar) {
          filteredAccounts = filteredAccounts.filter(account => dayjs(account.account_date).isSame(this.selectedDate, 'day'))
        }
      } else if (this.isPersonalExpense) {

      }

      return filteredAccounts;
    },
    selectedUnfinishAccounts() {
      let filteredAccounts = this.accounts;
      filteredAccounts= filteredAccounts.filter(account => account.flag===0)
      if (this.isAllExpense) {
        if (this.showCalendar) {
          filteredAccounts = filteredAccounts.filter(account => dayjs(account.account_date).isSame(this.selectedDate, 'day'))
        }
      } else if (this.isPersonalExpense) {

      }

      return filteredAccounts;
    },
  }
};
</script>


<style scoped>
#demo {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

.fixed-buttons {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: #f9f9f9;
  z-index: 1000;
  padding: 6px 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
}

.fixed-container {
  border: 2px solid rgb(192, 233, 10); 
  margin-top: 40px; /* Adjust margin to make space for fixed buttons */
  height: calc(600px); 
  overflow-y: auto;
}

.scrollable-block {
  max-height: 100%; 
}


.account-area {
  border: 2px solid black; 
  padding: 1px; 
  font-size: 15px;
  width: 100%;
}


.account-area-placeholder {
  border: 2px solid black;
  padding: 1px; 
  opacity: 0.5; 
}

.account-area table {
  width: 100%; 
  border-collapse: collapse; 
}

.account-area th {
  border: 1px solid #ddd; 
  padding: 8px; 
}

.account-area td {
  border: 1px solid #ddd; 
  padding: 8px; 
  position: relative;
}
.account-area th {
  background-color: #f2f2f2;
}

.account-area tr:nth-child(even) {
  background-color: #f2f2f2; 
}

.account-area button {
  padding: 4px 8px;
  margin: 2px;
  border: none;
  border-radius: 4px;
  background-color: #FFCC00;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}
.account-area button:hover {
  transform: scale(1.05);
}

.account-area button:first-child {
  background-color: #007BFF; /* 藍色背景 */
  color: white; /* 白色字體 */
}

.account-area button:last-child {
  background-color: #DC3545; /* 紅色背景 */
  color: white; /* 白色字體 */
}
.btn-group {
  display: flex;
  justify-content: center;
  background-color:#FFEFDB;
  gap: 10px;
}

.btn-group button {
  padding: 8px 16px; 
  border: none;
  border-radius: 5px;
  background: #FFCC00; /* 深黃色背景 */
  color: black; /* 黑色字體 */
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.btn-group button.active {
  background: #ff1e00; /* 更淺的黃色 */
}

.btn-group button:hover {
  transform: scale(1.05);
}

.group-buttons-container {
  display: flex;
  justify-content: flex-start; 
  overflow-x: auto;
  padding: 10px 0;
  white-space: nowrap;
  background-color: #FFEFDB;
}

.group-buttons {
  display: flex;
  gap: 10px;
}

.group-buttons button {
  padding: 8px 16px; 
  border: none;
  border-radius: 5px;
  background: #FFCC00; /* 深黃色背景 */
  color: black; /* 黑色字體 */
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.group-buttons button.active {
  background: #ff1e00; /* 更淺的黃色 */
}

.group-buttons button:hover {
  transform: scale(1.05);
}

.bottom-buttons {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color:#FFEFDB;
  z-index: 1000;
  padding: 10px 0;
  box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.bottom-buttons button {
  padding: 6px 16px; 
  border: none;
  border-radius: 16px;
  background: #FFFF;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.bottom-buttons button:hover {
  transform: scale(1.05);
}

.split-button {
  display: flex;
}

.manual-accounting {
  background: #FFCC00; /* 深黃色背景 */
  color: black; /* 黑色字體 */
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
  margin-right: 10px;
}

.manual-accounting:hover {
  transform: scale(1.05);
}

.voice-text-accounting {
  background: #FFCC00; /* 深黃色背景 */
  color: black; /* 黑色字體 */
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.voice-text-accounting:hover {
  transform: scale(1.05);
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  z-index: 9999;
}

.toggle-calendar-button {
  margin-bottom: 20px;
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  border-radius: 20px;
  background: #FFCC00; /* 深黃色背景 */
  color: black; /* 黑色字體 */
  transition: background 0.3s ease, transform 0.3s ease;
}

.toggle-calendar-button:hover {
  transform: scale(1.05);
}
.date-selector {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.date-selector button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  margin: 0 10px;
}

.date-selector span {
  font-size: 18px;
}

</style>
