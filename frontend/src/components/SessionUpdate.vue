<template>
  <nav-bar></nav-bar>
  <div class="container mt-5">
    <div class="card shadow rounded-4">
      <div class="card-header bg-primary text-white text-center fs-4 fw-bold">
        Update Session
      </div>
      <div class="card-body">
        <form @submit.prevent="updateSession">
          <!-- Session Name -->
          <div class="mb-3">
            <label class="form-label fw-semibold">Session Name</label>
            <input
              v-model="sessionData.name"
              type="text"
              class="form-control text-muted"
              readonly
            />
          </div>

          <!-- Start Date -->
          <div class="mb-3">
            <label class="form-label fw-semibold">Start Date</label>
            <input
              v-model="sessionData.start_date"
              type="date"
              class="form-control"
              required
            />
          </div>

          <!-- End Date -->
          <div class="mb-3">
            <label class="form-label fw-semibold">End Date</label>
            <input
              v-model="sessionData.end_date"
              type="date"
              class="form-control"
              required
            />
          </div>

          <!-- Status -->
          <div class="mb-3">
            <label class="form-label fw-semibold">Status</label>
            <select v-model="sessionData.is_active" class="form-control" required>
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>

          <!-- Buttons -->
          <div class="d-flex justify-content-end gap-2">
            
            <button type="submit" class="btn btn-success" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm"></span>
              Save Changes
            </button>

            <button type="button" class="btn btn-secondary" @click="$router.back()">
              Cancel
            </button>
            
          </div>
        </form>
      </div>
    </div>

    <!-- Alert -->
    <div
      v-if="message"
      :class="['alert', success ? 'alert-success' : 'alert-danger', 'mt-3']"
    >
      {{ message }}
    </div>
  </div>
</template>

<script>
import { useSessionStore } from "@/store/userStore";

export default {
  name: "SessionUpdate",
  data() {
    return {
      sessionData: {
        id: "",
        name: "",
        start_date: "",
        end_date: "",
        is_active: null,
      },
      loading: false,
      message: "",
      success: false,
    };
  },
  mounted() {
    const store = useSessionStore();
    if (store.currentSession) {
      const session = { ...store.currentSession };

      // Format dates to YYYY-MM-DD for HTML date input
      session.start_date = this.formatDateForInput(session.start_date);
      session.end_date = this.formatDateForInput(session.end_date);

      // Ensure is_active is boolean
      if (typeof session.is_active !== "boolean") {
        session.is_active = session.is_active === "active" || session.is_active === 1;
      }

      this.sessionData = session;
    } else {
      this.message = "No session data found.";
      this.success = false;
    }
  },
  methods: {
    formatDateForInput(date) {
      if (!date) return "";
      const d = new Date(date);
      if (isNaN(d)) return "";
      return d.toISOString().split("T")[0];
    },

    validateForm() {
      if (!this.sessionData.start_date) {
        this.message = "Start date is required.";
        this.success = false;
        return false;
      }
      if (!this.sessionData.end_date) {
        this.message = "End date is required.";
        this.success = false;
        return false;
      }
      if (new Date(this.sessionData.end_date) < new Date(this.sessionData.start_date)) {
        this.message = "End date cannot be earlier than start date.";
        this.success = false;
        return false;
      }
      return true;
    },

    async updateSession() {
      if (!this.validateForm()) return;

      this.loading = true;
      this.message = "";

      try {
        const payload = {
          start_date: this.sessionData.start_date,
          end_date: this.sessionData.end_date,
          is_active: this.sessionData.is_active,
        };

        const response = await fetch(
          `/api/update_session/${this.sessionData.id}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: "Bearer " + localStorage.getItem("token"),
            },
            body: JSON.stringify(payload),
          }
        );

        if (!response.ok) {
          throw new Error("Failed to update session");
        }

        this.success = true;
        this.message = "Session updated successfully!";
        setTimeout(() => {
          this.$router.push("/getSession");
        }, 1500);
      } catch (error) {
        this.success = false;
        this.message = error.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
