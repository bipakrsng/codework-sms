<template>
  <div class="container mt-4">
    <div class="card shadow-lg border-0 rounded-3">
      <div class="card-header bg-primary text-white text-center">
        <h5 class="mb-0">
          <i class="bi bi-pencil-square me-2"></i> Update Teacher
        </h5>
      </div>

      <div class="card-body p-4">
        <form @submit.prevent="updateTeacher">
          <!-- TEACHER DETAILS -->
          <h5 class="text-secondary border-bottom pb-2 mb-3 mt-2">
            <i class="bi bi-person-badge me-2"></i> Teacher Information
          </h5>
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">First Name <span class="text-danger">*</span></label>
              <input type="text" v-model="form.first_name" class="form-control" required />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Last Name <span class="text-danger">*</span></label>
              <input type="text" v-model="form.last_name" class="form-control" required />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Teacher Phone <span class="text-danger">*</span></label>
              <input type="tel" v-model="form.phone" class="form-control" required />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Teacher Email <span class="text-danger">*</span></label>
              <input type="email" v-model="form.email" class="form-control" required />
            </div>
          </div>

          <!-- SUBJECTS -->
          <div class="mb-3">
            <label class="form-label">Add Subject <span class="text-danger">*</span></label>
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
                    v-model="form.add_subject_ids"
                    @change="onAddChange(sub.id)"
                  />
                  <label class="form-check-label" :for="'subject-' + sub.id">
                    {{ sub.name }} ({{ sub.code }})
                  </label>
                </div>
              </div>
            </div>
            <small class="text-muted">You can select multiple subjects</small>
          </div>

          <div class="mb-3">
            <label class="form-label">Remove Subjects <span class="text-danger">*</span></label>
            <div class="row">
              <div 
                v-for="sube in subjects" 
                :key="sube.id" 
                class="col-md-6 mb-2"
              >
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    :id="'subject-' + sube.id"
                    :value="sube.id"
                    v-model="form.remove_subject_ids"
                    @change="onAddChange(sube.id)"
                  />
                  <label class="form-check-label" :for="'subject-' + sube.id">
                    {{ sube.name }} ({{ sube.code }})
                  </label>
                </div>
              </div>
            </div>
            <small class="text-muted">You can select multiple subjects</small>
          </div>

          <!-- BUTTONS -->
          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="button" @click="router.push('/teachers')" class="btn btn-outline-secondary px-4">
              <i class="bi bi-arrow-left me-1"></i> Back
            </button>
            <button type="submit" class="btn btn-success px-4" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i class="bi bi-check2-circle me-1"></i> Update Teacher
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="message" class="alert alert-info mt-3">{{ message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {watch} from "vue"
import axios from "axios";

const route = useRoute();
const router = useRouter();
const teacherId = route.params.id;

const form = ref({
  first_name: "",
  last_name: "",
  phone: "",
  email: "",
  add_subject_ids:[],
  remove_subject_ids:[]
});

const subjects = ref([]);
const loading = ref(false);
const message = ref("");

// Fetch subjects for checkboxes
const fetchSubjects = async () => {
  try {
    const token = localStorage.getItem("token");
    const res = await fetch("/api/get_subjects", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to load subjects");
    subjects.value = await res.json();
  } catch (e) {
    alert(e.message);
  }
};

// Fetch teacher details to pre-fill form
const fetchTeacher = async () => {
  try {
    const token = localStorage.getItem("token");
    const res = await axios.get(`/api/get_teacher/${teacherId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = res.data;

    form.value.first_name = data.first_name;
    form.value.last_name = data.last_name;
    form.value.phone = data.phone;
    form.value.email = data.email;
    form.value.add_subject_ids = data.subjects ? data.subjects.map(s => s.id) : [];
    form.value.remove_subject_ids = [];

  } catch (err) {
    console.error("Error fetching teacher:", err);
  }
};

// Update teacher API call
const updateTeacher = async () => {
  try {
    loading.value = true;
    const token = localStorage.getItem("token");
    await axios.put(`/api/update_teacher/${teacherId}`, form.value, {
      headers: { Authorization: `Bearer ${token}` },
    });
    message.value = "Teacher updated successfully!";
    router.push("/getTeacher")
  } catch (err) {
    console.error("Error updating teacher:", err);
    message.value = "Failed to update teacher.";
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchSubjects();
  fetchTeacher();
});

const onAddChange = (id) => {
  // If added to add_subject_ids, remove from remove_subject_ids
  if (form.value.add_subject_ids.includes(id)) {
    form.value.remove_subject_ids = form.value.remove_subject_ids.filter(rid => rid !== id)
  }

  if (form.value.remove_subject_ids.includes(id)) {
    form.value.add_subject_ids = form.value.add_subject_ids.filter(rid => rid !== id)
  }
}


</script>

<style scoped>
.container {
  max-width: 800px;
}
</style>
