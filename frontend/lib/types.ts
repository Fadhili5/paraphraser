// TypeScript types matching backend Pydantic models

// User Registration
export interface UserRegisterRequest {
  username: string;
  email: string;
  password: string;
  phone_number: string;
  recaptcha_token: string;
}

export interface UserRegisterResponse {
  message: string;
  user_id: string;
}

// User Login
export interface UserLoginRequest {
  email: string;
  password: string;
  recaptcha_token: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string; // "bearer"
}

// Paraphrase
export interface ParaphraseRequest {
  text: string;
  mode: string;
}

export interface ParaphraseResponse {
  paraphrased_text: string;
  original_length: number;
  paraphrased_length: number;
}

// API Error Response
export interface ApiErrorResponse {
  detail: string;
}

// Rate Limit Error (special case)
export interface RateLimitError {
  detail: string; // Format: "Rate limit exceeded. Try again in {ttl}s."
}

// User Public (for authenticated user info)
export interface UserPublic {
  id: string;
  username: string;
  email: string;
  phone_number?: string;
  role: string;
}

