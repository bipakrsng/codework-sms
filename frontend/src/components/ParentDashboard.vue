<template>
  <div class="container mt-5">
    <h2 class="mb-4 text-center">👨‍👩‍👦 Parent Dashboard</h2>

    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status"></div>
      <p>Loading your students...</p>
    </div>

    <div v-else>
      <div v-if="students.length > 0">
        <div class="row">
          <div v-for="student in students" :key="student.id" class="col-md-6">
            <div class="card shadow-sm mb-4">
              <div class="card-body">
                <!-- Student Info -->
                <h5 class="card-title">
                  {{ student.first_name }} {{ student.last_name }}
                </h5>
                <p class="card-text">
                  <strong>DOB:</strong> {{ formatDate(student.date_of_birth) }} <br />
                  <strong>Admission Date:</strong> {{ formatDate(student.admission_date) }} <br />
                  <strong>Gender:</strong> {{ student.gender }} <br />
                  <strong>Aadhaar:</strong> {{ student.aadhaar_number }} <br />
                  <strong>APAAR ID:</strong> {{ student.apaar_id }} <br />
                  <strong>Class ID:</strong> {{ student.class_id }} <br />
                  <strong>Address:</strong>
                  {{ student.address_line1 }} {{ student.address_line2 }},
                  {{ student.city }}, {{ student.country }} <br />
                </p>

                <!-- Fee Details -->
                <div v-if="fees[student.id] && fees[student.id].length" class="mt-3 border-top pt-3">
                  <h6>Fee Details</h6>
                  <div v-for="fee in fees[student.id].filter(f => f.payment_status !=='Paid')" :key="fee.id" 
                  
                  class="mb-2 p-2 border rounded">
                    <p>
                      <strong>Fee ID:</strong> {{ fee.id }} <br />
                      <strong>Amount Due:</strong> ₹{{ fee.amount_due }} <br />
                      <strong>Amount Paid:</strong> ₹{{ fee.amount_paid || 0 }} <br />
                      <strong>Due Date:</strong> {{ formatDate(fee.due_date) }} <br />
                      <strong>Status:</strong>
                      <span :class="statusClass(fee.payment_status)">
                        {{ fee.payment_status }}
                      </span>
                    </p>

                    <button
                      v-if="fee.payment_status !== 'Paid'"
                      class="btn btn-success btn-sm"
                      @click="payNow(student.id, fee.id)"
                    >
                      Pay Now
                    </button>
                  </div>
                </div>

                <!-- Payment History -->
                <div v-if="paymentHistory[student.id]" class="mt-3 border-top pt-3">
                  <h6>📜 Payment History</h6>
                  <ul class="list-group">
                    <li
                      v-for="p in paymentHistory[student.id]"
                      :key="p.id"
                      class="list-group-item d-flex justify-content-between"
                    >
                      <span>{{ formatDate(p.created_at) }} - ₹{{ p.amount }}</span>
                      <span class="badge bg-success">Paid</span>
                    </li>
                  </ul>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="alert alert-info">
        No students found for your account.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { decodeToken } from "@/utils/auth";

const students = ref([]);
const fees = ref({});
const paymentHistory = ref({});
const loading = ref(true);
const user_id = ref(null);

const formatDate = (datestr) => {
  if (!datestr) return "N/A";
  const date = new Date(datestr);
  return date.toLocaleDateString("en-GB", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};

// Bootstrap color helper
const statusClass = (status) => {
  if (status === "Paid") return "text-success fw-bold";
  if (status === "Overdue") return "text-danger fw-bold";
  return "text-warning fw-bold";
};

// Fetch students + fee info
onMounted(async () => {
  try {
    const token = localStorage.getItem("token");
    const user = decodeToken(token);
    user_id.value = user ? user.user_id : null;

    const res = await axios.get(`/api/get_parent_students/${user_id.value}`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    students.value = res.data;

    for (let s of students.value) {
      try {
        const feeRes = await axios.get(`/api/get_fees/${s.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        fees.value[s.id] = feeRes.data;

        // Uncomment later when history API is ready
        const historyRes = await axios.get(`/api/get_payments_history/${s.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        paymentHistory.value[s.id] = historyRes.data;
      } catch (err) {
        console.error(`Error fetching fee for student ${s.id}:`, err);
      }
    }
  } catch (err) {
    console.error("Error fetching students:", err);
  } finally {
    loading.value = false;
  }
});

// Razorpay PayNow
const payNow = async (studentId, feeId) => {
  try {
    const token = localStorage.getItem("token");

    // 1. Create order from backend
    const res = await axios.post(`/api/create_order/${studentId}/${feeId}`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const { order_id, amount, currency, razorpay_key } = res.data;

    // 2. Launch Razorpay checkout
    const options = {
      key: razorpay_key,
      amount: amount,
      currency: currency,
      name: "School Fees",
      description: "Fee Payment",
      order_id: order_id,
      handler: async function (response) {
        // 3. Verify payment on backend
        await axios.post(`/api/verify_payment`, {
          razorpay_order_id: response.razorpay_order_id,
          razorpay_payment_id: response.razorpay_payment_id,
          razorpay_signature: response.razorpay_signature,
          fee_id: feeId
        }, {
          headers: { Authorization: `Bearer ${token}` }
        });

        alert("Payment Successful!");
        window.location.reload();
      },
      theme: { color: "#3399cc" }
    };

    const rzp = new Razorpay(options);
    rzp.open();

  } catch (err) {
    console.error("Payment error:", err);
    alert("Payment failed");
  }
};
</script>
