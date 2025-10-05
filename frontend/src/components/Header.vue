<template>
  <header id="header" class="header fixed-top d-flex align-items-center">
    <div class="d-flex align-items-center justify-content-between">
      <a href="index.html" class="logo d-flex align-items-center">
        <img src="@/assets/img/logo.png" alt="" />
        <span class="d-none d-lg-block">NiceAdmin</span>
      </a>
      <i class="bi bi-list toggle-sidebar-btn"></i>
    </div>
    <!-- End Logo -->

    <div class="search-bar">
      <form class="search-form d-flex align-items-center" method="POST" action="#">
        <input type="text" name="query" placeholder="Search" title="Enter search keyword" />
        <button type="submit" title="Search"><i class="bi bi-search"></i></button>
      </form>
    </div>
    <!-- End Search Bar -->

    <nav class="header-nav ms-auto">
      <ul class="d-flex align-items-center">
        <li class="nav-item d-block d-lg-none">
          <a class="nav-link nav-icon search-bar-toggle" href="#">
            <i class="bi bi-search"></i>
          </a>
        </li>
        <!-- End Search Icon-->

        <!-- Notifications -->
        <li class="nav-item dropdown">
          <a class="nav-link nav-icon" href="#" data-bs-toggle="dropdown">
            <i class="bi bi-bell"></i>
            <span class="badge bg-primary badge-number">4</span>
          </a>

          <ul class="dropdown-menu dropdown-menu-end dropdown-menu-arrow notifications">
            <li class="dropdown-header">
              You have 4 new notifications
              <a href="#"><span class="badge rounded-pill bg-primary p-2 ms-2">View all</span></a>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="notification-item">
              <i class="bi bi-exclamation-circle text-warning"></i>
              <div>
                <h4>Lorem Ipsum</h4>
                <p>Quae dolorem earum veritatis oditseno</p>
                <p>30 min. ago</p>
              </div>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="notification-item">
              <i class="bi bi-x-circle text-danger"></i>
              <div>
                <h4>Atque rerum nesciunt</h4>
                <p>Quae dolorem earum veritatis oditseno</p>
                <p>1 hr. ago</p>
              </div>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="notification-item">
              <i class="bi bi-check-circle text-success"></i>
              <div>
                <h4>Sit rerum fuga</h4>
                <p>Quae dolorem earum veritatis oditseno</p>
                <p>2 hrs. ago</p>
              </div>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="notification-item">
              <i class="bi bi-info-circle text-primary"></i>
              <div>
                <h4>Dicta reprehenderit</h4>
                <p>Quae dolorem earum veritatis oditseno</p>
                <p>4 hrs. ago</p>
              </div>
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li class="dropdown-footer">
              <a href="#">Show all notifications</a>
            </li>
          </ul>
        </li>
        <!-- End Notification Nav -->

        <!-- Messages -->
        <li class="nav-item dropdown">
          <a class="nav-link nav-icon" href="/message" data-bs-toggle="dropdown">
            <i class="bi bi-chat-left-text"></i>
            <span class="badge bg-success badge-number">3</span>
          </a>

          <ul class="dropdown-menu dropdown-menu-end dropdown-menu-arrow messages">
            <li class="dropdown-header">
              You have 3 new messages
              <a href="/message"><span class="badge rounded-pill bg-primary p-2 ms-2">View all</span></a>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="message-item">
              <a href="#">
                <img src="@/assets/img/messages-1.jpg" alt="" class="rounded-circle" />
                <div>
                  <h4>Maria Hudson</h4>
                  <p>Velit asperiores et ducimus soluta repudiandae labore officia est ut...</p>
                  <p>4 hrs. ago</p>
                </div>
              </a>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="message-item">
              <a href="#">
                <img src="@/assets/img/messages-2.jpg" alt="" class="rounded-circle" />
                <div>
                  <h4>Anna Nelson</h4>
                  <p>Velit asperiores et ducimus soluta repudiandae labore officia est ut...</p>
                  <p>6 hrs. ago</p>
                </div>
              </a>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="message-item">
              <a href="#">
                <img src="@/assets/img/messages-3.jpg" alt="" class="rounded-circle" />
                <div>
                  <h4>David Muldon</h4>
                  <p>Velit asperiores et ducimus soluta repudiandae labore officia est ut...</p>
                  <p>8 hrs. ago</p>
                </div>
              </a>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li class="dropdown-footer">
              <a href="#">Show all messages</a>
            </li>
          </ul>
        </li>
        <!-- End Messages Nav -->

        <!-- Profile Dropdown -->
        <li class="nav-item dropdown pe-3">
          <a
            class="nav-link nav-profile d-flex align-items-center pe-0"
            href="#"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <img src="@/assets/img/profile-img.jpg" alt="Profile" class="rounded-circle" />
            <span class="d-none d-md-block dropdown-toggle ps-2">
              {{ user ? user.name : "Guest" }}
            </span>
          </a>

          <ul class="dropdown-menu dropdown-menu-end dropdown-menu-arrow profile">
            <li class="dropdown-header">
              <h6>{{ user ? user.email : "Kevin Anderson" }}</h6>
              <span>{{ user ? user.role : "Web Designer" }}</span>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li>
              <router-link class="dropdown-item d-flex align-items-center" to="/profile">
                <i class="bi bi-person"></i>
                <span>My Profile</span>
              </router-link>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li>
              <router-link class="dropdown-item d-flex align-items-center" to="/settings">
                <i class="bi bi-gear"></i>
                <span>Account Settings</span>
              </router-link>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li>
              <router-link class="dropdown-item d-flex align-items-center" to="/faq">
                <i class="bi bi-question-circle"></i>
                <span>Need Help?</span>
              </router-link>
            </li>
            <li><hr class="dropdown-divider" /></li>

            <li v-if="user">
              <a class="dropdown-item d-flex align-items-center" href="#" @click.prevent="logout">
                <i class="bi bi-box-arrow-right"></i>
                <span>Sign Out</span>
              </a>
            </li>
          </ul>
        </li>
        <!-- End Profile Dropdown -->
      </ul>
    </nav>
    <!-- End Icons Navigation -->
  </header>
  <!-- End Header -->

  <!-- ======= Sidebar ======= -->
  <aside id="sidebar" class="sidebar">
    <ul class="sidebar-nav" id="sidebar-nav">
      <li class="nav-item">
        <a class="nav-link" href="index.html">
          <i class="bi bi-grid"></i>
          <span>Dashboard</span>
        </a>
      </li>

      <!-- Example collapsed menus -->
      <li class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#components-nav" data-bs-toggle="collapse" href="#">
          <i class="bi bi-menu-button-wide"></i><span>Class</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="components-nav" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getClasses"><i class="bi bi-circle"></i><span>All Classes</span></a>
          </li>
          <li>
            <a href="/add-class"><i class="bi bi-circle"></i><span>Add Class</span></a>
          </li>
        </ul>
      </li>

      <!-- Session -->
      <li class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#forms-nav" data-bs-toggle="collapse" href="#">
          <i class="bi bi-journal-text"></i><span>Session</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="forms-nav" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getSession"><i class="bi bi-circle"></i><span>Sessions</span></a>
          </li>
          <li>
            <a href="/addSession"><i class="bi bi-circle"></i><span>Add Session</span></a>
          </li>
        </ul>
      </li>

      <!-- Students -->
      <li class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#tables-nav" data-bs-toggle="collapse" href="#">
          <i class="bi bi-layout-text-window-reverse"></i><span>Students</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="tables-nav" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getStudents"><i class="bi bi-circle"></i><span>All Students</span></a>
          </li>
          <li>
            <a href="/createStudent"><i class="bi bi-circle"></i><span>Add Student</span></a>
          </li>
          <li>
            <a href="/assign-subject"><i class="bi bi-circle"></i><span>Assign Subject to Student</span></a>
          </li>
        </ul>
      </li>

      <!-- Teacher -->
      <li v-if="user.role[0]==='admin'" class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#charts-nav" data-bs-toggle="collapse" href="#">
          <i class="bi bi-bar-chart"></i><span>Teacher</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="charts-nav" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getTeacher"><i class="bi bi-circle"></i><span>All Teacher</span></a>
          </li>
          <li>
            <a href="/createTeacher"><i class="bi bi-circle"></i><span>Add Teacher</span></a>
          </li>
        </ul>
      </li>

      <!-- Subjects -->
      <li class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#icons-nav" data-bs-toggle="collapse" href="#">
          <i class="bi bi-gem"></i><span>Subject</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="icons-nav" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getSubject"><i class="bi bi-circle"></i><span>All Subjects</span></a>
          </li>
          <li>
            <a href="/subjects/create"><i class="bi bi-circle"></i><span>Add Subject</span></a>
          </li>
        </ul>
      </li>

      <!-- Timetable -->
      <li class="nav-item">
        <a class="nav-link collapsed" data-bs-target="#icons-nav1" data-bs-toggle="collapse" href="#">
          <i class="bi bi-gem"></i><span>Timetable</span><i class="bi bi-chevron-down ms-auto"></i>
        </a>
        <ul id="icons-nav1" class="nav-content collapse" data-bs-parent="#sidebar-nav">
          <li>
            <a href="/getClasses"><i class="bi bi-circle"></i><span>Timetable by Class</span></a>
          </li>
          <li>
            <a href="/createTimetable"><i class="bi bi-circle"></i><span>Create Timetable</span></a>
          </li>
        </ul>
      </li>


      <li class="nav-item" v-if="user.role[0]==='admin'">
        <a class="nav-link collapsed" href='/face-register'>
          <i class="bi bi-person"></i>
          <span>Face Register</span>
        </a>
      </li>

      <!-- Profile -->
      <li class="nav-item">
        <a class="nav-link collapsed" href="/message">
          <i class="bi bi-person"></i>
          <span>Message</span>
        </a>
      </li>

       <li class="nav-item">
        <a class="nav-link collapsed" href="/mark_attendance">
          <i class="bi bi-person"></i>
          <span>Mark Attendance</span>
        </a>
      </li>

      <!-- Contact -->
      <li class="nav-item">
        <a class="nav-link collapsed" href="/attendance">
          <i class="bi bi-envelope"></i>
          <span>Attendance</span>
        </a>

      </li>
       <li class="nav-item">
        <a class="nav-link collapsed" href="#">
          <i class="bi bi-envelope"></i>
          <span>Contact</span>
        </a>
      </li>

      <!-- Login/Logout -->
      <li class="nav-item" v-if="!user">
        <a class="nav-link collapsed" href="/login">
          <i class="bi bi-box-arrow-in-right"></i>
          <span>Login</span>
        </a>
      </li>
      <li class="nav-item" v-if="user">
        <a class="nav-link collapsed" href="/logout" @click="logout">
          <i class="bi bi-box-arrow-in-right"></i>
          <span>Sign out</span>
        </a>
      </li>
    </ul>
  </aside>
  <!-- End Sidebar-->
</template>

<script>
import { decodeToken } from "@/utils/auth";

export default {
  name: "Header",
  data() {
    return {
      user: null,
    };
  },
  created() {
    const token = localStorage.getItem("token");
    if (token) {
      this.user = decodeToken(token);
      console.log(this.user);
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      this.$router.push("/login");
    },
  },
};
</script>
