<template>
  <div class="container mt-4">
    <h4>Assign Subjects to Students</h4>
    <div class="card p-3 shadow-sm">
      <!-- Student Dropdown -->
      <div class="mb-3">
        <label for="student" class="form-label">Select Student</label>
        <select v-model="selectedStudent" class="form-select" id="student">
          <option disabled value="">-- Choose Student --</option>
          <option v-for="student in students" :key="student.id" :value="student.id">
            {{ student.first_name }} {{ student.last_name }} (Class {{ student.class_name }})
          </option>
        </select>
      </div>

      <!-- Subjects Multi Select -->
     <div class="mb-3">
  <label class="form-label">Select Subjects</label>
  <div v-for="subject in subjects" :key="subject.id" class="form-check">
    <input
      class="form-check-input"
      type="checkbox"
      :id="'subject-' + subject.id"
      :value="subject.id"
      v-model="selectedSubjects"
    />
    <label class="form-check-label" :for="'subject-' + subject.id">
      {{ subject.name }}
    </label>
  </div>
  <div class="form-text">You can select multiple subjects.</div>
</div>


      <!-- Submit Button -->
      <button class="btn btn-primary" @click="assignSubjects">Assign</button>
    </div>

    <!-- Assigned subjects display -->
    <div v-if="assigned.length" class="mt-4">
      <h5>Assigned Subjects</h5>
      <ul class="list-group">
        <li v-for="(sub, idx) in assigned" :key="idx" class="list-group-item">
          {{ sub }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "StudentSubjectMapping",
  data() {
    return {
      students: [],
      subjects: [],
      selectedStudent: "",
      selectedSubjects: [],
      assigned: []
    };
  },
  mounted() {
    this.fetchStudents();
    this.fetchSubjects();
  },
  methods: {
    async fetchStudents() {
      const res = await axios.get("/api/get_students",{
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      this.students = res.data;
    },
    async fetchSubjects() {
      const res = await axios.get("/api/get_subjects",{
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      this.subjects = res.data;
    },
    async assignSubjects() {
      if (!this.selectedStudent || this.selectedSubjects.length === 0) {
        alert("Please select a student and at least one subject.");
        return;
      }

      try {
        const res = await axios.post("/api/assign_subject_to_student", {
          student_id: this.selectedStudent,
          subject_ids: this.selectedSubjects,
        },{
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        this.assigned = res.data.assigned_subjects;
        alert("Subjects assigned successfully!");
      } catch (err) {
        console.error(err);
        alert("Error assigning subjects.");
      }
    },
  },
};
</script>
