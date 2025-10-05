<template>
  <div class="container mt-3">
    <div class="card shadow-lg border-0 rounded-3">
      <div class="card-header bg-primary text-white text-center ">
        <h5 class="mb-0"><i class="bi bi-person-plus me-0"></i> Add New Teacher</h5>
      </div>

      <div class="card-body p-4">
        <form @submit.prevent="createTeacher">
          <!-- USER DETAILS -->
          
          

          <!-- TEACHER DETAILS -->
          <h5 class="text-secondary border-bottom pb-2 mb-3 mt-4">
            <i class="bi bi-person-badge me-2"></i> Teacher Information
          </h5>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">First Name <span class="text-danger">*</span></label>
              <input type="text" v-model="form.first_name" class="form-control" required placeholder="Enter first name" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Last Name <span class="text-danger">*</span></label>
              <input type="text" v-model="form.last_name" class="form-control" required placeholder="Enter last name" />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Teacher Phone <span class="text-danger">*</span></label>
              <input type="tel" v-model="form.teacher_phone" class="form-control" required placeholder="Enter teacher phone" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Teacher Email <span class="text-danger">*</span></label>
              <input type="email" v-model="form.teacher_email" class="form-control" required placeholder="Enter teacher email" />
            </div>
          </div>

          <!-- SUBJECTS -->
            <div class="mb-3">
            <label class="form-label">Select Subjects <span class="text-danger">*</span></label>
            
            <div class="row">
              <div 
                v-for="sub in subjects" 
                :key="sub.id" 
                class="col-md-6 mb-2"
              >
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="'subject-' + sub.id"
                    :value="sub.id"
                    v-model="form.subject_id"
                  />
                  <label class="form-check-label" :for="'subject-' + sub.id">
                    {{ sub.name }} ({{ sub.code }})
                  </label>
                </div>
              </div>
            </div>

            <small class="text-muted">You can select multiple subjects</small>
          </div>

          <!-- BUTTONS -->
          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="button" @click="resetForm" class="btn btn-outline-secondary px-4">
              <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
            </button>
            <button type="submit" class="btn btn-success px-4" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i class="bi bi-check2-circle me-1"></i> Create Teacher
            </button>
          </div>
        </form>
      </div>
    
    <div v-if="message"
    class="alert alert-danger text-center mx-3">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import {useRouter} from 'vue-router'

const router = useRouter()


const message = ref('')

const form = ref({
  email: "",
  password: "",
  phone_number: "",
  first_name: "",
  last_name: "",
  subject_id: [],
  teacher_phone: "",
  teacher_email: "",
})

const subjects = ref([])
const loading = ref(false)

// Fetch subjects from backend
const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem("token")
    const res = await fetch("/api/get_subjects", {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error("Failed to load subjects")
    subjects.value = await res.json()
  } catch (e) {
    alert(e.message)
  }
}

onMounted(fetchSubjects)

// Create Teacher API
const createTeacher = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem("token")

    const res = await fetch("/api/create_teacher", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(form.value),
    })

    const data = await res.json()
    if (res.ok) {
      message.value = 'Teacher created Successfully!!!'
      router.push("/getTeacher")
    }
    else{
      message.value =  data.message ||'Failed to Create Teacher'
  }

    
    resetForm()
  } catch (e) {
    alert(e.message)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    email: "",
    password: "",
    phone_number: "",
    first_name: "",
    last_name: "",
    subject_id: [],
    teacher_phone: "",
    teacher_email: "",
  }
}
</script>
