<template>
  <div id="app">
    <router-view :key="$route.fullPath"/>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      profile: {},
      msg: "", 
      
    };
  },
  beforeCreate() {
    if (window.liff) {
      window.liff.init({
        liffId: '2004983305-2LqXBLZr'
      }).then(() => {
        this.getProfile();
      }).catch((error) => {
        console.error('LIFF 初始化失敗', error);
      });
    } else {
      console.error('LIFF SDK 無法使用');
    }
  },
  methods: {

    getProfile() {
      if (window.liff.isLoggedIn()) {
        window.liff.getProfile().then((profile) => {
          this.profile = profile;
          this.$root.$userId = profile.userId;
          this.$root.$userName = profile.displayName;//6/2
          this.$root.$userPictureUrl = profile.pictureUrl;
          const apiUrl = `${this.$apiUrl}/api/get_personal_account/`;
            console.log(apiUrl);
            console.log(this.$root.$userId);
            this.$axios.post(apiUrl, { userId: this.$root.$userId,name: this.$root.$userName })
            .then(response => {
                console.log(response);
                this.$root.$personal_id = response.data.personal_id
                console.log(this.$root.$personal_id)
              })
            .catch(error => {
                console.error(error);
            })
            .finally(() => {
              this.loading = false;
            });
            }).catch((error) => {
              console.error('獲取Profile失敗', error);
            });
      } else {
        window.liff.login();
      }
    }
  }
};
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>