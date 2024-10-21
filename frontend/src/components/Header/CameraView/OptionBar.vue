<template>
    <div>
        <h2 class="sr-only">Options</h2>
        <div class="flex justify-between gap-4">
            <select aria-label="Mode selection" name="mode" id="mode" v-model="store.currentMode">
                <option value="description">Description</option>
                <option value="bus">Bus</option>
                <option value="tracking">Tracking</option>
            </select>

            <div>
                <label for="continuous">Continuous</label>
                <input v-model=store.continuous type="checkbox" id="continuous" name="continuous"
                    :disabled="store.trackingElement == '' && store.currentMode == Mode.Tracking">
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { Mode } from '@/models/modes';
    import { useOptionsStore } from '@/stores/options';
    const store = useOptionsStore();
</script>