<template>
    
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Class List</h3>
      <button class="btn btn-primary" @click="goToAddClass">+ Add New Class</button>
    </div>

    <table class="table table-hover table-bordered align-middle">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>Class Name</th>
          <th>Section</th>
          <th>Session Name</th>
          <th>Timetable</th>
          <th>Actions</th>
          <th>Deleted By</th>
        </tr>
      </thead>
      <tbody>
        <tr 
          v-for="cls in classes" 
          :key="cls.id"
          :class="{'table-secondary':!cls.session?.is_active,'table-danger':cls.deleted_at}"
        >
          <td>{{ cls.id }}</td>
          <td>
            <a href="#" @click.prevent="cls.session.is_active && !cls.deleted_at &&handleClassClick(cls)"
            >
              {{ cls.name }}
            </a>
          </td>
          <td>{{ cls.section }}</td>
          <td>{{ cls.session?.name || 'N/A' }}</td>
          <td><button class="btn btn-info "
            @click="$router.push(`/timetable/${cls.id}`)"
            :disabled="!cls.session?.is_active"
            >Show</button></td>

          <td>
            <div class="dropdown">
                <button 
                  class="btn btn-secondary btn-sm dropdown-toggle" 
                  type="button" 
                  id="dropdownMenuButton"
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                  :disabled="!cls.session?.is_active"
                >
                 Actions
                </button>
             <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
            <li>
            <button 
            class="dropdown-item text-warning" 
            @click="updateClass(cls)"
            :disabled="!cls.session?.is_active"
            v-if="!cls.deleted_at">
              Update
            </button>
            </li>

            <li>
            <button 
            class="dropdown-item text-danger" @click="deleteClass(cls.id)"
            :disabled="!cls.session?.is_active"
            v-if="!cls.deleted_at">
              Delete
            </button>
            </li>

             <li>
            <button 
            class="dropdown-item text-danger" @click="restoreClass(cls.id)"
            :disabled="!cls.session?.is_active"
            v-if="cls.deleted_at">
              Restore
            </button>
            </li>
             </ul>
            </div>
          </td>
          <td v-if="cls.deleted_at">{{ cls.user.phone_number}}</td>
        </tr>
        <tr v-if="classes.length === 0">
          <td colspan="5" class="text-center">No classes found</td>
        </tr>
      </tbody>
    </table>

    <!-- Response messages -->
    <div v-if="responseMessage" 
         :class="['alert', responseSuccess ? 'alert-success' : 'alert-danger']">
      {{ responseMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const classes = ref([])
const responseMessage = ref('')
const responseSuccess = ref(false)
const router = useRouter()

// Fetch all classes
const fetchClasses = async () => {
  const token = localStorage.getItem('token')
  try {
    const res = await fetch('/api/get_classes', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    // credentials:'include'
    })
    
    const data = await res.json()
    console.log(data)
    
    if (res.ok) {
      classes.value = data || [] // adjust if API returns differently
    } else {
      responseMessage.value = data.message || 'Failed to fetch classes'
      responseSuccess.value = false
    }
  } catch (error) {
    console.error(error)
    responseMessage.value = 'Error fetching classes'
    responseSuccess.value = false
  }
}

// Click class name
const handleClassClick = (cls) => {
  alert(`You clicked class: ${cls.name}`)
  // You can route to details page:
  // router.push(`/class/${cls.id}`)
}

// Navigate to add new class form
const goToAddClass = () => {
  router.push('/add-class')
}

// Update class
const updateClass = (cls) => {
  router.push(`/update-class/${cls.id}`)
}

// Delete class
const deleteClass = async (id) => {
  if (!confirm('Are you sure you want to delete this class?')) return

  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`/api/delete_class/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await res.json()
    responseMessage.value = data.message || 'Deleted successfully'
    responseSuccess.value = res.ok

    if (res.ok) {
      // classes.value = classes.value.filter(c => c.id !== id)
      fetchClasses()
    }
  } catch (error) {
    console.error(error)
    responseMessage.value = 'Error deleting class'
    responseSuccess.value = false
  }
}
const restoreClass = async (id) =>{
  if (!confirm("Are you sure want to restore this Class?"))
  return

  const token = localStorage.getItem('token')
  try {
    const res = await fetch(`/api/restore_class/${id}`,{
      method:'PATCH',
      headers:{'Authorization':`Bearer ${token}`}
    })

    const data = await res.json()
    responseMessage.value = data.message || 'Deleted successfully'
    responseSuccess.value = res.ok
    fetchClasses()

  }
  catch(error){
    console.error(error)
    responseMessage.value = 'Error restoring class'
    responseSuccess.value = false
  }
  }


onMounted(() => {
  fetchClasses()
})
</script>
