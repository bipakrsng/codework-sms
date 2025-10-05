<template>
  <div class="container my-4">
    <!-- Search Box -->
    <div class="card p-3 mb-4">
      <h5>Subject Attendance</h5>
      <div class="row g-3">
        
        
        <div class="col-md-2">
          <select v-model="filters.clas" class="form-select">
            <option value="" disabled>Select Class</option>
            <option v-for="s in classes" :key="s" :value="s.id">{{ s.name + " "+s.section }}</option>
          </select>
        </div>

        
        <div class="col-md-2">
          <select v-model="filters.course" class="form-select">
            <option value="" disabled>Select Course</option>
            <option v-for="c in courses" :key="c" :value="c.id">{{ c.name +" "+ c.code }}</option>
          </select>
        </div>
         <div class="card p-3 mb-3">
          <input type="date" v-model="filters.date" class="form-control" />
        </div>

        <div class="col-md-2">
          <button class="btn btn-success w-100" @click="fetchAttendance">Search</button>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- Attendance Table -->
      <div class="col-md-8">
        <div class="card p-3">
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Name</th>
                <th>Present</th>
                <th>Absent</th>
                <!-- <th>Leave</th>
                <th>Note</th> -->
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in students" :key="student.student_id">
                <td>{{ student.student_id }}</td>
                <td>{{ student.name }}</td>
                <td><input type="radio" :name="`status-${student.id}`" value="Present" v-model="student.status" /></td>
                <td><input type="radio" :name="`status-${student.id}`" value="Absent" v-model="student.status" /></td>
                <!-- <td><input type="radio" :name="`status-${student.id}`" value="Leave" v-model="student.status" /></td>
                <td><input type="text" v-model="student.note" placeholder="Note" class="form-control" /></td> -->
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Calendar + Summary -->
      <div class="col-md-4">
       
        <div class="card p-3 bg-warning mb-2">
          <strong>{{ summary.total }}</strong> Total Students
        </div>
        <div class="card p-3 bg-success text-white mb-2">
          <strong>{{ summary.present }}</strong> Present Today
        </div>
        <div class="card p-3 bg-danger text-white">
          <strong>{{ summary.absent }}</strong> Absent Today
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { ref, onMounted } from "vue";

export default {
  name: "AttendanceApp",
  setup() {
    const classes = ref([]);
    
    const courses = ref([]);

    const filters = ref({
      clas: "",
      course: "",
      date: new Date().toISOString().substr(0, 10),
    });

    const students = ref([]);
    const summary = ref({ total: 100, present: 50, absent: 50 });

    // Fetch dropdown options on mount
    onMounted(async () => {
  try {
    const resClasses = await axios.get("/api/get_classes", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    });
    classes.value = resClasses.data;
    console.log(classes.value);

    const resCourses = await axios.get("/api/get_subjects", {
      headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
    });
    courses.value = resCourses.data;
    console.log(courses.value);

  } catch (err) {
    console.error(err);
  }
});


    // Fetch attendance based on search
    const fetchAttendance = async () => {
      let {  clas,course, date } = filters.value;
      let res = await axios.get(`/api/fetch_attendance`, {
        params: {  clas, course, date },
    
      
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
      },
      );
      students.value = res.data.students;
      console.log(students.value);
      summary.value = res.data.summary;
    };

    return {
      
    classes,
      courses,
      filters,
      students,
      summary,
      fetchAttendance,
    };
  },
};
</script>
