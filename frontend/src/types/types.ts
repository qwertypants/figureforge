// User & Authentication Types
export interface User {
  id: string;
  email: string;
  username?: string;
  role?: 'admin' | 'user';
  subscription?: Subscription;
  created_at: string;
  updated_at: string;
}

export interface Subscription {
  plan: 'hobby' | 'pro' | 'studio' | string;
  status: 'active' | 'inactive' | 'cancelled' | 'past_due';
  quota_limit: number;
  quota_remaining: number;
  current_period_start: string;
  current_period_end: string;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
}

// Auth store state
export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
  clearError: () => void;
  hasActiveSubscription: () => boolean;
  getQuotaRemaining: () => number;
  isAdmin: () => boolean;
}

// Image & Generation Types
export interface Image {
  id: string;
  url: string;
  thumbnail_url?: string;
  user_id: string;
  prompt?: string;
  parameters?: GenerationParameters;
  created_at: string;
  is_public: boolean;
  is_favorite?: boolean;
}

export interface GenerationParameters {
  batch_size: number;
  body_type: BodyType;
  pose_type: PoseType;
  camera_angle: CameraAngle;
  lighting: LightingType;
  clothing: ClothingType;
  background: BackgroundType;
  ethnicity: EthnicityType;
  age_range: AgeRange;
  gender_presentation: GenderPresentation;
}

// Enum types for generation options
export type BodyType = 'slim' | 'average' | 'athletic' | 'curvy' | 'heavyset';
export type PoseType = 'standing' | 'sitting' | 'action' | 'reclining' | 'gesture';
export type CameraAngle = 'eye_level' | 'low_angle' | 'high_angle' | 'dutch_angle' | 'profile';
export type LightingType = 'studio' | 'natural' | 'dramatic' | 'rim' | 'soft';
export type ClothingType = 'casual' | 'formal' | 'athletic' | 'minimal' | 'traditional';
export type BackgroundType = 'simple' | 'studio' | 'outdoor' | 'abstract' | 'architectural';
export type EthnicityType = 'diverse' | 'african' | 'asian' | 'caucasian' | 'hispanic' | 'middle_eastern' | 'south_asian';
export type AgeRange = 'young_adult' | 'adult' | 'middle_aged' | 'elderly';
export type GenderPresentation = 'androgynous' | 'masculine' | 'feminine';

// Job types
export interface GenerationJob {
  job_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  images?: Image[];
  created_at: string;
  completed_at?: string;
  error?: string;
}

// Image store state
export interface ImageState {
  generationForm: GenerationParameters;
  currentJob: GenerationJob | null;
  jobHistory: GenerationJob[];
  publicImages: Image[];
  userImages: Image[];
  favorites: string[];
  isGenerating: boolean;
  isLoadingGallery: boolean;
  galleryPage: number;
  galleryHasMore: boolean;
  updateGenerationForm: (updates: Partial<GenerationParameters>) => void;
  resetGenerationForm: () => void;
  setCurrentJob: (job: GenerationJob | null) => void;
  addJobToHistory: (job: GenerationJob) => void;
  setIsGenerating: (isGenerating: boolean) => void;
  setPublicImages: (images: Image[], append?: boolean) => void;
  setUserImages: (images: Image[], append?: boolean) => void;
  setFavorites: (favorites: string[]) => void;
  addToFavorites: (imageId: string) => void;
  removeFromFavorites: (imageId: string) => void;
  setIsLoadingGallery: (isLoading: boolean) => void;
  setGalleryPage: (page: number) => void;
  setGalleryHasMore: (hasMore: boolean) => void;
  isFavorited: (imageId: string) => boolean;
}

// Billing & Pricing Types
export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  stripe_price_id: string;
  images_per_month: number;
  features: string[];
  recommended?: boolean;
}

export interface CheckoutSession {
  sessionId: string;
}

export interface BillingPortal {
  url: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  cursor?: string;
  has_more: boolean;
}

export interface ApiError {
  detail: string;
  code?: string;
}

export interface ToggleFavoriteResponse {
  is_favorite: boolean;
}

export interface ReportImageResponse {
  success: boolean;
}

export interface DeleteImageResponse {
  success: boolean;
}

// Component Props Types
export interface ProtectedRouteProps {
  children: React.ReactNode;
}

export interface ImageCardProps {
  image: Image;
  showActions?: boolean;
}

export interface LayoutProps {
  children?: React.ReactNode;
}

// Form/Input types
export interface LoginForm {
  email: string;
  password: string;
}

export interface SignUpForm {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface ReportForm {
  reason: 'inappropriate' | 'copyright' | 'quality' | 'other';
  details: string;
}

export interface UpdateUsernameForm {
  username: string;
}

// UI State Types
export interface Message {
  type: 'success' | 'error' | 'info';
  text: string;
}

export interface LoadingState {
  [key: string]: boolean;
}

// Route Types
export interface LocationState {
  from?: Location;
}

// API Configuration Types
export interface ApiConfig {
  baseURL: string;
  timeout: number;
  headers: {
    'Content-Type': string;
    Authorization?: string;
  };
}