<template>
  <div id="demo">
    <!-- 頂部 -->
    <nav class="navbar navbar-light bg-light fixed-top">
      <div class="container-fluid">
        <button type="button" id="sidebarCollapse" class="btn btn-link" @click="toggleSidebar">
          <i class="fas fa-bars"></i>
        </button>
        <span class="navbar-brand mb-0 h1">記帳app</span>
      </div>
    </nav>

    <!-- 側邊 -->
    <nav id="sidebar" class="bg-light">
      <ul class="list-unstyled components">
        <li>
          <a href="#" @click="showPersonalExpense" :class="{ active: isPersonalExpense }">個人帳本</a>
        </li>
        <li>
          <a href="#" @click="showGroupExpense" :class="{ active: isGroupExpense }">群組帳本</a>
        </li>
        <li>
          <a href="#" @click="showPayBack" :class="{ active: isPayBack }">還錢通知</a>
        </li>
      </ul>
    </nav>

    <!-- 頁面内容 -->
    <div id="content" class="p-4 p-md-5">
      <!-- 個人帳本 -->
      <div v-if="isPersonalExpense" class="personal-expense-container">
        <div class="date-selector">
          <button class="btn btn-outline-secondary" @click="prevMonth" :disabled="loading">←</button>
          <span class="mx-3">{{ currentYearMonth }}</span>
          <button class="btn btn-outline-secondary" @click="nextMonth" :disabled="loading">→</button>
        </div>
        <div class="fixed-container">
          <div class="scrollable-block">
            <table v-if="selectedAccounts.length > 0" class="table table-striped">
              <thead>
                <tr>
                  <th>項目</th>
                  <th>金額</th>
                  <th>類別</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in selectedAccounts" :key="account.id">
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
      </div>

      <!-- 群組帳本 -->
      <div v-if="isGroupExpense" class="group-expense-container">
        <div class="group-buttons-container">
          <div class="group-buttons">
            <button
              v-for="groups in group"
              :key="groups.group_id"
              class="btn"
              :class="{ 'btn-primary': selectedGroupId === groups.group_id, 'btn-outline-primary': selectedGroupId !== groups.group_id }"
              @click="filterByGroup(groups.group_id)"
            >
              {{ groups.group_name }}
            </button>
          </div>
        </div>
        <div class="date-selector">
          <button class="btn btn-outline-secondary" @click="prevMonth" :disabled="loading">←</button>
          <span class="mx-3">{{ currentYearMonth }}</span>
          <button class="btn btn-outline-secondary" @click="nextMonth" :disabled="loading">→</button>
        </div>
        <div class="fixed-container">
          <div class="scrollable-block">
            <table v-if="selectedAccounts.length > 0" class="table table-striped">
              <thead>
                <tr>
                  <th>項目</th>
                  <th>金額</th>
                  <th>類別</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in selectedAccounts" :key="account.id">
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
      </div>

      <!-- 還錢通知 -->
      <div v-if="isPayBack" class="payback-container">
          <div class="scrollable-block">
              <table v-if="payBackAccounts.length > 0 || payBackAccounts2.length > 0" class="table table-striped account-area">
                  <thead>
                      <tr>
                          <th>歸還金額</th>
                          <th>欠款人</th>
                          <th>收款人</th>
                          <th>群組名稱</th>
                          <th>還錢狀態</th>
                      </tr>
                  </thead>
                  <tbody>
                      <tr v-for="(account, index) in payBackAccounts" :key="index">
                          <td>{{ account.return_payment }}</td>
                          <td>{{ account.payer }}</td>
                          <td>{{ account.receiver }}</td>
                          <td>{{ account.group_name }}</td> <!-- 新增顯示群組名稱 -->
                          <td :class="{ 'unpaid': account.return_flag === 0 }">
                              {{ account.return_flag === 0 ? '尚未歸還' : '已歸還' }}
                          </td>
                      </tr>
                      <!-- 如果有第二個列表也需要顯示群組名稱 -->
                      <tr v-for="(account, index) in payBackAccounts2" :key="index">
                          <td>{{ account.return_payment }}</td>
                          <td>{{ account.payer }}</td>
                          <td>{{ account.receiver }}</td>
                          <td>{{ account.group_name }}</td> <!-- 新增顯示群組名稱 -->
                          <td :class="{ 'unpaid': account.return_flag === 0 }">
                              {{ account.return_flag === 0 ? '已歸還' : '尚未歸還' }} <!-- 注意這裡的顯示邏輯是否需要調整 -->
                          </td>
                      </tr>
                  </tbody>
              </table>
              <div v-else-if="loading" class="loading">載入中...</div>
              <div v-else class="account-area-placeholder">
                  <h2>還錢通知：</h2>
                  <p>暫無資料</p>
              </div>
          </div>
      </div>

      <!-- 底部按鈕 -->
      <div class="bottom-buttons">
        <div class="button-container" @click="navigateToOverview">
          <button class="btn btn-outline-info overview-button">
            <img :src="analysisimg" class="analysis" width="30" height="30">
          </button>
          <div class="button-text">報表</div>
        </div>
        <div class="button-container" @click="manualAccounting">
          <button class="btn btn-outline-info manual-accounting">
            <img :src="fromimg" class="form" width="30" height="30">
          </button>
          <div class="button-text">手動記帳</div>
        </div>
        <div class="button-container" @click="voiceTextAccounting">
          <button class="btn btn-outline-info voice-text-accounting">
            <img :src="plusimg" class="plus" width="30" height="30">
          </button>
          <div class="button-text">個人記帳</div>
        </div>
        <div class="button-container" @click="joinGroupAccount">
          <button class="btn btn-outline-info group-account-button">
            <img :src="joingroupimg" class="joingroup" width="30" height="30">
          </button>
          <div class="button-text">加入群組</div>
        </div>
        <div class="button-container" @click="createGroupAccount">
          <button class="btn btn-outline-info group-account-button">
            <img :src="creategroupimg" class="creategroup" width="30" height="30">
          </button>
          <div class="button-text">創建群組</div>
        </div>
      </div>
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
      isPersonalExpense: true,
      isGroupExpense: false,
      isAllExpense: false,
      isPayBack: false,
      currentYearMonth: dayjs().format('YYYY-MM'),
      loading: true,
      personal_id: '',
      group: [],
      group2: [],
      inputOptions: {},
      selectedGroupId: null,
      group_account: [],
      payBackAccounts: [],
      payBackAccounts2: [],
    };
  },
  methods: {
    toggleSidebar() {
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.toggle('active');
    },
    showPersonalExpense() {
      this.isPersonalExpense = true;
      this.isGroupExpense = false;
      this.isAllExpense = false;
      this.isPayBack = false;
      this.toggleSidebar();
    },
    showGroupExpense() {
      this.isPersonalExpense = false;
      this.isGroupExpense = true;
      this.isAllExpense = false;
      this.isPayBack = false;
      this.toggleSidebar();
    },
    showPayBack() {
      this.isPersonalExpense = false;
      this.isGroupExpense = false;
      this.isAllExpense = false;
      this.isPayBack = true;
      this.fetchPayBack();
      this.toggleSidebar();
    },
    prevMonth() {
      const newDate = dayjs(this.currentYearMonth).subtract(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
      if (this.isPersonalExpense) {
        this.fetchPersonalExpenseDataForMonth(newDate);
      } else if (this.isGroupExpense) {
        this.fetchGroupExpenseDataForMonth(newDate);
      }
    },
    nextMonth() {
      const newDate = dayjs(this.currentYearMonth).add(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
      if (this.isPersonalExpense) {
        this.fetchPersonalExpenseDataForMonth(newDate);
      } else if (this.isGroupExpense) {
        this.fetchGroupExpenseDataForMonth(newDate);
      }
    },
    fetchPersonalExpenseDataForMonth(date) {
      console.log('Fetching personal expense data for:', date.format('YYYY-MM'));
      const apiUrl = `${this.$apiUrl}/api/get_personal_expense_data/`;
      this.loading = true;
      this.$axios.post(apiUrl, { account_date: date.format('YYYY-MM'), personal_id: this.personal_id })
        .then(response => {
          this.accounts = response.data.accounts;
        })
        .catch(error => {
          console.error('Error fetching personal expense data:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchGroupExpenseDataForMonth(date) {
      console.log('Fetching group expense data for:', date.format('YYYY-MM'));
      const apiUrl = `${this.$apiUrl}/api/get_group_expense_data/`;
      this.loading = true;
      this.$axios.post(apiUrl, { account_date: date.format('YYYY-MM'), group_id: this.selectedGroupId })
        .then(response => {
          this.accounts = response.data.accounts;
        })
        .catch(error => {
          console.error('Error fetching group expense data:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    navigateToOverview() {
      this.$router.push({ name: 'liff_account_overview' });
    },
    //群組記帳
    manualAccounting() {
      const apiUrl = `${this.$apiUrl}/api/get_group/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          this.group2 = response.data.groups;
          this.group2.forEach(group => {
            this.inputOptions[group.group_id] = group.group_name;
          });
          Swal.fire({
            title: "選擇帳本",
            input: "select",
            inputOptions: this.inputOptions,
            inputPlaceholder: "選擇一個帳本",
            showCancelButton: true,
            inputValidator: (value) => {
              if (!value) {
                return "請選擇帳本";
              }
            }
          }).then((result) => {
              this.$router.push({ name: 'liff_group_form', params: { formData: { group_id: result.value, item: '', payment: '', location: '' } } });
          });
        });
    },
    voiceTextAccounting() {
      Swal.fire({
        title: "快速記帳",
        input: "text",
        confirmButtonText: "送出",
        inputPlaceholder: "請輸入",
        inputValidator: (value) => {
          if (!value) {
            return "請輸入資訊!";
          }
        }
      }).then((result) => {
        if (result.isConfirmed) {
          const data = result.value;
          Swal.fire({
            title: '請稍候...',
            allowOutsideClick: false,
            didOpen: () => {
              Swal.showLoading();
            }
          });
          const apiUrl = `${this.$apiUrl}/api/get_user_account_info/`;
          this.$axios.post(apiUrl, { user_input: data, personal_id: this.$root.$personal_id })
            .then(response => {
              Swal.close();
              if (response.data.temp === '錯誤') {
                Swal.fire({
                  text: "請檢查輸入的記帳內容!",
                  icon: "warning"
                });
              } else {
                this.$router.push({ name: 'liff_personal_form', params: { formData: response.data.temp } });
              }
            })
            .catch(error => {
              Swal.close();
              console.error('Error:', error);
            });
        }
      });
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
        if (result.isConfirmed) {
          const groupcode = result.value;
          const apiUrl = `${this.$apiUrl}/api/joingroup/`;
          this.$axios.post(apiUrl, { GroupCode: groupcode, Personal_ID: this.$root.$personal_id })
            .then(response => {
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
            });
        }
      });
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
        if (result.isConfirmed) {
          const groupname = result.value;
          this.creategroup_axios(groupname);
          Swal.fire({
            title: "創建成功!",
            icon: "success"
          });
        }
      });
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
    filterByGroup(groupId) {
      this.selectedGroupId = groupId;
    },
    fetchPayBack() {
      const apiUrl = `${this.$apiUrl}/api/get_payback/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          this.payBackAccounts = response.data.payer_payback_list;
          this.payBackAccounts2 = response.data.receiver_payback_list;
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchAccounts() {
      const apiUrl = `${this.$apiUrl}/api/get_personal_account/`;
      this.$axios.post(apiUrl, { userId: this.$root.$userId, name: this.$root.$userName })
        .then(response => {
          this.accounts = response.data.accounts;
          this.personal_id = this.$root.$personal_id;
        })
        .catch(error => {
          console.error(error);
        });
    },
    fetchGroup() {
      const apiUrl = `${this.$apiUrl}/api/get_group/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          this.group = response.data.groups;
        })
        .catch(error => {
          console.error(error);
        });
    },
    fetchGroupAccount() {
      const apiUrl = `${this.$apiUrl}/api/get_group_account/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          console.log(response);
        })
        .catch(error => {
          console.error(error);
        });
    },
  },
  mounted() {
    const checkUserId = () => {
      if (this.$root.$userId === null || this.$root.$personal_id === null) {
        setTimeout(checkUserId, 500);
      } else {
        Promise.all([this.fetchAccounts(), this.fetchGroup(), this.fetchGroupAccount()])
          .then(() => {
            this.loading = false;
          })
          .catch(error => {
            console.error("An error occurred while fetching data:", error);
            this.loading = false; 
          });
      }
    };
    checkUserId();
  },
  computed: {
    selectedAccounts() {
      let filteredAccounts = this.accounts;
      filteredAccounts = filteredAccounts.filter(account => account.flag === 1);
      filteredAccounts = filteredAccounts.filter(account => account.account_date.slice(0, 7) === this.currentYearMonth);
      if (this.isPersonalExpense) {
        return filteredAccounts;
      } else if (this.isGroupExpense) {
        return filteredAccounts.filter(account => account.group_id === this.selectedGroupId);
      }
      return filteredAccounts;
    },
    selectedPayBackAccounts() {
      let filteredAccounts = this.payBackAccounts;
      if (this.isPayBack) {
        filteredAccounts = filteredAccounts.filter(account => dayjs(account.account_date).isSame(this.selectedDate, 'day'));
      }
      return filteredAccounts;
    },
  }
};
</script>

<style scoped>
body {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  background-color: #fafafa;
  color: #333;
}

#demo {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  background: #FFEFDB;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 1030; 
}

#sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 150px;
  height: 100%;
  background: #FFEFDB;
  transition: all 0.5s ease;
  transform: translateX(-250px);
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 1020; 
}

#sidebar.active {
  transform: translateX(0);
}

.sidebar-header {
  padding: 20px; 
  background: #FFE4B5;
  border-bottom: 1px solid #FFCC99;
}

#sidebar ul.components {
  padding: 60px 0 20px 0; 
  border-bottom: 1px solid #FFCC99;
}

#sidebar ul li a {
  padding: 15px;
  font-size: 1.1em;
  display: block;
  color: #333;
  transition: 0.3s;
  border-radius: 4px;
}

#sidebar ul li a:hover {
  background: #FFC299;
  color: #fff;
}

#sidebar ul li a.active {
  background: #FFA07A;
  color: #fff;
}

#content {
  flex-grow: 1;
  padding: 20px;
  margin-top: 56px; 
}

.payback-container, .fixed-container {
  margin-top: 20px;
}

.scrollable-block {
  max-height: 100%;
  overflow-y: auto;
}

.account-area {
  border: 2px solid #FFA07A;
  padding: 1px;
  font-size: 15px;
  width: 100%;
}

.account-area-placeholder {
  border: 2px solid #FFA07A;
  padding: 1px;
  opacity: 0.5;
}

.table th, .table td {
  vertical-align: middle;
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

.group-buttons-container {
  display: flex;
  justify-content: center;
  overflow-x: auto;
  padding: 10px 0;
  white-space: nowrap;
  background-color: #FFEFDB;
}

.group-buttons {
  display: flex;
  gap: 10px;
}

.group-buttons .btn {
  padding: 8px 16px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.3s ease;
}

.group-buttons .btn-primary {
  background: #FFA07A;
  color: white;
}

.group-buttons .btn-outline-primary {
  background: #fff;
  border: 2px solid #FFA07A;
  color: #FFA07A;
}

.group-buttons .btn:hover {
  transform: scale(1.05);
}

.date-selector {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.date-selector button {
  margin: 0 10px;
  background: #FFA07A;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
  transition: background 0.3s;
}

.date-selector button:hover {
  background: #FF7F50;
}

.bottom-buttons {
  display: flex;
  justify-content: space-evenly;
  gap: 8px;
  flex-wrap: wrap;
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100vw;
  background: #FFEFDB;
  padding: 10px 0;
  margin: 0;
  box-shadow: 0 -2px 4px rgba(0,0,0,0.1);
  z-index: 1030; 
}

.button-container {
  text-align: center;
}

.button-container .btn-outline-info {
  border-color: #FFA07A;
  color: #FFA07A;
}

.button-container .btn-outline-info:hover {
  background: #FFA07A;
  color: white;
}

.button-text {
  font-size: 12px;
  margin-top: 5px;
  text-align: center;
  color: black;
  width: 55px;
  line-height: 1.2;
  white-space: pre-wrap;
  padding-left: 6px;
}

.unpaid {
  color: red;
}
</style>
