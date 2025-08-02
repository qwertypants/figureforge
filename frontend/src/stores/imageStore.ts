import { create } from "zustand";
import { ImageState } from "../types/types";

const useImageStore = create<ImageState>((set, get) => ({
  // Image generation state
  generationForm: {
    batch_size: 1,
    body_type: "average",
    pose_type: "standing",
    camera_angle: "eye_level",
    lighting: "studio",
    clothing: "casual",
    background: "simple",
    ethnicity: "diverse",
    age_range: "adult",
    gender_presentation: "androgynous",
  },

  currentJob: null,
  jobHistory: [],

  // Gallery state
  publicImages: [],
  userImages: [],
  favorites: [],

  // UI state
  isGenerating: false,
  isLoadingGallery: false,
  galleryPage: 1,
  galleryHasMore: true,

  // Actions
  updateGenerationForm: (updates) =>
    set((state) => ({
      generationForm: { ...state.generationForm, ...updates },
    })),

  resetGenerationForm: () =>
    set(() => ({
      generationForm: {
        batch_size: 1,
        body_type: "average",
        pose_type: "standing",
        camera_angle: "eye_level",
        lighting: "studio",
        clothing: "casual",
        background: "simple",
        ethnicity: "diverse",
        age_range: "adult",
        gender_presentation: "androgynous",
      },
    })),

  setCurrentJob: (job) => set({ currentJob: job }),

  addJobToHistory: (job) =>
    set((state) => ({
      jobHistory: [job, ...state.jobHistory].slice(0, 50), // Keep last 50 jobs
    })),

  setIsGenerating: (isGenerating) => set({ isGenerating }),

  // Gallery actions
  setPublicImages: (images, append = false) =>
    set((state) => ({
      publicImages: append ? [...state.publicImages, ...images] : images,
    })),

  setUserImages: (images, append = false) =>
    set((state) => ({
      userImages: append ? [...state.userImages, ...images] : images,
    })),

  setFavorites: (favorites) => set({ favorites }),

  addToFavorites: (imageId) =>
    set((state) => ({
      favorites: [...state.favorites, imageId],
    })),

  removeFromFavorites: (imageId) =>
    set((state) => ({
      favorites: state.favorites.filter((id) => id !== imageId),
    })),

  setIsLoadingGallery: (isLoading) => set({ isLoadingGallery: isLoading }),

  setGalleryPage: (page) => set({ galleryPage: page }),

  setGalleryHasMore: (hasMore) => set({ galleryHasMore: hasMore }),

  // Helper to check if image is favorited
  isFavorited: (imageId) => {
    const { favorites } = get();
    return favorites.includes(imageId);
  },
}));

export default useImageStore;
