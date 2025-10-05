<template>
  
  <div class="container mt-5">
    <div class="card shadow rounded-4">
      <div class="card-header bg-primary text-white text-center fs-4">
        Add New Class
      </div>
      <div class="card-body">
        <form @submit.prevent="submitForm">
          <div class="mb-3">
            <label for="name" class="form-label">Class Name <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.name"
              type="text"
              class="form-control"
              id="name"
              required
              placeholder="e.g., 2A"
            />
          </div>

          <div class="mb-3">
            <label for="section" class="form-label">Section (optional)</label>
            <input
              v-model.trim="form.section"
              type="text"
              class="form-control"
              id="section"
              placeholder="e.g., A"
            />
          </div>

          <div class="mb-3">
            <label for="session_id" class="form-label">Session <span class="text-danger">*</span></label>
            <select
              v-model.number="form.session_id"
              class="form-control"
              id="session_id"
              required
            >
              <option value="" disabled>Select session</option>
              <option v-for="session in sessions.filter(s=>s.is_active)" :key="session.id" :value="session.id">
                {{ session.name }}
              </option>
            </select>
          </div>

          <div class="d-grid">
            <button class="btn btn-secondary" type="submit" @click="$router.back()">Cancel</button>
            <button type="submit" class="btn btn-success">Create Class</button>
          </div>
        </form>

        <div class="mt-3" v-if="responseMessage">
          <div :class="['alert', responseSuccess ? 'alert-success' : 'alert-danger']">
            {{ responseMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()


const form = ref({
  name: '',
  section: '',
  session_id: null
})

const sessions = ref([])
const responseMessage = ref('')
const responseSuccess = ref(false)

const token = localStorage.getItem('token')

async function fetchSessions() {
  try {
    const res = await fetch('/api/get_sessions', { // Adjust endpoint as needed
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!res.ok) throw new Error('Failed to fetch sessions')

    const data = await res.json()
    sessions.value = data || []  // Adjust if your response is different
  } catch (err) {
    console.error('Error fetching sessions:', err)
    responseMessage.value = 'Failed to load sessions. Please try again later.'
    responseSuccess.value = false
  }
}

onMounted(() => {
  fetchSessions()
})

const submitForm = async () => {
  const payload = {
    name: form.value.name.toLowerCase(),
    section: form.value.section ? form.value.section.toUpperCase() : 'A',
    session_id: form.value.session_id
  }

  try {
    const res = await fetch('/api/create_class', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    const data = await res.json()
    responseSuccess.value = res.ok
    
    responseMessage.value = data.message || 'Something went wrong'

    if (res.ok) {
      form.value = {
        name: '',
        section: '',
        session_id: null
      },
      router.push('/getclasses')
    }
  } catch (error) {
    responseSuccess.value = false
    responseMessage.value = 'Server error. Please try again later.'
    console.error(error)
  }
}
</script>
