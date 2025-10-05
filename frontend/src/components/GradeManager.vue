<template>
  <div class="container">
    <h3>Manage Grades</h3>

    <form @submit.prevent="saveGrade">
      <!-- Subject -->
      <div class="mb-3">
        <label for="subject" class="form-label">Subject</label>
        <select v-model="grade.subject_id" class="form-select" id="subject">
          <option disabled value="">-- Select Subject --</option>
          <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </div>

      <!-- Term -->
      <div class="mb-3">
        <label for="term" class="form-label">Term</label>
        <select v-model="grade.term" class="form-select" id="term">
          <option disabled value="">-- Select Term --</option>
          <option v-for="t in terms" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>

      <!-- Score -->
      <div class="mb-3">
        <label for="score" class="form-label">Score</label>
        <input v-model="grade.score" type="number" class="form-control" id="score" step="0.1" />
      </div>

      <!-- Grade -->
      <div class="mb-3">
        <label for="grade" class="form-label">Grade</label>
        <select v-model="grade.grade" class="form-select" id="grade">
          <option disabled value="">-- Select Grade --</option>
          <option>A</option>
          <option>B</option>
          <option>C</option>
          <option>D</option>
          <option>F</option>
        </select>
      </div>

      <!-- Teacher -->
      <div class="mb-3">
        <label for="teacher" class="form-label">Teacher</label>
        <select v-model="grade.teacher_id" class="form-select" id="teacher">
          <option disabled value="">-- Select Teacher --</option>
          <option v-for="t in teachers" :key="t.id" :value="t.id">
            {{ t.first_name }} {{ t.last_name }}
          </option>
        </select>
      </div>

      <button class="btn btn-success" type="submit">
        {{ isUpdate ? "Update Grade" : "Add Grade" }}
      </button>
    </form>

    <div v-if="message" class="alert alert-info mt-3">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useRoute } from "vue-router";

export default {
  name: "GradeManager",
  setup() {
    const route = useRoute();
    const studentId = route.params.student_id;
    const classId = route.params.class_id;
    return { studentId, classId };
  },
  data() {
    return {
      grade: {
        subject_id: "",
        term: "",
        score: "",
        grade: "",
        teacher_id: ""
      },
      terms: ["Term 1", "Term 2", "Term 3"],
      subjects: [],
      teachers: [],
      isUpdate: false,
      message: ""
    };
  },
  mounted() {
    this.fetchSubjects();
    this.fetchTeachers();
  },
  methods: {
    async fetchSubjects() {
      const token = localStorage.getItem("token");
      const res = await axios.get("/api/get_subjects", {
        headers: { Authorization: `Bearer ${token}` }
      });
      this.subjects = res.data;
    },
    async fetchTeachers() {
        const token = localStorage.getItem("token");
      const res = await axios.get("/api/get_teachers",
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      this.teachers = res.data;
    },
    async saveGrade() {
      try {
        const res = await axios.post(
          `/api/create_grade/${this.studentId}/${this.classId}/${this.grade.term}`,
          {
            subject_id: this.grade.subject_id,
            score: this.grade.score,
            grade: this.grade.grade,
            teacher_id: this.grade.teacher_id,
            student_id: this.studentId,
            class_id: this.classId,
            term: this.grade.term
          },
            {
                headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
            }
        );
        this.message = res.data.message;
        this.isUpdate = true;
      } catch (err) {
        this.message = err.response?.data?.message || "Error saving grade.";
      }
    }
  }
};
</script>
