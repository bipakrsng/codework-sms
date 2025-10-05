<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">
      Fee Records for Student ID: {{ studentId }}
    </h2>

    <!-- Fees Table -->
    <div v-if="fees.length > 0" class="overflow-x-auto">
      <table class="table-auto w-full border-collapse border">
        <thead>
          <tr class="bg-gray-100">
            <th class="border px-4 py-2">Fee ID</th>
            <th class="border px-4 py-2">Amount Due</th>
            <th class="border px-4 py-2">Due Date</th>
            <th class="border px-4 py-2">Is Paid</th>
            <th class="border px-4 py-2">Amount Paid</th>
            <th class="border px-4 py-2">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="fee in fees" :key="fee.id">
            <td class="border px-4 py-2">{{ fee.id }}</td>
            <td class="border px-4 py-2">{{ fee.amount_due }}</td>
            <td class="border px-4 py-2">{{ formatDate(fee.due_date) }}</td>
            <td class="border px-4 py-2">{{ fee.is_paid ? "Yes" : "No" }}</td>
            <td class="border px-4 py-2">{{ fee.amount_paid || 0 }}</td>
            <td class="border px-4 py-2">{{ fee.payment_status }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- No Records -->
    <div v-else-if="feesFetched" class="text-red-500">
      No fee records found.
    </div>

    <!-- Error/Message -->
    <div v-if="message" class="mt-4 text-blue-600">
      {{ message }}
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { useRoute } from "vue-router";

export default {
  name: "StudentFees",
  setup() {
    const route = useRoute();
    const studentId = route.params.student_id; // <-- get student_id from URL
    return { studentId };
  },
  data() {
    return {
      fees: [],
      feesFetched: false,
      message: "",
    };
  },
  mounted() {
    this.fetchFees();
  },
  methods: {
    async fetchFees() {
      try {
        const res = await axios.get(`/api/get_fees/${this.studentId}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        this.fees = res.data;
        this.feesFetched = true;
      } catch (err) {
        this.fees = [];
        this.feesFetched = true;
        this.message =
          err.response?.data?.message || "Error fetching fee records.";
      }
    },
    formatDate(dt) {
      if (!dt) return "";
      return new Date(dt).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      });
    },
  },
};
</script>
