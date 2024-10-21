import type { Mode } from "@/models/modes";
import axios from "axios";

const url = import.meta.env.VITE_GATEWAY_URL;

async function getTrackingFromImage(image: File, prompt: string) {
  const formData = new FormData();
  formData.append("image", image);
  try {
    const response = await axios.post(url + "/process-tracking", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      params: {
        prompt: prompt,
      },
    });

    return {
      data: response.data.result,
    };
  } catch (err) {
    let error;

    if (axios.isAxiosError(err) && err.response) {
      error = err.response.data.detail;
    } else {
      error = err;
    }

    return {
      error,
    };
  }
}

async function getInfoFromImage(mode: Mode, image: File) {
  const formData = new FormData();

  formData.append("image", image);
  try {
    const response = await axios.post(url + "/process", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      params: {
        mode: mode,
      },
    });

    return {
      data: response.data.result,
    };
  } catch (err) {
    let error;

    if (axios.isAxiosError(err) && err.response) {
      error = err.response.data.detail;
    } else {
      error = err;
    }

    return {
      error,
    };
  }
}

export { getInfoFromImage, getTrackingFromImage };
