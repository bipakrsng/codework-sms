<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
    <h3>Subjects</h3>
    <button class="btn btn-primary mb-3" @click="$router.push('/subjects/create')">
      + Create New Subject
    </button>
    </div>


    <table class="table table-bordered">
      <thead>
        <tr>
          <th>ID</th>
          <th>Subject Name</th>
          <th>Code</th>
          <th>Created At</th>
          <th>Updated At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="subject in subjects" :key="subject.id">
          <td>{{ subject.id }}</td>
          <td>{{ subject.name }}</td>
          <td>{{ subject.code }}</td>
          <td>{{ new Date(subject.created_at).toLocaleString() }}</td>
          <td>{{ new Date(subject.updated_at).toLocaleString() }}</td>
          <td>
            <button
              class="btn btn-warning btn-sm me-2"
              @click="$router.push(`/subjects/update/${subject.id}`)"
            >
              Update
            </button>
            <button
              class="btn btn-danger btn-sm"
              @click="deleteSubject(subject.id)"
            >
              Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const subjects = ref([]);

const fetchSubjects = async () => {
  try {
    const res = await axios.get("http://localhost:5000/api/get_subjects", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    subjects.value = res.data;
  } catch (err) {
    console.error("Error fetching subjects:", err);
  }
};

const deleteSubject = async (id) => {
  if (!confirm("Are you sure you want to delete this subject?")) return;
  try {
    await axios.delete(`http://localhost:5000/api/delete_subject/${id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
    });
    subjects.value = subjects.value.filter((s) => s.id !== id);
  } catch (err) {
    console.error("Error deleting subject:", err);
  }
};

onMounted(fetchSubjects);
</script>
