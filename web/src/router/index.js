import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../layouts/AppLayout.vue'),
    children: [
      { path: '', name: 'welcome', component: () => import('../views/WelcomeView.vue') },
      { path: 'db/:id', name: 'db-detail', component: () => import('../views/db/DatabaseDetailShell.vue') },
      { path: 'tasks', name: 'tasks', component: () => import('../views/db/TasksPage.vue') },
      { path: 'trash', name: 'trash', component: () => import('../views/TrashPage.vue') },
      { path: ':pathMatch(.*)*', redirect: '/' },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
