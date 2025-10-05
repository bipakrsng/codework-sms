<template>

  <div class="container mt-5">
    <h3 class="mb-4">Update Student having id : {{ studentId }}</h3>
    <form @submit.prevent="submitForm">
      <!-- Section 1: Basic User Details -->
      <div v-if="step === 1" class="card mb-3">
        <div class="card-header bg-primary text-white">
          Basic User Details
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label for="email" class="form-label">Email <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.email"
              type="email"
              id="email"
              class="form-control"
              required
              placeholder="Enter email"
              @blur="validateEmail"
            />
          </div>
          <div v-if="errors.email" class="text-danger small">{{ errors.email }}</div>
          
          <div class="mb-3">
            <label for="phone_number" class="form-label">Phone Number <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.phone_number"
              type="tel"
              id="phone_number"
              class="form-control"
              required
              placeholder="Enter phone number"
              @blur="validatePhone('phone_number')"
            />
          </div>
          <div v-if="errors.phone_number" class="text-danger small">{{ errors.phone_number }}</div>
        </div>
      </div>

      <!-- Section 2: Student Details -->
      <div v-if="step === 2" class="card mb-3">
        <div class="card-header bg-success text-white">
          Student Details
        </div>
        <div class="card-body">
          <!-- Same inputs as before for student details -->
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="first_name" class="form-label">First Name <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.first_name"
                type="text"
                id="first_name"
                class="form-control"
                required
                placeholder="First name"
              />
            </div>
            <div class="col-md-6 mb-3">
              <label for="last_name" class="form-label">Last Name <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.last_name"
                type="text"
                id="last_name"
                class="form-control"
                required
                placeholder="Last name"
              />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="date_of_birth" class="form-label">Date of Birth <span class="text-danger">*</span></label>
              <input
                v-model="form.date_of_birth"
                type="date"
                id="date_of_birth"
                class="form-control"
                required
              />
            </div>
            <div class="col-md-6 mb-3">
              <label for="gender" class="form-label">Gender <span class="text-danger">*</span></label>
              <select v-model="form.gender" id="gender" class="form-select" required>
                <option disabled value="">Select gender</option>
                <option>Male</option>
                <option>Female</option>
                <option>Other</option>
              </select>
            </div>
          </div>

          <div class="mb-3">
            <label for="address_line1" class="form-label">Address Line 1 <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.address_line1"
              type="text"
              id="address_line1"
              class="form-control"
              required
              placeholder="Address line 1"
            />
          </div>

          <div class="mb-3">
            <label for="address_line2" class="form-label">Address Line 2</label>
            <input
              v-model.trim="form.address_line2"
              type="text"
              id="address_line2"
              class="form-control"
              placeholder="Address line 2 (optional)"
            />
          </div>

          <div class="row">
            <div class="col-md-4 mb-3">
              <label for="city" class="form-label">City <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.city"
                type="text"
                id="city"
                class="form-control"
                required
                placeholder="City"
              />
            </div>
            <div class="col-md-4 mb-3">
              <label for="state" class="form-label">State <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.state"
                type="text"
                id="state"
                class="form-control"
                required
                placeholder="State"
              />
            </div>
            <div class="col-md-4 mb-3">
              <label for="postal_code" class="form-label">Postal Code <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.postal_code"
                type="text"
                id="postal_code"
                class="form-control"
                required
                placeholder="Postal code"
              />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="country" class="form-label">Country <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.country"
                type="text"
                id="country"
                class="form-control"
                required
                placeholder="Country"
              />
            </div>

            <div class="col-md-6 mb-3">
              <label for="class_id" class="form-label">Class ID <span class="text-danger">*</span></label>
              <select 
                v-model.number="form.class_id"
                placeholder="Select Class"
                id="class_id"
                class="form-control"
                required
              >
              <option value="" disabled>Select CLass </option>
              <option v-for="cls in classes"
              :keys="cls.id"
              :value="cls.id">{{cls.name +" "+cls.section}}</option>
              </select>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="religion" class="form-label">Religion <span class="text-danger">*</span></label>
              <select
                v-model.trim="form.religion"
                type="text"
                id="religion"
                class="form-control"
                required
                placeholder="Religion"
              >
                <option value="" disabled>Select Religion</option>
                <option>Hindu</option>
                <option>Muslim</option>
                <option>Christian</option>
                <option>Sikh</option>
                <option>Other</option>
              </select>
            </div>
            <div class="col-md-6 mb-3">
              <label for="admission_date" class="form-label">Admission Date <span class="text-danger">*</span></label>
              <input
                v-model="form.admission_date"
                type="date"
                id="admission_date"
                class="form-control"
                required
              />
            </div>
          </div>

          <div class="mb-3">
            <label for="roll_number" class="form-label">Roll Number <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.roll_number"
              type="text"
              id="roll_number"
              class="form-control"
              required
              placeholder="Roll number"
            />
          </div>

          <div class="mb-3">
            <label for="aadhar_number" class="form-label">Aadhar Number <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.aadhaar_number"
              type="text"
              id="aadhar_number"
              class="form-control"
              required
              placeholder="Aadhar number"
              pattern="\d{12}"
              title="Aadhar number must be 12 digits"
              maxlength="12"
              @blur="validateAadhar('aadhaar_number')"
            />
          </div>
          <div v-if="errors.aadhaar_number" class="text-danger small">{{ errors.aadhar_number }}</div>


          <div class="mb-3">
            <label for="apaar_id" class="form-label">Apaar ID <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.apaar_id"
              type="text"
              id="apaar_id"
              class="form-control"
              required
              placeholder="Apaar ID"
              pattern="\d{12}"
              title="Apaar ID must be 12 digits"
              maxlength="12"
              @blur="validateAadhar('apaar_id')"
            />
          </div>
          <div v-if="errors.apaar_id" class="text-danger small">{{ errors.apaar_id }}</div>
        </div>
      </div>

      <!-- Section 3: Parent/Guardian Details -->
      <div v-if="step === 3" class="card mb-4">
        <div class="card-header bg-info text-white">
          Guardian/Parent Details
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="guardian_first_name" class="form-label">Guardian First Name <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.guardian_first_name"
                type="text"
                id="guardian_first_name"
                class="form-control"
                required
                placeholder="Guardian first name"
              />
            </div>
            <div class="col-md-6 mb-3">
              <label for="guardian_last_name" class="form-label">Guardian Last Name <span class="text-danger">*</span></label>
              <input
                v-model.trim="form.guardian_last_name"
                type="text"
                id="guardian_last_name"
                class="form-control"
                required
                placeholder="Guardian last name"
              />
            </div>
          </div>

          <div class="mb-3">
            <label for="guardian_email" class="form-label">Guardian Email <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.guardian_email"
              type="email"
              id="guardian_email"
              class="form-control"
              required
              placeholder="Guardian email"
              @blur="validateEmail"
            />
          </div>
          <div v-if="errors.guardian_email" class="text-danger small">{{ errors.guardian_email }}</div>

          <div class="mb-3">
            <label for="guardian_phone" class="form-label">Guardian Phone <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.guardian_phone"
              type="tel"
              id="guardian_phone"
              class="form-control"
              required
              placeholder="Guardian phone"
              
              @blur="validatePhoneGuardian('guardian_phone')"
              maxlength="10"
            />
          </div>
          <div v-if="errors.guardian_phone" class="text-danger small">{{ errors.guardian_phone }}</div>


          <div class="mb-3">
            <label for="relationship" class="form-label">Relationship <span class="text-danger">*</span></label>
            <select
              v-model.trim="form.relationship"
              type="text"
              id="relationship"
              class="form-control"
              required
              placeholder="Relationship to student"
            >
            <option value="" disabled>Select Relationship</option>
            <option value="Father">Father</option>
            <option value="Mother">Mother</option>
            <option value="Guardian">Guardian</option>
            <option value="Other">Other</option>

          </select>
          </div>

          <div class="mb-3">
            <label for="guardian_aadhar_number" class="form-label">Guardian Aadhar Number <span class="text-danger">*</span></label>
            <input
              v-model.trim="form.guardian_aadhar_number"
              type="text"
              id="guardian_aadhar_number"
              class="form-control"
              required
              placeholder="Guardian aadhar number"
              @blur="validateAadharGaurdian('guardian_aadhar_number')"
            />
          </div>
          <div v-if="errors.guardian_aadhar_number" class="text-danger small">{{ errors.guardian_aadhar_number }}</div>

        </div>
      </div>

      <!-- Navigation Buttons -->
      <div class="d-flex justify-content-between mt-3">
        <button
          type="button"
          class="btn btn-secondary"
          :disabled="step === 1"
          @click="prevStep"
        >
          Previous
        </button>

        <button
          v-if="step < 3"
          type="button"
          class="btn btn-primary"
          @click="nextStep"
        >
          Next
        </button>

        <button
          v-if="step === 3"
          type="submit"
          class="btn btn-success"
          :disabled="loading"
        >
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          Submit
        </button>
      </div>

      <!-- Response Message -->
      <div
        v-if="responseMessage"
        :class="['alert mt-3', responseSuccess ? 'alert-success' : 'alert-danger']"
      >
        {{ responseMessage }}
      </div>
    </form>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const studentId = route.params.id

const step = ref(1)
const form = ref({
  email: '',
  
  phone_number: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: '',
  address_line1: '',
  address_line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: '',
  class_id: null,
  religion: '',
  admission_date: '',
  roll_number: '',
  aadhaar_number: '',
  apaar_id: '',
  guardian_first_name: '',
  guardian_last_name: '',
  guardian_email: '',
  guardian_phone: '',
  relationship: '',
  guardian_aadhar_number: ''
})

const errors = ref({})
const classes = ref([])
const loading = ref(false)
const responseMessage = ref('')
const responseSuccess = ref(false)

const validateEmail = () => {
  const regex = /^[^\s@]+@gmail\.com$/i
  errors.value.email = regex.test(form.value.email) ? '' : 'Email must be a valid Gmail address'
}
const validateGuardianEmail = () => {
  const regex = /^[^\s@]+@gmail\.com$/i
  errors.value.guardian_email = regex.test(form.value.guardian_email) ? '' : 'Email must be a valid Gmail address'
}
const validatePhone = () => {
  const regex = /^[6-9]\d{9}$/
  errors.value.phone_number = regex.test(form.value.phone_number) ? '' : 'Phone number must be 10 digits starting with 6-9'
}
const validatePhoneGuardian = () => {
  const regex = /^[6-9]\d{9}$/
  errors.value.guardian_phone = regex.test(form.value.guardian_phone) ? '' : 'Phone number must be 10 digits starting with 6-9'
}
const validateAadhar = () => {
  const regex = /^\d{12}$/
  errors.value.aadhaar_number = regex.test(form.value.aadhaar_number) ? '' : 'Aadhar number must be exactly 12 digits'
}
const validateAadharGaurdian = () => {
  const regex = /^\d{12}$/
  errors.value.guardian_aadhar_number = regex.test(form.value.guardian_aadhar_number) ? '' : 'Aadhar number must be exactly 12 digits'
}
const validateApaar = () => {
  const regex = /^[A-Za-z0-9]{12}$/
  errors.value.apaar_id = regex.test(form.value.apaar_id) ? '' : 'Apaar ID must be 12 alphanumeric characters'
}


const validateAll = () => {
  validateEmail()
  validatePhone('phone_number')
  validatePhoneGuardian()
  validateAadhar('aadhar_number')
  validateAadharGaurdian('guardian_aadhar_number')
  validateApaar()
  validateGuardianEmail()
  validatePhone('guardian_phone')
  validateAadhar('guardian_aadhar_number')
  console.log("Errors object before return:", errors.value)
  return Object.values(errors.value).every(err => err === '')
  
}

const nextStep = () => { if (step.value < 3) step.value++ }
const prevStep = () => { if (step.value > 1) step.value-- }

const classesget = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/get_classes', { headers: { Authorization: `Bearer ${token}` } })
    if (!res.ok) throw new Error('Failed to fetch classes')
    classes.value = await res.json()
  } catch (error) {
    console.error(error)
  }
}

const fetchStudentDetails = async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/get_student/${studentId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) throw new Error('Failed to fetch student details')
    const data = await res.json()
    
    form.value.email = data.user?.email || ''
    form.value.phone_number = data.user?.phone_number || ''
    form.value.first_name = data.first_name || ''
    form.value.last_name = data.last_name || ''
    form.value.date_of_birth = data.date_of_birth
      ? new Date(data.date_of_birth).toISOString().split('T')[0] // format for <input type="date">
      : ''
    form.value.gender = data.gender || ''
    form.value.address_line1 = data.address_line1 || ''
    form.value.address_line2 = data.address_line2 || ''
    form.value.city = data.city || ''
    form.value.state = data.state || ''
    form.value.country = data.country || ''
    form.value.postal_code = data.postal_code || ''
    form.value.class_id = data.class_id || null
    form.value.religion = data.religion || ''
    form.value.admission_date = data.admission_date
      ? new Date(data.admission_date).toISOString().split('T')[0]
      : ''
    form.value.roll_number = data.roll_number || ''
    form.value.aadhaar_number = data.aadhaar_number || ''
    form.value.apaar_id = data.apaar_id || ''

    // Guardian/Parent details
    form.value.guardian_first_name = data.parent?.first_name || ''
    form.value.guardian_last_name = data.parent?.last_name || ''
    form.value.guardian_email = data.parent?.email || ''
    form.value.guardian_phone = data.parent?.phone || ''
    form.value.relationship = data.parent?.relationship || ''
    form.value.guardian_aadhar_number = data.parent?.aadhar_number || ''

  } catch (error) {
    console.error(error)
  }
}

const submitForm = async () => {
  loading.value = true

  if (!validateAll()) {
    responseMessage.value = 'Please fix validation errors before submitting.'
    responseSuccess.value = false
    loading.value = false
    return
  }
  // else{
  //   console.log(this.form)
  // }
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/update_student/${studentId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(form.value)
    })
    const data = await res.json()
    responseSuccess.value = res.ok
    responseMessage.value = data.message || (res.ok ? 'Student updated successfully' : 'Failed to update student')
    if (res.ok) {
      setTimeout(() => router.push('/getStudent'), 2000)
    }
  } catch (error) {
    console.error(error)
    responseSuccess.value = false
    responseMessage.value = 'Server error. Please try again later.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  classesget()
  fetchStudentDetails()
})
</script>
