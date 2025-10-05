<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3>Student List</h3>
      <button class="btn btn-primary" @click="$router.push('/createStudent')">
        Add Student
      </button>
    </div>

    <table class="table table-bordered table-hover align-middle">
      <thead class="table-dark">
        <tr>
          <th>ID</th>
          <th>First Name</th>
          <th>Last Name</th>
          <th>DOB</th>
          <th>Gender</th>
          <th>City</th>
          <th>Parent ID</th>
          <th>Actions</th>
          <th>Delete_by</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="student in students" :key="student.id"
        :class="student.deleted_at ? 'table-danger' : 'table-secondary'">
          <td>{{ student.id }}</td>
          <td>{{ student.first_name }}</td>
          <td>{{ student.last_name }}</td>
          <td>{{ formatDate(student.date_of_birth) }}</td>
          <td>{{ student.gender }}</td>
          <td>{{ student.city }}</td>
          <td>
            <a href="#" @click.prevent="showParent(student.parent)">
              {{ student.parent_id }}
            </a>
          </td>
          <td>
              <div class="dropdown">
                <button 
                  class="btn btn-secondary btn-sm dropdown-toggle" 
                  type="button" 
                  id="dropdownMenuButton"
                  data-bs-toggle="dropdown" 
                  aria-expanded="false"
                >
                  Actions
                </button>

                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
                  <li>
                    <button 
                    class="dropdown-item text-warning" 
                    @click="editStudent(student)"
                    v-if="!student.deleted_at">
                      Update
                    </button>
                  </li>
                  <li>
                    <button 
                    class="dropdown-item text-danger" @click="deleteStudent(student.id)"
                    v-if="!student.deleted_at">
                      Delete
                    </button>
                  </li>
                  <li>
                    <button 
                    class="dropdown-item text-info" @click="showGrades(student)"
                    v-if="!student.deleted_at">
                      Show Grades
                    </button>
                  </li>
                  <li>
                    <button 
                    class="dropdown-item text-success" @click="modifyGrades(student)"
                    v-if="!student.deleted_at">
                      Modify Grades
                    </button>
                  </li>
                  <li>
                    <button 
                    class="dropdown-item text-warning" 
                    @click="feeStudent(student)"
                    v-if="!student.deleted_at">
                      Show Fee
                    </button>
                  </li>
                  <li>
                    <button 
                    class="dropdown-item text-primary" 
                    @click="feeCreate(student)"
                    v-if="!student.deleted_at">
                      Create Fee
                    </button>
                  </li>
                   <li>
                    <button 
                    class="dropdown-item text-primary" 
                    @click="restoreStudent(student.id)"
                    v-if="student.deleted_at">
                      Restore
                    </button>
                  </li>
                </ul>
              </div>
            </td>
            <td>
             {{ student.deleted_at ? student.user.phone_number : ''  }}
            </td>
            

        </tr>
        <tr v-if="students.length === 0">
          <td colspan="8" class="text-center">No students found.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();

const students = ref([]);

// Fetch students from API
const fetchStudents = async () => {
  try {
    const token = localStorage.getItem("token");
    const res = await fetch("/api/get_students", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Failed to fetch students");
    const data = await res.json();
    console.log(data)
    students.value = data;
  } catch (e) {
    alert(e.message);
  }
};

onMounted(() => {
  fetchStudents();
});

// Format date helper
const formatDate = (dt) => {
  if (!dt) return "";
  return new Date(dt).toLocaleDateString();
};

// Student update (navigate to update page)
const editStudent = (student) => {
  router.push(`/updateStudent/${student.id}`);
};

const feeStudent = (student) => {
  router.push({name:'StudentFee',params:{student_id:student.id}});
};

const feeCreate = (student) => {
  router.push({name:'FeeCreate',params:{student_id:student.id}});
};
// Delete student
const deleteStudent = async (id) => {
  if (!confirm("Are you sure you want to delete this student?")) return;
  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`/api/delete_student/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to delete student");
    fetchStudents();
    // alert("Student deleted successfully");
    // students.value = students.value.filter((s) => s.id !== id);
  } catch (e) {
    alert(e.message);
  }
};

const restoreStudent = async (id) => {
  if (!confirm("Are you sure you want to restore this student?")) return;
  try {
    const token = localStorage.getItem("token");
    const res = await fetch(`/api/restore_student/${id}`, {
      method: "PATCH",
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || "Failed to restore student");
    fetchStudents();
    // alert("Student deleted successfully");
    // students.value = students.value.filter((s) => s.id !== id);
  } catch (e) {
    alert(e.message);
  }
};

// Navigate to Grade Fetcher
const showGrades = (student) => {
  // Assuming student.class_id exists (otherwise pass it differently)
  router.push({
    
    name: "GradeFetcher",
    params: { student_id: student.id, class_id: student.class_id },
  });
};

// Navigate to Grade Manager
const modifyGrades = (student) => {
  router.push({
    name: "GradeManager",
    params: { student_id: student.id, class_id: student.class_id },
  });
};
</script>
