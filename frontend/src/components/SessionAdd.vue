<template>
  <nav-bar></nav-bar>
  <div class="container mt-5">
    <div class="card shadow rounded-4">
      <div class="card-header bg-primary text-white text-center fs-4">
        Create New Session
      </div>
      <div class="card-body">
        <form @submit.prevent="submitForm">
          <!-- Start Date -->
          <div class="mb-3">
            <label for="start_date" class="form-label">Start Date</label>
            <input
              type="date"
              id="start_date"
              v-model="form.start_date"
              class="form-control"
              :min="minDate"
              required
            />
            <small v-if="errors.start_date" class="text-danger">
              {{ errors.start_date }}
            </small>
          </div>

          <!-- End Date -->
          <div class="mb-3">
            <label for="end_date" class="form-label">End Date</label>
            <input
              type="date"
              id="end_date"
              v-model="form.end_date"
              class="form-control"
              :min="form.start_date + 365 || minDate"
              required
            />
            <small v-if="errors.end_date" class="text-danger">
              {{ errors.end_date }}
            </small>
          </div>

          <!-- Action Buttons -->
          <div class="d-flex justify-content-end gap-2">
            <button
              type="button"
              class="btn btn-secondary"
              @click="$router.back()"
            >
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              Create Session
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "CreateSession",
  data() {
    const today = new Date().toISOString().split("T")[0];
    return {
      minDate: today,
      form: {
        start_date: "",
        end_date: "",
      },
      errors: {
        start_date: "",
        end_date: "",
      },
    };
  },
  methods: {
    validateForm() {
      let valid = true;
      this.errors = { start_date: "", end_date: "" };

      // Check if dates are filled
      if (!this.form.start_date) {
        this.errors.start_date = "Start date is required.";
        valid = false;
      }
      if (!this.form.end_date) {
        this.errors.end_date = "End date is required.";
        valid = false;
      }

      // Validate start date not in past
      const today = new Date();
      const start = new Date(this.form.start_date);
      const end = new Date(this.form.end_date);

      if (this.form.start_date && start < today.setHours(0, 0, 0, 0)) {
        this.errors.start_date = "Start date cannot be in the past.";
        valid = false;
      }

      // Validate end date after start date
      if (this.form.start_date && this.form.end_date && end < start) {
        this.errors.end_date = "End date must be after start date.";
        valid = false;
      }

      // Optional: Limit session duration (e.g., max 1 year)
      const maxDurationDays = 365;
      if (this.form.start_date && this.form.end_date) {
        const diffDays =
          (end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24);
          console.log(diffDays)
        if (diffDays < 365 || diffDays % 365 !== 0 ) {
          this.errors.end_date = `Session cannot be less than 365 days. or it should be multiple of 365 days`;
          valid = false;
        }
      }

      return valid;
    },

    async submitForm() {
      if (!this.validateForm()) {
        return;
      }

      try {
        const token = localStorage.getItem("token");

        const response = await fetch("/api/create_session", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(this.form),
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.message || "Failed to create session.");
        }

        alert("Session created successfully!");
        this.$router.push("/getSession");
      } catch (error) {
        console.error(error);
        alert(error.message);
      }
    },
  },
};
</script>
