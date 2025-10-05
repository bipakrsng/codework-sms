<template>
  <div class="container">
    <h3>Fetch Grades</h3>
    <div class="mb-3">
      <label for="term" class="form-label">Select Term</label>
      <select v-model="term" class="form-select" id="term">
        <option disabled value="">-- Select Term --</option>
        <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
      </select>
    </div>
    <button class="btn btn-primary" @click="fetchGrades">Fetch Grades</button>

    <div v-if="grades.length" class="mt-4">
      <h5>Grades:</h5>
      <table class="table">
        <thead>
          <tr>
            <th>Subject</th>
            <th>Score</th>
            <th>Grade</th>
            <th>Teacher</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="g in grades" :key="g.id">
            <td>{{ g.subject.name }}</td>
            <td>{{ g.score }}</td>
            <td>{{ g.grade }}</td>
            <td>{{ g.teacher.first_name }} {{ g.teacher.last_name }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="message" class="alert alert-warning mt-3">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useRoute } from "vue-router";

export default {
  name: "GradeFetcher",
  setup() {
    const route = useRoute();
    const studentId = route.params.student_id;
    const classId = route.params.class_id;

    return { studentId, classId };
  },
  data() {
    return {
      term: "",
      terms: ["Term 1", "Term 2", "Term 3"],
      grades: [],
      message: ""
    };
  },
  methods: {
    async fetchGrades() {
      if (!this.term) {
        this.message = "Please select a term first!";
        return;
      }
      try {
        const res = await axios.get(
          `/api/get_grades/${this.studentId}/${this.classId}/${this.term}`,
          {
            headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
          }
        );
        this.grades = res.data;
        console.log(this.grades);
        this.message = "";
      } catch (err) {
        this.grades = [];
        this.message = err.response?.data?.message || "Error fetching grades.";
      }
    }
  }
};
</script>
