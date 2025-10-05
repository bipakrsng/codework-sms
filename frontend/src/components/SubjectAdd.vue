<template>
  <div class="container d-flex justify-content-center align-items-center mt-5">
    <div class="card shadow-lg p-4 rounded-4" style="max-width: 500px; width: 100%;">
      <h3 class="text-center mb-4 fw-bold text-primary">
        {{ isUpdate ? "Update Subject" : "Create New Subject" }}
      </h3>

      <form @submit.prevent="handleSubmit" class="needs-validation">
        <!-- Subject Name -->
        <div class="mb-3">
          <label class="form-label fw-semibold">📘 Subject Name</label>
          <input
            v-model="form.name"
            type="text"
            class="form-control form-control-lg rounded-3"
            placeholder="Enter subject name"
            required
          />
        </div>

        <!-- Subject Code -->
        <div class="mb-3">
          <label class="form-label fw-semibold">🔖 Subject Code</label>
          <input
            v-model="form.code"
            type="text"
            class="form-control form-control-lg rounded-3"
            placeholder="Enter subject code"
            required
          />
        </div>

        <!-- Action Buttons -->
        <div class="d-flex justify-content-between mt-4">
          <button type="button" class="btn btn-outline-secondary px-4 rounded-3" @click="router.push('/getSubject')">
            Cancel
          </button>
          <button type="submit" class="btn btn-success px-4 rounded-3">
            {{ isUpdate ? "Update" : "Create" }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";

const route = useRoute();
const router = useRouter();

const form = ref({
  name: "",
  code: "",
});

const isUpdate = route.path.includes("update");
const subjectId = route.params.id;

// Fetch subject details when updating
const fetchSubject = async () => {
  try {
    const res = await axios.get(`/api/get_subject/${subjectId}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    form.value = {
      name: res.data.name,
      code: res.data.code,
    };
  } catch (err) {
    console.error("Error fetching subject:", err);
  }
};

const handleSubmit = async () => {
  try {
    if (isUpdate) {
      await axios.put(`/api/update_subject/${subjectId}`, form.value, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      
    } else {
      await axios.post("/api/create_subject", form.value, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      
    }
    router.push("/getSubject");
  } catch (err) {
    console.error("Error saving subject:", err);
  }
};

onMounted(() => {
  if (isUpdate) fetchSubject();
});
</script>
