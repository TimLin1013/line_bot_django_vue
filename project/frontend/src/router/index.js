import Vue from 'vue'
import Router from 'vue-router'
import liff_search from '@/components/liff_search'
import liff_keep from '@/components/liff_keep'
import liff_personal from '@/components/liff_personal_form'
import liff_account_overview from '@/components/liff_account_overview.vue'
import liff_group_form from '@/components/liff_group_form.vue'
import liff_personal_unfinish from '@/components/liff_personal_unfinish.vue'
import liff_group_unfinish from '@/components/liff_group_unfinish.vue'
Vue.use(Router)

  export default new Router({
    routes: [
      {
        path: '/:queryParam', 
        name: 'liff_search_with_query',
        component: liff_search,
        props: true 
      },
      {
        path: '/',
        name: 'liff_search',
        component: liff_search,
        props: true 
      },
      {
        path: '/keep',
        name: 'liff_keep',
        component: liff_keep,
        props: true
      },
      {
        path: '/personal_form',
        name: 'liff_personal_form',
        component: liff_personal,
        props: true
      },
      {
        path: '/account_overview',
        name: 'liff_account_overview',
        component: liff_account_overview,
        props: true
      },
      {
        path: '/group_form',
        name: 'liff_group_form',
        component: liff_group_form,
        props: true
      },
      {
        path: '/personal_unfinish',
        name: 'liff_personal_unfinish',
        component: liff_personal_unfinish,
        props: true
      },
      {
        path: '/group_unfinish',
        name: 'liff_group_unfinish',
        component: liff_group_unfinish,
        props: true
      },
    ]
    
  })