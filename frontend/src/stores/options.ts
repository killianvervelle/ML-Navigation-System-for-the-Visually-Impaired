import { ref, watch } from "vue";
import { defineStore } from "pinia";
import { Mode } from "@/models/modes";

export const useOptionsStore = defineStore("options", () => {
  const currentMode = ref(Mode.Description);
  const continuous = ref(false);
  const trackingElement = ref("");

  watch(currentMode, (val) => {
    if (val == Mode.Tracking) {
      trackingElement.value = "";
    }
  })

  return { currentMode, continuous, trackingElement };
});
