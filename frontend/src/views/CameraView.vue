<template>
    <div class="flex flex-col h-screen">
        <section class="p-2">
            <OptionBar></OptionBar>
        </section>
        <section class="flex-1 p-2 border border-black">
            <CameraModule></CameraModule>
        </section>
        <section class="border border-black p-2">
            <h2 class="sr-only">Environment description</h2>
            <TextDescription></TextDescription>
        </section>
    </div>
</template>

<script lang="ts" setup>
    import CameraModule from '@/components/Header/CameraView/CameraModule.vue';
    import OptionBar from '@/components/Header/CameraView/OptionBar.vue';
    import TextDescription from '@/components/Header/CameraView/TextDescription.vue';
</script>