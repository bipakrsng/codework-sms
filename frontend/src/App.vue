<template>
    <div>
        <hea-der v-if="!['/','/register'].includes($route.path)"></hea-der>
        <router-view></router-view>
        <foo-ter v-if="!['/','/register'].includes($route.path)"></foo-ter>
    </div>
</template>
