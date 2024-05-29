<template>
  <div id="demo">
    <calendar @change="onChange"/>
    <inlineCalendar @change="onChange"/>

    <div class="fixed-container">
      <div class="btn-group">
        <button :class="{ active: isPersonalExpense }" @click="showPersonalExpense">
          個人花費
        </button>
        <button :class="{ active: !isPersonalExpense }" @click="showGroupExpense">
          群組花費
        </button>
      </div>

      <div class="scrollable-block">
        <table v-if="selectedAccounts.length > 0" class="account-area">
          <thead>
            <tr>
              <th>項目</th>
              <th>日期</th>
              <th>金額</th>
              <th>類別</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(account, index) in selectedAccounts" :key="index">
              <td>{{ account.item }}</td>
              <td>{{ account.account_date }}</td>
              <td>{{ account.payment }}</td>
              <td>{{ account.category_name }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else class="account-area-placeholder"> 
          <h2>當天花費：</h2>
          <p>暫無資料</p>
        </div>
      </div>
    </div>
    <button class="keep-button" @click="navigateToKeep">記帳</button>
  </div>
</template>

<script>
import dayjs from 'dayjs';

export default {
  data() {
    return {
      selectedDate: '',
      accounts: [],
      isPersonalExpense: true
    };
  },
  methods: {
    onChange(date) {
      const formattedDate = dayjs(date).format('YYYY-MM-DD');
      this.selectedDate = formattedDate;

    },
    fetchAccounts() {
      const apiUrl = `${this.$apiUrl}/api/get_personal_account/`;
      console.log(apiUrl);

      this.$axios.post(apiUrl, { userId: this.$root.$userId })
        .then(response => {
          this.accounts = response.data.accounts;
        })
        .catch(error => {
          console.error(error);
        });
    },
    showPersonalExpense() {
      this.isPersonalExpense = true;
    },
    showGroupExpense() {
      this.isPersonalExpense = false;
    },
    navigateToKeep() {
      this.$router.push({ name: 'liff_keep' });
    }
  },
  watch: {
    'this.$root.$userId': function(newVal) {
      if (newVal) {
        this.fetchAccounts();
      }
    }
  },
  computed: {
    selectedAccounts() {
      return this.accounts.filter(account => dayjs(account.account_date).isSame(this.selectedDate, 'day'));
    }
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
  margin-top: 60px;
}

.fixed-container {
  height: calc(300px); 
  overflow-y: auto;
}

.scrollable-block {
  max-height: 100%; 
}

.account-area {
  border: 2px solid blue; 
  padding: 10px; 
  margin: 0 auto; 
}

.account-area-placeholder {
  border: 2px solid blue;
  padding: 10px; 
  opacity: 0.5; 
}

.account-area table {
  width: 100%; 
  border-collapse: collapse; 
}

.account-area th,
.account-area td {
  border: 1px solid #ddd; 
  padding: 8px; 
}

.account-area th {
  background-color: #f2f2f2;
}

.account-area tr:nth-child(even) {
  background-color: #f2f2f2; 
}

.btn-group {
  margin-bottom: 10px;
}

.btn-group button {
  margin-right: 10px;
  padding: 10px 20px; 
  border: none;
  cursor: pointer;
}

.btn-group button.active {
  background-color: #4CAF50;
  color: white;
}

.keep-button {
  margin-right: 10px;
  padding: 30px 40px;
  font-size: 20px;
  border: none;
  cursor: pointer;
}
</style>
