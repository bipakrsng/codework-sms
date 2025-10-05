<template>
  <div class="flex flex-col items-center p-4">
    <h2 class="text-xl font-bold mb-4">Face Recognition Attendance</h2>

    <!-- Camera preview -->
    <video ref="video" autoplay playsinline class="border rounded w-80 h-60"></video>

    <p v-if="status" class="mt-4 font-medium">
      {{ status }}
    </p>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from "vue";
import axios from "axios";

export default {
  setup() {
    const video = ref(null);
    const status = ref("");
    let intervalId = null;

    // Initialize camera
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.value.srcObject = stream;
      } catch (err) {
        console.error("Camera access denied:", err);
        status.value = "Unable to access camera";
      }
    };

    // Capture frame as base64
    const captureFrame = () => {
      const canvas = document.createElement("canvas");
      canvas.width = video.value.videoWidth;
      canvas.height = video.value.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video.value, 0, 0, canvas.width, canvas.height);
      return canvas.toDataURL("image/png"); // base64 format
    };

    // Send frame to backend
    const sendFrame = async () => {
      if (!video.value) return;
      const imageData = captureFrame();
      try {
        const res = await axios.post("/api/attendance/mark", 
            {
          image: imageData,
          
        },
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        status.value = res.data.status || "Attendance checked";
      } catch (err) {
        console.error("Error sending frame:", err);
        status.value = "Error sending frame";
      }
    };

    onMounted(() => {
      startCamera();

      // send frame every 5 seconds
      intervalId = setInterval(sendFrame, 5000);
    });

    onUnmounted(() => {
      if (intervalId) clearInterval(intervalId);
    });

    return { video, status };
  },
};
</script>

<style>
video {
  object-fit: cover;
}
</style>
