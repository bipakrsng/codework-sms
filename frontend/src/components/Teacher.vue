<template>
  
  <div class="container mt-4">
    <h3>Teacher List</h3>
    <button class="btn btn-primary" @click="$router.push('/createTeacher')">Add Teacher</button>
    
    <table class="table table-bordered table-hover align-middle mt-3">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>First Name</th>
          <th>Last Name</th>
          <th>Phone</th>
          <th>Email</th>
          
          <th>Subjects</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="teacher in teachers" :key="teacher.id"
        :class="teacher.deleted_at?'table-danger':'table-secondary'">
          <td>{{ teacher.id }}</td>
          <td>{{ teacher.first_name }}</td>
          <td>{{ teacher.last_name }}</td>
          <td>{{ teacher.phone }}</td>
          <td>{{ teacher.email }}</td>
          
          <td>
            <ul class="mb-0">
              <li v-for="sub in teacher.subjects" :key="sub.id">
                {{ sub.name }} ({{ sub.code }})
              </li>
            </ul>
          </td>
          <td>
            <div class="dropdown">
              <button 
              class="btn btn-sm btn-secondary dropdown-toggle" 
                type="button" 
                data-bs-toggle="dropdown" 
                aria-expanded="false">
                Actions
    </button>
          <ul class="dropdown-menu">
        <li>
          <button 
            class="dropdown-item text-warning" 
            @click="editTeacher(teacher)"
            v-if="!teacher.deleted_at">
            <i class="bi bi-pencil-square me-2"></i> Update
          </button>
        </li>

        <li>
          <button 
            class="dropdown-item text-danger" 
            @click="deleteTeacher(teacher.id)"
            v-if="!teacher.deleted_at">
            <i class="bi bi-trash me-2"></i> Delete
          </button>
        </li>

        <li>
          <button 
            class="dropdown-item text-warning" 
            @click="restoreTeacher(teacher.id)"
            v-if="teacher.deleted_at">
            <i class="bi bi-pencil-square me-2"></i> Restore
          </button>
        </li>
      </ul>

  </div>
</td>

        </tr>
        <tr v-if="teachers.length === 0">
          <td colspan="8" class="text-center">No teachers found.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const teachers = ref([])

// Fetch teachers from API
const fetchTeachers = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/get_teachers', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch teachers')
    const data = await res.json()
    teachers.value = data
    console.log(data)
  } catch (e) {
    alert(e.message)
  }
}

onMounted(() => {
  fetchTeachers()
})

// Update teacher
const editTeacher = (teacher) => {
  router.push(`/updateTeacher/${teacher.id}`)
}

// Delete teacher
const deleteTeacher = async (id) => {
  if (!confirm('Are you sure you want to delete this teacher?')) return
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/delete_teacher/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message || 'Failed to delete teacher')
    
    fetchTeachers()
  } catch (e) {
    alert(e.message)
  }
}

const restoreTeacher = async (id) => {
  if (!confirm('Are you sure you want to restore this teacher?')) return
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/restore_teachers/${id}`, {
      method: 'PATCH',
      headers: { Authorization: `Bearer ${token}` }
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message || 'Failed to delete teacher')
    
    fetchTeachers()
  } catch (e) {
    alert(e.message)
  }
}
</script>
