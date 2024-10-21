<template>
    <p role="log" aria-live="polite">{{ useDescriptionStore().description }}</p>
</template>

<script setup lang="ts">
    import { useDescriptionStore } from '@/stores/description';
</script>