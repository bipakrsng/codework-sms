<template>
  <div class="container mt-5">
    <h2 class="mb-4">
      Timetable for {{ timetableData.class_name }} - {{ timetableData.section }}
    </h2>

    <!-- Error / Loading -->
    <div v-if="loading" class="text-muted">Loading timetable...</div>
    <div v-if="error" class="text-danger">{{ error }}</div>

    <!-- Timetable -->
    <div v-if="!loading && !error">
      <div
        v-for="(entries, day) in timetableData.timetable"
        :key="day"
        class="mb-4"
      >
        <h4 class="bg-primary text-white p-2 rounded">{{ day }}</h4>
        <table class="table table-bordered">
          <thead>
            <tr>
              <th>Start</th>
              <th>End</th>
              <th>Subject</th>
              <th>Teacher</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="entry in entries" :key="entry.id">
              <td>{{ entry.start_time }}</td>
              <td>{{ entry.end_time }}</td>
              <td>{{ entry.subject }}</td>
              <td>{{ entry.teacher }}</td>
              <td>
                <button
                  class="btn btn-sm btn-warning me-2"
                  @click="goToUpdate(entry.id)"
                >
                  Update
                </button>
                <button
                  class="btn btn-sm btn-danger"
                  @click="deleteTimetable(entry.id)"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import axios from "axios"
import { useRouter } from "vue-router"

const props = defineProps({
  id: {
    type: Number,
    required: true
  }
})

const router = useRouter()
const timetableData = ref({})
const loading = ref(true)
const error = ref("")

// Fetch timetable
const fetchTimetable = async () => {
  try {
    const response = await axios.get(`/api/get_timetable/${props.id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
    timetableData.value = response.data
    console.log(response.data)
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to fetch timetable."
  } finally {
    loading.value = false
  }
}

// Delete timetable entry
const deleteTimetable = async (entryId) => {
  if (!confirm("Are you sure you want to delete this entry?")) return

  try {
    await axios.delete(`/api/delete_timetable/${entryId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    })
    // Refresh timetable
    fetchTimetable()
  } catch (err) {
    error.value = err.response?.data?.message || "Failed to delete entry."
  }
}

// Navigate to update page
const goToUpdate = (entryId) => {
  router.push(`/timetable/update/${entryId}`)
}

onMounted(fetchTimetable)
</script>

<style scoped>
.table {
  background-color: #fff;
}
</style>
