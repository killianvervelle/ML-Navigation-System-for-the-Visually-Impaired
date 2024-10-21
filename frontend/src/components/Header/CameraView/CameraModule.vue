<template>
    <div class="h-full flex flex-col justify-between">
        <div :class="{ 'opacity-25': loading }" class="flex-grow">
            <video playsinline ref="camera" autoplay="true"></video>
        </div>
        <input v-if="optionsStore.currentMode == Mode.Tracking" class="border border-black " type="text"
                v-model="optionsStore.trackingElement" placeholder="Object to track" :disabled=optionsStore.continuous>
        <button :disabled="cannotTakePicture" @click="snapshot()">Take picture</button>
    </div>
</template>

<script setup lang="ts">
    import CameraPhoto, { FACING_MODES } from 'jslib-html5-camera-photo';
    import { getInfoFromImage, getTrackingFromImage } from "@/api/api";
    import { useOptionsStore } from "@/stores/options";
    import { useDescriptionStore } from "@/stores/description";
    import { storeToRefs } from 'pinia'
    import { ref, watch, onMounted, computed } from "vue";
    import { Mode } from '@/models/modes';

    const loading = ref(false);

    const camera: any = ref(null);

    onMounted(() => {
        startCamera();
    });

    let cameraPhoto: any;

    const startCamera = async () => {
        console.log(FACING_MODES.ENVIRONMENT)

        cameraPhoto = new CameraPhoto(camera.value);
        cameraPhoto.startCamera(FACING_MODES.ENVIRONMENT, {})
            .then(() => {
                console.log("camera started")
            })
            .catch((error) => {
                console.error("Camera not started", error)
            });
    }

    const dataURLtoFile = (dataurl: any, filename: any) => {
        const arr = dataurl.split(',')
        const mime = arr[0].match(/:(.*?);/)[1]
        const bstr = atob(arr[1])
        let n = bstr.length
        const u8arr = new Uint8Array(n)
        while (n) {
            u8arr[n - 1] = bstr.charCodeAt(n - 1)
            n -= 1 // to make eslint happy
        }
        return new File([u8arr], filename, { type: mime })
    }

    const optionsStore = useOptionsStore();

    const snapshot = async () => {
        loading.value = true
        camera.value?.pause()
        const config = {};
        let dataUri = cameraPhoto.getDataUri(config);


        let result;
        if (optionsStore.currentMode == Mode.Tracking) {
            result = await getTrackingFromImage(dataURLtoFile(dataUri, "image.png"), optionsStore.trackingElement)
        } else {
            result = await getInfoFromImage(optionsStore.currentMode, dataURLtoFile(dataUri, "image.png"))
        }

        if (result.error) {
            console.error(result.error);
            if (typeof result.error === "string") {
                useDescriptionStore().description = result.error
            } else {
                useDescriptionStore().description = "Network error"
            }
            loading.value = false
            camera.value?.play()
            return;
        }

        useDescriptionStore().description = result.data;
        camera.value?.play()
        loading.value = false
    }

    const cannotTakePicture = computed(() => {
        return ((optionsStore.currentMode == Mode.Tracking) && (optionsStore.trackingElement == "")) || optionsStore.continuous
    });

    const { continuous } = storeToRefs(useOptionsStore())

    let interval: number = 0;

    watch(continuous, async (isContinuous) => {
        if (isContinuous) {
            await takeContinuousSnapshot();
        } else {
            clearTimeout(interval);
        }
    });

    const takeContinuousSnapshot = async () => {
        if (continuous) {
            await snapshot()
            interval = setTimeout(async () => {
                await takeContinuousSnapshot();
            }, 5000);
        }
    }

</script>