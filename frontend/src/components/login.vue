<template>
  <main>
    <div class="container">
      <div class="d-flex flex-column justify-content-center align-items-center min-vh-50 ">
        <div class="row justify-content-start w-100 ">
          <div class="col-lg-4 col-md-6 ">
            <div class="login-card-wrapper">

            <!-- Logo -->
            <div class="d-flex justify-content-center py-4">
              <router-link to="/" class="d-flex align-items-center text-decoration-none">
                <img src="@/assets/img/logo.png" alt="logo" height="40" class="me-2" />
                <span class="fs-5 fw-bold d-none d-lg-inline">NiceAdmin</span>
              </router-link>
            </div>

            <!-- Card -->
            
            <div class="card shadow-sm">
              <div class="card-body">
                <div class="text-center mb-3">
                  <h5 class="fw-bold">Login to Your Account</h5>
                  <p class="text-muted small">Enter your username & password to login</p>
                </div>

                <!-- Login Form -->
                <form class="needs-validation" @submit.prevent="handleLogin" novalidate>
                  <!-- Username -->
                  <div class="mb-3">
                    <label for="yourUsername" class="form-label">Username</label>
                    <div class="input-group has-validation">
                      <span class="input-group-text">@</span>
                      <input
                        v-model="username"
                        type="text"
                        class="form-control"
                        id="yourUsername"
                        required
                      />
                      <div class="invalid-feedback">Please enter your username.</div>
                    </div>
                  </div>

                  <!-- Password -->
                  <div class="mb-3">
                    <label for="yourPassword" class="form-label">Password</label>
                    <input
                      v-model="password"
                      type="password"
                      class="form-control"
                      id="yourPassword"
                      required
                    />
                    <div class="invalid-feedback">Please enter your password!</div>
                  </div>

                  <!-- Remember Me -->
                  <div class="mb-3 form-check">
                    <input
                      class="form-check-input"
                      type="checkbox"
                      v-model="rememberMe"
                      id="rememberMe"
                    />
                    <label class="form-check-label" for="rememberMe">Remember me</label>
                  </div>

                  <!-- Error Message -->
                  <div v-if="error" class="alert alert-danger" role="alert">
                    {{ error }}
                  </div>

                  <!-- Submit -->
                  <button class="btn btn-primary w-100" type="submit">Login</button>

                  <!-- Register -->
                  <p class="small mt-3 mb-0 text-center">
                    
                    <router-link to="/register">Forget Password ?</router-link>
                  </p>
                </form>
              </div>
            </div>
            

            <!-- Credits -->
            <div class="text-center mt-3">
              <small class="text-muted">
                Designed by <a href="https://getbootstrap.com/" target="_blank">Bootstrap</a>
              </small>
            </div>

          </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script>
import axios from "axios";
import { useUserStore } from "@/store/userStore";
import { decodeToken } from "@/utils/auth";

export default {
  name: "Login",
  data() {
    return {
      username: "",
      password: "",
      rememberMe: false,
      error: null,
    };
  },
  methods: {
    async handleLogin() {
      if (!this.username || !this.password) {
        this.error = "Please enter username and password";
        return;
      }

      try {
        const response = await axios.post("/api/login", {
          email: this.username,
          password: this.password,
        });

        // Save token
        localStorage.setItem("token", response.data.token);

        // Decode token to get user info
        const user = decodeToken(response.data.token);

        // Set user in store
        const userStore = useUserStore();
        userStore.setUserFromToken(user);

        // Redirect
        if (user.role[0] === "student") this.$router.push("/student-dashboard");

        if (user.role[0] === "teacher") this.$router.push("/teacher-dashboard");

        if (user.role[0] === "admin")
        this.$router.push("/admin-dashboard");
        if (user.role[0] === "parent") this.$router.push("/parent-dashboard");

      } catch (error) {
        console.error("Login failed:", error);
        this.error = error.response?.data?.error || "Login failed. Please try again.";
      }
    },
  },
};
</script>
