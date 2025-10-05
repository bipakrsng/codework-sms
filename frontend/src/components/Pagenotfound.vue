<template>
  <div class="d-flex flex-column justify-content-center align-items-center vh-100 bg-light text-center">
    <h1 class="display-1 fw-bold text-danger">404</h1>
    <h2 class="mb-3">Page Not Found</h2>
    <p class="text-muted mb-4">
      Sorry, the page you are looking for does not exist or has been moved.
    </p>
    <!-- <router-link to="/" class="btn btn-primary">
      Back to Home
    </router-link> -->
    <button class="btn btn-primary"
    @click="$router.back()">GO Back</button>
  </div>
</template>

<script>
export default {
  name: "NotFoundPage",
};
</script>
