<template>
  <div class="container mt-5">
    <h2>{{ isUpdate ? "Update" : "Create" }} Timetable Entry</h2>

    <form @submit.prevent="submitTimetable">
      <!-- Class -->
      <div class="mb-3">
        <label class="form-label">Class</label>
        <select v-model="form.class_id" class="form-select" required>
          <option value="" disabled>Select Class</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }} - {{ cls.section }}
          </option>
        </select>
      </div>

      <!-- Subject -->
      <div class="mb-3">
        <label class="form-label">Subject</label>
        <select v-model="form.subject_id" class="form-select" required>
          <option value="" disabled>Select Subject</option>
          <option v-for="sub in subjects" :key="sub.id" :value="sub.id">
            {{ sub.name }} ({{ sub.code }})
          </option>
        </select>
      </div>

      <!-- Teacher -->
      <div class="mb-3">
        <label class="form-label">Teacher</label>
        <select v-model="form.teacher_id" class="form-select" required>
          <option value="" disabled>Select Teacher</option>
          <option v-for="t in teachers" :key="t.id" :value="t.id">
            {{ t.first_name }} {{ t.last_name }}
          </option>
        </select>
      </div>

      <!-- Day of Week -->
      <div class="mb-3">
        <label class="form-label">Day of Week</label>
        <select v-model="form.day_of_week" class="form-select" required>
          <option value="" disabled>Select Day</option>
          <option v-for="day in days" :key="day" :value="day">{{ day }}</option>
        </select>
      </div>

      <!-- Time -->
      <div class="mb-3 row">
        <div class="col">
          <label class="form-label">Start Time</label>
          <input type="time" v-model="form.start_time" class="form-control" required />
        </div>
        <div class="col">
          <label class="form-label">End Time</label>
          <input type="time" v-model="form.end_time" class="form-control" required />
        </div>
      </div>

      <!-- Submit -->
      <button type="submit" class="btn btn-primary">
        {{ isUpdate ? "Update" : "Create" }}
      </button>
    </form>

    <!-- Success/Error messages -->
    <div v-if="message" class="alert alert-success mt-3">{{ message }}</div>
    <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { useRoute } from "vue-router"

const route = useRoute()
const isUpdate = route.path.includes("update");
const timetableId = route.params.id

const form = ref({
  class_id: "",
  subject_id: "",
  teacher_id: "",
  day_of_week: "",
  start_time: "",
  end_time: ""
})

const classes = ref([])
const subjects = ref([])
const teachers = ref([])
const message = ref("")
const error = ref("")
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

// Fetch dropdown data
const fetchData = async () => {
  try {
    const [clsRes, subjRes, teacherRes] = await Promise.all([
      axios.get("/api/get_classes", { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }),
      axios.get("/api/get_subjects", { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }),
      axios.get("/api/get_teachers", { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } })
    ])
    classes.value = clsRes.data
    subjects.value = subjRes.data
    teachers.value = teacherRes.data

    // If update → fetch timetable details and prefill
    if (isUpdate) {
      const res = await axios.get(`/api/get_timetable_timetable_id/${timetableId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      })
      const data = res.data
      console.log(data)
      form.value = {
    class_id: data.class_?.id || "",
    subject_id: data.subject?.id || "",
    teacher_id: data.teacher?.id || "",
    day_of_week: data.day_of_week || "",
    start_time: data.start_time || "",
    end_time: data.end_time || ""
  }
}
    
  } catch (err) {
    error.value = "Failed to fetch data."
  }
}

// Create or Update timetable entry
const submitTimetable = async () => {
  message.value = ""
  error.value = ""
  try {
    if (isUpdate) {
      const response = await axios.put(`/api/update_timetable/${timetableId}`, form.value, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      })
      message.value = response.data.message
    } else {
      const response = await axios.post("/api/create_timetable", form.value, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      })
      message.value = response.data.message
      form.value = { class_id: "", subject_id: "", teacher_id: "", day_of_week: "", start_time: "", end_time: "" }
    }
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to save timetable entry."
  }
}

onMounted(fetchData)
</script>
