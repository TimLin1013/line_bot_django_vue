<template>
  <div id="demo">
    <!-- 頂部 -->
    <nav class="navbar navbar-light bg-light fixed-top">
      <div class="container-fluid">
        <button type="button" id="sidebarCollapse" class="btn btn-link" @click="toggleSidebar">
          <i class="fas fa-bars"></i>
        </button>
        <div class="ml-auto">
          <img v-if="$root.$userPictureUrl" :src="$root.$userPictureUrl" alt="Profile Picture" class="profile-picture"/>
          <span class="personal-id">個人資訊: {{ this.$root.$userName+" "+personal_id }}</span>
        </div>
      </div>
    </nav>

    <!-- 側邊 -->
    <nav id="sidebar" ref="sidebar" :class="{ 'active': sidebarActive }" class="bg-light">
      <ul class="list-unstyled components">
        <li>
          <a href="#" @click="showPersonalExpense()" :class="{ active: isPersonalExpense }">個人帳本</a>
        </li>
        <li>
          <a href="#" @click="showGroupExpense()" :class="{ active: isGroupExpense }">群組帳本</a>
        </li>
        <li>
          <a href="#" @click="showPayBack()" :class="{ active: isPayBack }">還錢通知</a>
        </li>
        <li>
          <a href="#" @click="isInfo()" :class="{ active: isPersonalInfo }">群組資訊</a>
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
            <table v-if="filteredAccounts.length > 0" class="table table-striped">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>項目</th>
                  <th>金額</th>
                  <th>類別</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in filteredAccounts" :key="account.id">
                  <td>{{ account.account_date.slice(5, 10)}}</td>
                  <td>{{ account.item }}</td>
                  <td>{{ account.payment }}</td>
                  <td>{{ account.category_name }}</td>
                  <td>
                    <button class="delete" @click="deleteAccount(account.personal_account_id)">刪除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else-if="loading" class="loading">載入中...</div>
            <div v-else class="account-area-placeholder">
              <h2>當月花費：</h2>
              <p>暫無資料</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 群組帳本 -->
      <div v-if="isGroupExpense" class="group-expense-container">
        <div class="group-selector">
          <select class="form-select" v-model="selectedGroupId">
            <option v-for="groups in group" :key="groups.group_id" :value="groups.group_id">
              {{ groups.group_name }}
            </option>
          </select>
        </div>
        <div class="date-selector">
          <button class="btn btn-outline-secondary" @click="prevMonth" :disabled="loading">←</button>
          <span class="mx-3">{{ currentYearMonth }}</span>
          <button class="btn btn-outline-secondary" @click="nextMonth" :disabled="loading">→</button>
        </div>
        <div class="fixed-container">
          <div class="scrollable-block">
            <table v-if="filteredAccounts.length > 0" class="table table-striped">
              <thead>
                <tr>
                  <th>日期</th>
                  <th>項目</th>
                  <th>金額</th>
                  <th>類別</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="account in filteredAccounts" :key="account.id">
                  <td>{{ account.account_date.slice(5, 10) }}</td>
                  <td>{{ account.group_account_item }}</td>
                  <td>{{ account.payment }}</td>
                  <td>{{ account.category_name }}</td>
                  <td>
                    <button class="delete_group" @click="deletegroupAccount(account.group_account_id,account.group_id)">刪除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else-if="loading" class="loading">載入中...</div>
            <div v-else class="account-area-placeholder">
              <h2>當月花費：</h2>
              <p>暫無資料</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 還錢通知 -->
      <div v-if="isPayBack" class="payback-container">
        <!-- 應付帳款（我是欠款人） -->
        <div class="payback-section">
          <h3>應付帳款</h3>
          <table v-if="payBackAccounts.length > 0" class="table table-striped account-area">
            <thead>
              <tr>
                <th>金額</th>
                <th>收款人</th>
                <th>群組</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(account, index) in payBackAccounts" :key="index">
                <td>{{ account.return_payment }}</td>
                <td>{{ account.receiver }}</td>
                <td>{{ account.group_name }}</td>
                <td>
                  <button v-if="account.return_flag === '0'" @click="markAsPaid(index, 'payer')" class="btn btn-warning w-100">
                    尚未還款
                  </button>
                  <span v-else>
                    已還款
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="account-area-placeholder">
            <p>暫無應付帳款資料</p>
          </div>
        </div>

        <!-- 應收帳款（我是收款人） -->
        <div class="payback-section">
          <h3>應收帳款</h3>
          <table v-if="payBackAccounts2.length > 0" class="table table-striped account-area">
            <thead>
              <tr>
                <th>金額</th>
                <th>欠款人</th>
                <th>群組</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(account, index) in payBackAccounts2" :key="index">
                <td>{{ account.return_payment }}</td>
                <td>{{ account.payer }}</td>
                <td>{{ account.group_name }}</td>
                <td>
                  <p v-if="account.return_flag === '0'">
                    尚未還款
                  </p>
                  <p v-else>
                    已還款
                  </p>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="account-area-placeholder">
            <p>暫無應收帳款資料</p>
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
        <div class="button-container" @click="groupAccounting">
          <button class="btn btn-outline-info manual-accounting">
            <img :src="fromimg" class="form" width="30" height="30">
          </button>
          <div class="button-text">群組記帳</div>
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
      <!-- 群組資訊 -->
      <div v-if="isPersonalInfo" class="personalInfo-container">
        <div class="fixed-container">
          <div class="scrollable-block">
            <table v-if="group3.length > 0" class="table table-striped">
              <thead>
                <tr>
                  <th>名稱</th>
                  <th>群組代碼</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group_member in group3" :key="group_member.id">
                  <td>{{ group_member.group_name }}</td>
                  <td>{{ group_member.group_code }}</td>
                  <td>
                    <button class="delete" @click="joingroup(group_member.group_id)">成員資訊</button>
                    <button class="delete" @click="newgroupcategory(group_member.group_id)">新增類別</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-else-if="loading" class="loading">載入中...</div>
            <div v-else class="account-area-placeholder">
              <p>暫無資料</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script>
import Swal from 'sweetalert2';
import dayjs from 'dayjs'; 

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
      isPersonalInfo:false,
      member:[],
      group_category:[],
      currentYearMonth: dayjs().format('YYYY-MM'),
      loading: true,
      personal_id: '',
      group: [],
      group2: [],
      group3:[],
      inputOptions: {},
      selectedGroupId: null,
      group_account: [],
      payBackAccounts: [],
      payBackAccounts2: [],
      sidebarActive: false,
    };
  },
  methods: {
    markAsPaid(index) {
      Swal.fire({
        title: '確認歸還?',
        text: "您確定要將此條目標記為已歸還嗎?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '是的, 標記!',
        cancelButtonText: '取消'
      }).then((result) => {
        if (result.isConfirmed) {
          const apiUrl = `${this.$apiUrl}/api/mark_as_paid/`;
          this.$axios.post(apiUrl, { return_id: this.payBackAccounts[index].return_id })
            .then(response => {
              if (response.data.success) {
                this.payBackAccounts[index].return_flag = 1; // 更新本地状态
                Swal.fire(
                  '已標記!',
                  '該條目已標記為已歸還.',
                  'success'
                );
              } else {
                Swal.fire(
                  '錯誤!',
                  '標記過程中出錯，請稍後再試.',
                  'error'
                );
              }
            })
            .catch(error => {
              console.error('Error marking as paid:', error);
              Swal.fire(
                '錯誤!',
                '標記過程中出錯，請稍後再試.',
                'error'
              );
            });
        }
      });
    },
    toggleSidebar() {
      this.sidebarActive = !this.sidebarActive;
    },
    handleOutsideClick(e) {
      const sidebar = this.$refs.sidebar;
      const sidebarButton = document.getElementById('sidebarCollapse');
      if (!sidebar.contains(e.target) && !sidebarButton.contains(e.target) && this.sidebarActive) {
        this.sidebarActive = false;
      }
    },
    showPersonalExpense() {
      this.isPersonalExpense = true;
      this.isGroupExpense = false;
      this.isAllExpense = false;
      this.isPayBack = false;
      this.isPersonalInfo = false;
      this.toggleSidebar();
    },
    showGroupExpense() {    
      this.isPersonalExpense = false;
      this.isGroupExpense = true;
      this.isAllExpense = false;
      this.isPayBack = false;
      this.isPersonalInfo = false;
      this.toggleSidebar();
    },
    showPayBack() {
      this.isPersonalExpense = false;
      this.isGroupExpense = false;
      this.isAllExpense = false;
      this.isPayBack = true;
      this.isPersonalInfo = false;
      this.fetchPayBack();
      this.toggleSidebar();
    },
    isInfo(){
      this.isPersonalExpense = false;
      this.isGroupExpense = false;
      this.isAllExpense = false;
      this.isPayBack = false;
      this.isPersonalInfo = true;
      this.fetchGroup();
      this.toggleSidebar()
    },
    prevMonth() {
      const newDate = dayjs(this.currentYearMonth).subtract(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
    },
    nextMonth() {
      const newDate = dayjs(this.currentYearMonth).add(1, 'month');
      this.currentYearMonth = newDate.format('YYYY-MM');
    },
    

    navigateToOverview() {
      this.$router.push({ name: 'liff_account_overview' });
    },

    //群組記帳
    groupAccounting() {
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
          showCancelButton:true,
          confirmButtonText: "送出",
          inputPlaceholder: "選擇一個帳本",
          allowOutsideClick: false,
          cancelButtonText:'取消',
          inputValidator: (value) => {
            if (!value) {
              return "請選擇帳本";
            }
          }
        }).then((result) => {
          if (result.value === null) {
            return;
          }
          if (result.isConfirmed) {
            Swal.fire({
              title: "群組帳目記帳",
              inputLabel:"輸入記帳資訊ex:項目地點金額",
              input: "text",
              showCancelButton:true,
              confirmButtonText: "送出",
              inputPlaceholder: "請輸入",
              cancelButtonText:'取消',
              allowOutsideClick: false,
              inputValidator: (value2) => {
                if (!value2) {
                  return "請輸入資訊!";
                }
              }
            }).then((result2) => {
              if (result2.value) {
                const data = result2.value;
                const apiUrl = `${this.$apiUrl}/api/get_group_account_info_classification/`;
                this.$axios.post(apiUrl, {user_input:data,group_id : result.value})
                .then(response => {
                  const classdata = response.data.temp;
                  if (response.data.temp === '錯誤'){
                    Swal.fire({
                        text: "請檢查輸入的記帳內容!",
                        icon: "warning"
                    });
                  }
                  else{
                    let data2 = ''
                    Swal.fire({
                      title: "分帳人資訊",
                      inputLabel:"1.按下全部人為全部人平均分攤金額\n2.可以輸入除外誰以外都要分帳\n3.若不用分帳直接按送出",
                      html: `
                          <button id="allPeopleButton" class="swal2-styled" style="background-color:#FFC299; ; color: black; padding: 10px 20px; font-size: 16px">全部人</button>
                          `,
                      input: "text",
                      confirmButtonText: "送出",
                      allowOutsideClick: false,
                      inputPlaceholder: "請輸入",
                      allowOutsideClick: false,
                      preConfirm: () => {
                        if(data2 === ''){
                          data2 = Swal.getInput().value;
                        }
                        return data2;
                      }
                    }).then((result3) => {
                      data2 = result3.value
                      Swal.fire({
                        title: '請稍候...',
                        allowOutsideClick: false,
                        didOpen: () => {
                          Swal.showLoading();
                        }
                      });
                      const apiUrl = `${this.$apiUrl}/api/get_group_account_info/`;
                      this.$axios.post(apiUrl, {user_input2:data2,group_id : result.value})
                        .then(response => {
                          Swal.close();
                          if(response.data.temp2 ==='錯誤'){
                           Swal.fire({
                              text: "請檢查輸入的記帳內容!",
                              icon: "warning"
                           });
                          }
                          else {
                            this.$router.push({ name: 'liff_group_form', params: { formData: classdata,formData2:response.data.temp2 } });
                          }
                        })
                        .catch(error => {
                          Swal.close();
                          console.error('Error:', error);
                        })
                  })
                  document.getElementById('allPeopleButton').addEventListener('click', () => {
                    data2 = '全部人';
                    Swal.getInput().value = '全部人';
                  })
                }
                });
              } 
          });
        }
      });
    })
        .catch(error => {
          console.error('Error:', error);
        });
    },

    voiceTextAccounting() {
      Swal.fire({
        title: "個人記帳",
        input: "text",
        showCancelButton:true,
        confirmButtonText: "送出",
        inputPlaceholder: "請輸入",
        cancelButtonText:'取消',
        allowOutsideClick: false,
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
        showCancelButton:true,
        confirmButtonText: "加入",
        inputPlaceholder: "請輸入",
        cancelButtonText:'取消',
        allowOutsideClick: false,
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
                }).then(() => {
                  this.fetchGroup()
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
        showCancelButton:true,
        inputPlaceholder: "請輸入",
        cancelButtonText:'取消',
        allowOutsideClick: false,
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
        }
      });
    },
    creategroup_axios(groupname) {
      const apiUrl = `${this.$apiUrl}/api/creategroup/`;
      this.$axios.post(apiUrl, { GroupName: groupname, userId: this.$root.$userId })
        .then(response => {
          console.log(response);
          if(response.data==='成功接收數據'){
              Swal.fire({
              title: "創建成功!",
              icon: "success"
            }).then(() => {
              this.fetchGroup()
            });
          }
        })
        .catch(error => {
          console.error(error);
        })
        .finally(() => {
          this.loading = false;
        });
    },

    fetchPayBack() {
      const apiUrl = `${this.$apiUrl}/api/get_payback/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id ,user_name:this.$root.$userName})
        .then(response => {
          this.payBackAccounts = response.data.payer_payback_list;
          this.payBackAccounts2 = response.data.receiver_payback_list;
          console.log(response.data)
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
          console.log(response.data.groups);
          this.group = response.data.groups;
          this.group3 = response.data.groups;
        })
        .catch(error => {
          console.error(error);
        });
    },
    fetchGroupAccount() {
      const apiUrl = `${this.$apiUrl}/api/get_group_account/`;
      this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
        .then(response => {
          this.group_account= response.data.group_account
          console.log(response.data);
        })
        .catch(error => {
          console.error(error);
        });
    },
    checkUserId() {
      if (this.$root.$userId === null || this.$root.$personal_id === null) {
        setTimeout(() => this.checkUserId(), 500);
      } else {
        Promise.all([this.fetchAccounts(), this.fetchGroup(),this.fetchGroupAccount()])
          .then(() => {
            this.loading = false;
          })
          .catch(error => {
            console.error("An error occurred while fetching data:", error);
            this.loading = false;
          });
      }
    },
    deleteAccount(id) {
      Swal.fire({
        title:'確認刪除',
        icon:'warning',
        showCancelButton:true,
        confirmButtonText:'確定',
        allowOutsideClick: false,
        cancelButtonText:'取消'
      }).then((result) => {
        if(result.isConfirmed){
          const apiUrl = `${this.$apiUrl}/api/delete_personal/`;
          const requestdata={personal_id:this.$root.$personal_id,account_id:id}
          this.$axios.post(apiUrl,requestdata)
          .then(response => {
            Swal.fire({
                title: "刪除成功!",
                icon: "success"
            })
            this.fetchAccounts()
          }).catch(error => {
              console.error(error);
            });
        }
      })
    },
    //拉人
    joingroup(group_id){
      const apiUrl = `${this.$apiUrl}/api/show_member/`;
      this.$axios.post(apiUrl, {groupId:group_id })
        .then(response => {
          this.member = response.data;
          const membersTable = `
          <style>
            .table-wrapper {
              max-height: 400px; /* 調整這個高度以適應你的需求 */
              -webkit-overflow-scrolling: touch; /* 為移動設備啟用慣性滾動 */
            }
            .members-table {
              overflow-y: scroll;
              width: 100%;
              border-collapse: collapse;
            }
            .members-table th, .members-table td {
              border: 1px solid #ddd;
              padding: 8px;
            }
            .members-table th {
              background-color: #f2f2f2;
              position: sticky;
              top: 0; /* 保持標題行固定在頂部 */
            }
          </style>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
          <div class="table-wrapper">
            <table class="table members-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>名字</th>
                </tr>
              </thead>
              <tbody>
                ${this.member.map(member => `
                  <tr>
                    <td>${member.personal_id}</td>
                    <td>${member.personal_name}</td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>`;
          Swal.fire({
            title: '成員列表',
            html: membersTable,
            showCancelButton:true,
            confirmButtonText:'新增',
            allowOutsideClick: false,
            showDenyButton: true,
            denyButtonText: '退出群組',
            cancelButtonText:'取消'
          }).then((result) => {
            if(result.isConfirmed){
              Swal.fire({
                title:'輸入加入群組者的id',
                input:'text',
                showCancelButton:true,
                confirmButtonText: '新增',
                allowOutsideClick: false,
                cancelButtonText:'取消',
                inputPlaceholder: "請輸入",
                inputValidator: (value) => {
                  if (!value) {
                    return "請輸入!";
                  }
                }
              }).then(result => {
                if(result.value){
                  const temp =  result.value
                  const apiUrl = `${this.$apiUrl}/api/join_group/`;
                  const requestdata={input:temp,groupID:group_id}
                  this.$axios.post(apiUrl,requestdata)
                  .then(response => {
                    if (response.data ==='成功加入群組'){
                      Swal.fire({
                          title: "加入成功!",
                          icon: "success"
                      })
                    }else if(response.data === '此使用者已加入該群組'){
                      Swal.fire({
                          title: "此使用者已加入該群組!",
                          icon: "warning"
                      })
                    }else if(response.data ==='查無此使用者，請重新輸入'){
                      Swal.fire({
                          title: "查無此使用者，請重新輸入!",
                          icon: "warning"
                      })
                    }
                  }).catch(error => {
                      console.error(error);
                    });
                }
              })
            }
            else if(result.isDenied){
              Swal.fire({
                title: "確認退出？",
                icon: "warning",
                confirmButtonText: '確認',
                showCancelButton:true,
                cancelButtonText:'取消',
              }).then((result) => {
                if (result.isConfirmed){
                  const apiUrl = `${this.$apiUrl}/api/exit_group/`;
                  const requestdata={personal_id:this.$root.$personal_id,groupID:group_id}
                  this.$axios.post(apiUrl,requestdata)
                  .then(response => {
                    if (response.data==='Yes'){
                      Swal.fire({
                        title: "刪除成功",
                        icon: "success",
                        confirmButtonText: '確認',
                      })
                      this.fetchGroup()
                    }else if(response.data === 'No'){
                      Swal.fire({
                        title: "刪除失敗",
                        text:"群組中尚有成員未還清給您，或是您有尚未還錢給其他人，因此無法執行退出操作",
                        icon: "warning",
                        confirmButtonText: '確認',
                      })
                    }
                  })
                }
              })
            }
         });
        })
    },
    //新增類別
    newgroupcategory(group_id) {
      const apiUrl = `${this.$apiUrl}/api/show_group_category/`;
      this.$axios.post(apiUrl, { groupId: group_id })
        .then(response => {
          this.group_category = response.data;
          const categoryTable = `
          <style>
            .table-wrapper {
              max-height: 400px; /* 調整這個高度以適應你的需求 */
              -webkit-overflow-scrolling: touch; /* 為移動設備啟用慣性滾動 */
            }
            .members-table {
              overflow-y: scroll;
              width: 100%;
              border-collapse: collapse;
            }
            .members-table th, .members-table td {
              border: 1px solid #ddd;
              padding: 8px;
            }
            .members-table th {
              background-color: #f2f2f2;
              position: sticky;
              top: 0; /* 保持標題行固定在頂部 */
            }
          </style>
          <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
          <div class="table-wrapper">
            <table class="table members-table">
              <thead>
                <tr>
                  <th>交易類型</th>
                  <th>類別名稱</th>
                </tr>
              </thead>
              <tbody>
                ${this.group_category.map(category => `
                  <tr>
                    <td>${category.transaction_type}</td>
                    <td>${category.category_name}</td>
                  </tr>`).join('')}
              </tbody>
            </table>
          </div>`;
          Swal.fire({
            title: '類別列表',
            html: categoryTable,
            showCancelButton:true,
            confirmButtonText:'新增',
            cancelButtonText:'取消'
          }).then((result) => {
            if (result.isConfirmed) {
              Swal.fire({
                title: "<small>新增類別</small>",
                html: `
                    <div style="text-align: left; font-size: 14px;">
                        <label for="transactionType" style="display: block; margin-bottom: 5px; font-size:16px; font-weight:bold">交易類型</label>
                        <select name="transactionType" id="transactionType" style="width: 100%; padding: 8px; box-sizing: border-box; margin-bottom: 10px;">
                          <option value="">選擇交易類型</option>
                          <option value="收入">收入</option>
                          <option value="支出">支出</option>
                        </select>
                        <label for="categoryName" style="display: block; margin-bottom: 5px; font-size:16px; font-weight:bold">類別名稱</label>
                        <input type="text" name="categoryName" id="categoryName" style="width: 100%; padding: 8px; box-sizing: border-box; margin-bottom: 10px;">
                    </div>
                `,
                showCancelButton:true,
                confirmButtonText:'確定',
                cancelButtonText:'取消',
                preConfirm: () => {
                  const transactionType = Swal.getPopup().querySelector('#transactionType').value;
                  const categoryName = Swal.getPopup().querySelector('#categoryName').value;
                  if (!transactionType || !categoryName) {
                      Swal.showValidationMessage('請填寫交易類型和類別名稱');
                      return false; 
                  }
                  return { transactionType: transactionType, categoryName: categoryName };
                }
              }).then((result) => {
                if (result.isConfirmed) {
                  const apiUrl = `${this.$apiUrl}/api/add_group_category/`;
                  const requestData = {
                    transactionType: result.value.transactionType,
                    categoryName: result.value.categoryName,
                    groupID: group_id
                  };
                  this.$axios.post(apiUrl, requestData)
                    .then(response => {
                      if(response.data === "成功"){
                        Swal.fire({
                          title: "新增成功!",
                          icon: "success"
                        })
                      }else if(response.data==='已有該類別'){
                        Swal.fire({
                          title: "已有該類別!",
                          icon: "warning"
                        })
                      }
                    })
                    .catch(error => {
                      console.error(error);
                    });
                }
              });
            }
          });
        }).catch(error => {
          console.error(error);
        });
    },

    deletegroupAccount(account,group) {
      Swal.fire({
        title:'刪除',
        icon:'warning',
        text: "刪除後分帳與還錢資訊也連動刪除?",
        showCancelButton:true,
        confirmButtonText:'確定',
        allowOutsideClick: false,
        cancelButtonText:'取消'
      }).then((result) => {
        if(result.isConfirmed){
          const apiUrl = `${this.$apiUrl}/api/delete_group/`;
          const requestdata={group_id:group,account_id:account}
          this.$axios.post(apiUrl,requestdata)
          .then(response => {
            Swal.fire({
                title: "刪除成功!",
                icon: "success"
            })
            this.fetchGroupAccount()
            this.selectedGroupId = group
          }).catch(error => {
              console.error(error);
            });
        }
      })
    },
  },
  mounted() {
    this.checkUserId();
    document.addEventListener('click', this.handleOutsideClick);
  },
  beforeDestroy() {
    document.removeEventListener('click', this.handleOutsideClick);
  },
  watch: {
    selectedGroupId(newValue) {
      this.selectedGroupId = newValue; 
    }
  },
  computed: {
    filteredAccounts() {
      let filteredAccounts = this.accounts;
      filteredAccounts= filteredAccounts.filter(account => account.flag===1)
      filteredAccounts= filteredAccounts.filter(account => account.account_date.slice(0, 7)===this.currentYearMonth)
      let filtereGroupdAccounts = this.group_account;
      filtereGroupdAccounts= filtereGroupdAccounts.filter(group_account => group_account.flag===1)
      filtereGroupdAccounts= filtereGroupdAccounts.filter(group_account => group_account.group_id===this.selectedGroupId)
      filtereGroupdAccounts= filtereGroupdAccounts.filter(group_account => group_account.account_date.slice(0, 7)===this.currentYearMonth)
      if (this.isPersonalExpense) {
        return filteredAccounts;
      } else if (this.isGroupExpense) {
        return filtereGroupdAccounts;
      }
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
.delete{
  padding: 6px 10px;
  background-color: #ffc107; 
  color: black;
  border-radius: 6px;
}
.delete_group{
  padding: 6px 10px;
  background-color: red; 
  color: white;
  border-radius: 6px;
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
.profile-picture {
  width: 40px; /* Adjust the width as needed */
  height: 40px; /* Adjust the height as needed */
  border-radius: 50%; /* Make it a circle */
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
.table .btn {
  width: 100%;
  padding: 6px 12px;
}

.float-right {
  float: right;
}

</style>
