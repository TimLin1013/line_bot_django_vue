<template>
    <div id="overview">
        <div class="summary-box">
            <div class="summary-item">Total: {{ total }}</div>
            <div class="summary-item">Income: {{ income }}</div>
            <div class="summary-item">Expense: {{ expense }}</div>
        </div>
        <div class="chart-container">
            <div class="date-controls">
                <button @click="prevMonth" :disabled="loading">←</button>
                <span>{{ currentYearMonth }}</span>
                <button @click="nextMonth" :disabled="loading">→</button>
            </div>
            <div v-if="income !== 0 || expense !== 0" class="personal">個人</div>
            <div v-else class="no-data-message">無相關資料</div>
            <apexchart ref="sample" type="donut" height="230" :options="chartOptions" :series="series"></apexchart>
            <div class="summary-box2">
                <div class="summary-item2">Total: {{ total2 }}</div>
                <div class="summary-item2">Income: {{ income2 }}</div>
                <div class="summary-item2">Expense: {{ expense2 }}</div>
             </div>
            <div v-if="income2 !== 0 || expense2 !== 0" class="group">
                群組
                <select v-model="selectedGroup" @change="groupChanged" class="selectedGroup">
                    <option v-for="group in groups" :key="group.group_id" :value="group.group_id">{{ group.group_name }}</option>
                </select>
            </div>
            <div v-else class="no-data-message">
                無相關資料
                <select v-model="selectedGroup" @change="groupChanged" class="selectedGroup">
                    <option v-for="group in groups" :key="group.group_id" :value="group.group_id">{{ group.group_name }}</option>
                </select>
            </div>
            <div class="chart-spacing">
                <apexchart ref="sample2" type="donut" height="230" :options="anotherchart" :series="series2"></apexchart>
            </div>
        </div>
    </div>
</template>
<script>
   export default {
    name: 'OverviewChart',
    mounted(){
        this.personalreport()
        this.fetchGroup(); 
        this.groupreport();
    },
    data() {
        return {
            currentYearMonth: dayjs().format('YYYY-MM'),
            selectedDate: dayjs().toDate(),
            personal_id: '', 
            loading: true,
            income:0,
            expense:0 ,
            total:0,
            series: [],
            income2:0,
            expense2:0,
            total2:0,
            series2:[],
            groups: [], 
            selectedGroup: null, 
            chartOptions: {
                chart: {
                    height: 350,
                    type: 'donut',
                },
                labels: ['收入', '支出'], 
                colors: ['#FFD700', '#ADD8E6'],
                dataLabels: {
                    style: {
                        colors: ['#000000'] 
                    }
                },
            },
            anotherchart:{
                chart:{
                    height: 350,
                    type: 'donut',
                },
                labels: ['收入', '支出'], 
                colors: ['#FFD700', '#ADD8E6'],
                dataLabels: {
                    style: {
                        colors: ['#000000'] 
                    }
                },
            }
        };
    },
    methods:{
        personalreport(){
            const apiUrl = `${this.$apiUrl}/api/personal_report/`;
                this.loading = true; 
                this.$axios.post(apiUrl, {personal_id: this.$root.$personal_id ,date: this.currentYearMonth})
                .then(response => {
                    const responseData = JSON.parse(response.data);
                    this.income = responseData.income_total
                    this.expense = responseData.expense_total
                    this.total = this.income-this.expense
                    this.series = [this.income, this.expense];
                    this.updateChart();
                })
                .catch(error => {
                    console.error(error);
                })
                .finally(() => {
                    this.loading = false;
                    this.updateChart();
                })
        },
        fetchGroup() {
            const apiUrl = `${this.$apiUrl}/api/get_group/`;
                this.$axios.post(apiUrl, { personal_id: this.$root.$personal_id })
                .then(response => {
                    console.log(response);
                    this.groups = response.data.groups;
                    if (this.groups.length > 0) {
                        this.selectedGroup = this.groups[0].group_id;  // 預設選擇第一個群組
                        this.groupreport(this.selectedGroup)
                    }
                })
                .catch(error => {
                    console.error(error);
                })
                .finally(() => {  
                    this.loading = false;
                });
        },
        groupreport(group){
            const apiUrl = `${this.$apiUrl}/api/group_report/`;
                this.loading = true; 
                this.$axios.post(apiUrl, {date: this.currentYearMonth, group_id:group})
                .then(response => {
                    console.log(response)
                    const responseData = JSON.parse(response.data);
                    this.income2 = responseData.income_total
                    this.expense2 = responseData.expense_total
                    this.total2 = this.income2-this.expense2
                    this.series2 = [this.income2, this.expense2];
                    this.updateChart();
                })
                .catch(error => {
                    console.error(error);
                })
                .finally(() => {
                    this.loading = false;
                    this.updateChart();
                })
        },
        updateChart() {
            if (this.$refs.sample) {
                this.$refs.sample.updateSeries(this.series);
            }
            if(this.$refs.sample2){
                this.$refs.sample2.updateSeries(this.series2)
            }
        },
        prevMonth() {
            this.currentYearMonth = dayjs(this.currentYearMonth).subtract(1, 'month').format('YYYY-MM');
            this.personalreport(); 
            this.groupreport(this.selectedGroup);
        },
        nextMonth() {
            this.currentYearMonth = dayjs(this.currentYearMonth).add(1, 'month').format('YYYY-MM');
            this.personalreport(); 
            this.groupreport(this.selectedGroup);
        },
        groupChanged() {
            this.groupreport(this.selectedGroup);
        },
    }
};
</script>
<style>
#overview {
  margin: 20;
  padding: 0;
}
.summary-box {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 30px;
  display: flex;
  justify-content: space-between;
  position: fixed;
  width: calc(100% - 20px);
  height: 25px;
  top: 0;
}

.summary-item {
  font-size: 18px;
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  text-align: left; 
  font-weight: bold;
}
.summary-box2 {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 30px;
    display: flex;
    justify-content: space-between;
    width: calc(100% - 20px);
    height: 25px;
}

.summary-item2 {
    font-size: 18px;
    margin-bottom: 10px;
    text-align: left;
    font-weight: bold;
    flex: 1; 
}

body {
  margin: 0;
  padding: 0;
}
.chart-container {
    margin-bottom: 10px; 
}

.date-controls {
    margin-bottom: 10px; 
    font-size: 18px;
}
.personal {
    text-align: left; 
    font-size: 18px; 
    margin-left: 10px;
    font-weight: bold;
}
.group {
    text-align: left; 
    font-size: 18px; 
    margin-left: 10px;
    font-weight: bold;
    margin-top: 20px;
}
.selectedGroup {  
    font-size: 18px;   
    width: 150px; 
}
.chart-spacing {
    margin-top: 15px; 
}
</style>
