<template>
  <div class="container mt-4">
    <div class="card shadow rounded-4">
      <div class="card-header bg-primary text-white text-center fs-4">
        Update Class
      </div>
      <div class="card-body">
        <form @submit.prevent="updateClass">
          <div class="mb-3">
            <label for="name" class="form-label">Class Name <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.name"
              type="text"
              class="form-control"
              id="name"
              required
              
            />
          </div>

          <div class="mb-3">
            <label for="section" class="form-label">Section</label>
            <input
              v-model.trim="form.section"
              type="text"
              class="form-control"
              id="section"
              
            />
          </div>

          <div class="d-flex justify-content-end gap-2">
            <button type="button" class="btn btn-secondary" @click="$router.back()">Cancel</button>
            <button type="submit" class="btn btn-success" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm"></span>
              Save Changes
            </button>
          </div>
        </form>

        <div v-if="message" :class="['alert', success ? 'alert-success' : 'alert-danger', 'mt-3']">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const form = ref({
  name: '',
  section: ''
})

const message = ref('')
const success = ref(false)
const loading = ref(false)

const classId = route.params.id

const fetchClass = async () => {
  loading.value = true
  message.value = ''
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/get_class/${classId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (!res.ok) {
      throw new Error('Failed to fetch class data')
    }
    const data = await res.json()
    form.value.name = data.name || ''
    form.value.section = data.section || ''
  } catch (err) {
    message.value = err.message
    success.value = false
  } finally {
    loading.value = false
  }
}


const updateClass = async () => {
  loading.value = true
  message.value = ''
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/update_class/${classId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        name: form.value.name,
        section: form.value.section
      })
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message || 'Update failed')

    message.value = data.message || 'Class updated successfully'
    success.value = true

    
      router.push('/getclasses') // Adjust to your class list route
    
  } catch (err) {
    message.value = err.message
    success.value = false
  } finally {
    loading.value = false
  }
}



onMounted(() => {
  fetchClass()
  
})
</script>
