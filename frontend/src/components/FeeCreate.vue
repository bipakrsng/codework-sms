<template>
  <div class="container my-5 d-flex justify-content-center">
    <div class="card shadow-lg border-0 rounded-4 w-50">
      <div class="card-body p-5">
        <!-- Title -->
        <h2 class="text-center mb-4 fw-bold text-primary">
          Create Fee Record
        </h2>

        <!-- Form -->
        <form @submit.prevent="createFee">
          <!-- Amount -->
          <div class="mb-4">
            <label class="form-label fw-semibold">Amount</label>
            <input
              v-model="amount"
              type="number"
              step="0.01"
              required
              placeholder="Enter fee amount"
              class="form-control form-control-lg"
            />
          </div>

          <!-- Due Date -->
          <div class="mb-4">
            <label class="form-label fw-semibold">Due Date</label>
            <input
              v-model="dueDate"
              type="date"
              required
              class="form-control form-control-lg"
            />
          </div>

          <!-- Submit Button -->
          <div class="d-grid">
            <button type="submit" class="btn btn-success btn-lg">
              <i class="bi bi-plus-circle me-2"></i> Create Fee
            </button>
          </div>
        </form>

        <!-- Message -->
        <div v-if="message" class="mt-4 text-center">
          <div
            v-if="success"
            class="alert alert-success fw-semibold"
            role="alert"
          >
            {{ message }}
          </div>
          <div
            v-else
            class="alert alert-danger fw-semibold"
            role="alert"
          >
            {{ message }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useRoute } from "vue-router";

export default {
  name: "FeeCreate",
  setup() {
    const route = useRoute();
    const studentId = route.params.student_id; // student_id from URL
    return { studentId };
  },
  data() {
    return {
      amount: "",
      dueDate: "",
      message: "",
      success: false,
    };
  },
  methods: {
    async createFee() {
      try {
        const res = await axios.post(
          `/api/create_fees/${this.studentId}`,
          {
            amount: this.amount,
            due_date: this.dueDate,
          },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`
            },
          }
        );
        this.message = res.data.message;
        this.success = true;
        this.amount = "";
        this.dueDate = "";
      } catch (err) {
        this.message =
          err.response?.data?.message || "Error creating fee record.";
        this.success = false;
      }
    },
  },
};
</script>
