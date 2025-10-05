<template>
  <div class="container mt-4">
    <h4>Capture Face (embedding-only)</h4>

    <!-- Student Dropdown -->
    <select v-model="studentid" class="form-select mb-2">
      <option disabled value="">Select student</option>
      <option v-for="s in students" :key="s.id" :value="s.id">
        {{ s.first_name }} {{ s.last_name }} (ID: {{ s.id }})
      </option>
    </select>

    <!-- Video + Canvas Overlay -->
    <div style="position: relative; width: 320px; height: 240px;">
      <video ref="video" autoplay playsinline width="320" height="240" class="border"></video>
      <canvas ref="overlay" width="320" height="240" style="position:absolute; top:0; left:0; pointer-events:none;"></canvas>
    </div>

    <div class="mt-2">
      <button @click="startCamera" class="btn btn-primary me-2">Start Camera</button>
      <button @click="captureAndRegister" class="btn btn-success" :disabled="!studentid">Capture & Register</button>
      <button @click="captureAndVerify" class="btn btn-warning">Capture & Verify</button>
    </div>

    <div v-if="message" class="mt-3 alert alert-info">{{ message }}</div>
    <div v-if="verifyResult" class="mt-3">
      <pre>{{ verifyResult }}</pre>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import * as faceapi from "face-api.js";

export default {
  data() {
    return {
      stream: null,
      studentid: "",
      students: [],
      message: "",
      verifyResult: null,
      modelsLoaded: false,
      detecting: false
    };
  },
  async mounted() {
    await this.loadModels();
    this.fetchStudents();
  },
  beforeUnmount() {
    // Stop camera when leaving component
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
    this.detecting = false;
  },
  methods: {
    async loadModels() {
      try {
        await faceapi.nets.tinyFaceDetector.loadFromUri("/models");
        this.modelsLoaded = true;
        console.log("Face models loaded");
      } catch (err) {
        console.error("Failed to load face models", err);
      }
    },
    async startCamera() {
      if (this.stream) return;
      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ video: true });
        this.$refs.video.srcObject = this.stream;

        // Start detection loop once video is ready
        this.$refs.video.onloadeddata = () => {
          console.log("Video ready, starting detection...");
          this.detecting = true;
          this.detectLoop();
        };
      } catch (e) {
        alert("Camera error: " + e.message);
      }
    },
    async detectLoop() {
  if (!this.modelsLoaded || !this.detecting) return;

  const video = this.$refs.video;
  const overlay = this.$refs.overlay;
  const ctx = overlay.getContext("2d");

  // Ensure canvas matches real video size
  overlay.width = video.videoWidth;
  overlay.height = video.videoHeight;

  const displaySize = { width: video.videoWidth, height: video.videoHeight };
  faceapi.matchDimensions(overlay, displaySize);

  const detect = async () => {
    if (!this.detecting) return;

    ctx.clearRect(0, 0, overlay.width, overlay.height);

    let detection = await faceapi.detectSingleFace(
      video,
      new faceapi.TinyFaceDetectorOptions()
    );

    if (detection) {
      detection = faceapi.resizeResults(detection, displaySize);

      const { x, y, width, height } = detection.box;

      overlay.width = width;
      overlay.height = height;

      // DEBUG rectangle first
      ctx.strokeStyle = "red";
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);

      // Circle
      const centerX = x + width / 2;
      const centerY = y + height / 2;
      const radius = Math.min(width, height) / 2;

      ctx.strokeStyle = "lime";
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
      ctx.stroke();
    }

    requestAnimationFrame(detect);
  };

  detect();
},

    async captureFaceOnly() {
      let detection = await faceapi.detectSingleFace(
        this.$refs.video,
        new faceapi.TinyFaceDetectorOptions()
      );
      if (!detection) {
        alert("No face detected!");
        return null;
      }

      const { x, y, width, height } = detection.box;
      const sx = Math.floor(x);
      const sy = Math.floor(y);
      const sw = Math.floor(width);
      const sh = Math.floor(height);

      const canvas = document.createElement("canvas");
      canvas.width = sw;
      canvas.height = sh;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(this.$refs.video, sx, sy, sw, sh, 0, 0, sw, sh);

      return canvas.toDataURL("image/png");
    },
    async captureSequence(duration = 2000) {
  const frames = [];
  const start = Date.now();
  while (Date.now() - start < duration) {
    const img = await this.captureFaceOnly();
    if (img) frames.push(img);
    await new Promise(r => setTimeout(r, 300)); // capture ~3 fps
  }
  return frames;
},
    async captureAndRegister() {
  if (!this.studentid) return alert("Select student first");

  this.message = "Please blink twice or turn your head left ↔ right during capture";

  const frames = await this.captureSequence(3000); // 3 sec sequence

  if (frames.length < 3) {
    return alert("Not enough frames captured");
  }

  try {
    const res = await axios.post(
      "/api/register_face",
      { student_id: this.studentid, frames },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    this.message = res.data.message || "Registered";
  } catch (err) {
    this.message = err?.response?.data?.error || "Registration failed";
  }
}
,
async captureAndVerify() {
  // capture 3 frames in quick succession
  const frames = [];
  for (let i = 0; i < 3; i++) {
    const img = await this.captureFaceOnly();
    if (img) frames.push(img);
    await new Promise(r => setTimeout(r, 500)); // small delay
  }

  if (frames.length === 0) return;

  try {
    const res = await axios.post(
      "/api/verify_face",
      { frames: frames, top_k: 3 },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    this.verifyResult = res.data.matches;
  } catch (err) {
    this.verifyResult = { error: err?.response?.data?.error || "Verify failed" };
  }
}
,
    async fetchStudents() {
      try {
        const res = await axios.get("/api/get_students", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` }
        });
        this.students = res.data || [];
      } catch (e) {
        console.error("Failed to fetch students", e);
      }
    }
  }
};
</script>
