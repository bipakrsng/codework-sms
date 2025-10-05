import { createApp } from 'vue'
import App from './App.vue'
import router from './router/router'

// Styles
import 'bootstrap/dist/css/bootstrap.min.css'
import '@/assets/vendor/bootstrap-icons/bootstrap-icons.css'
import '@/assets/css/style.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'



// Global components
import HeaDer from '@/components/Header.vue'
import FooTer from '@/components/Footer.vue'

// Store
import { createPinia } from 'pinia'
import { useUserStore } from './store/userStore'
import { decodeToken } from '@/utils/auth'

// Create Vue app
const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

app.component('hea-der', HeaDer)
app.component('foo-ter', FooTer)
app.use(router)

const userStore = useUserStore()
const token = decodeToken()
if (token) {
  userStore.setUserFromToken(token)
}

//  Mount only once (pick one container, say #app)
app.mount('#main')

// // Function to toggle which container is visible
// const toggleMounts = (toPath) => {
//   const appDiv = document.getElementById('app')
//   const mainDiv = document.getElementById('main')

//   if (!appDiv || !mainDiv) return

//   if (toPath === '/' || toPath === '/login') {
//     appDiv.style.display = 'block'
//     mainDiv.style.display = 'none'
//   } else {
//     appDiv.style.display = 'none'
//     mainDiv.style.display = 'block'
//   }
// }

// // Run once at startup
// toggleMounts(router.currentRoute.value.path)

// // Update on route change
// router.beforeEach((to, from, next) => {
//   toggleMounts(to.path)
//   next()
// })
