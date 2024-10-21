## Frontend application

### Overview

This Vue 3 frontend application uses Pinia for state management and interacts with an API for image processing tasks. The app contains modules for capturing and processing camera images, along with options for various modes, including object tracking and description.

### Technologies Used

- Vue 3: For the frontend UI framework.
- Pinia: For state management, replacing Vuex.
- TypeScript: Strongly typed JavaScript.
- Axios: For making HTTP requests to the backend.
- CSS: For styling, with TailwindCSS for utility-based design (as
indicated by the classes used).

### File Structure

- main.ts: This is the entry point of the application, where the Vue app is created and Pinia is added for state management.
- App.vue: This is the main app component. It loads a CameraView component that handles the camera functionality.
- views/CameraView.vue: This view component organizes the page into sections: one for the camera module, one for the option bar, and another for text description.
- stores/: Pinia stores are used for state management across components.
- api.ts: The API interaction functions are defined here. These functions send an image to the backend to either get general information or perform object tracking. 
  - getTrackingFromImage: Sends the image and the tracking prompt to the server.
  - getInfoFromImage: Sends the image along with the mode for different types of analysis.

### Instructions for Running the Project
1) Clone the repository
2) Install dependencies: ``npm install``      
3) Start the development server: ``npm run dev``
4) Visit http://localhost:5173/ to view the app

### Key Functionalities
- Camera Module: Handles image capture using the CameraView component.
- Options & Modes: User can select modes like description, tracking, or bus. These options are handled via the OptionBar and stored in the useOptionsStore.
- Image Processing: Images are processed using the getInfoFromImage and getTrackingFromImage functions, which interact with a backend API for machine learning tasks.

### Environment Variables
Make sure to set up the following environment variables:
``VITE_GATEWAY_URL=<Backend API URL>``


### Future Improvements
- Add more image processing options.
- Implement better error handling for network issues.
- Enhance UI/UX for better user experience.