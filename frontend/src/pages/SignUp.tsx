import { useState, ChangeEvent, FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import useAuthStore from "../stores/authStore";
import { SignUpForm } from "../types/types";

type Step = "form" | "verify";

function SignUp() {
  const navigate = useNavigate();
  const { signUp, confirmSignUp, resendConfirmationCode } = useAuth();
  const { setError, error } = useAuthStore();
  const [step, setStep] = useState<Step>("form");
  const [formData, setFormData] = useState<SignUpForm>({
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [verificationCode, setVerificationCode] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await signUp(formData.email, formData.password);
      setStep("verify");
    } catch (error: any) {
      if (error.code === "UsernameExistsException") {
        setError("An account with this email already exists");
      } else if (error.code === "InvalidPasswordException") {
        setError(
          "Password does not meet requirements. It must contain uppercase, lowercase, numbers, and symbols.",
        );
      } else {
        setError(error.message || "Failed to sign up");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleVerify = async (e: FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await confirmSignUp(formData.email, verificationCode);
      // After successful verification, redirect to login
      navigate("/login", {
        state: { message: "Account verified successfully! Please sign in." },
      });
    } catch (error: any) {
      if (error.code === "CodeMismatchException") {
        setError("Invalid verification code");
      } else if (error.code === "ExpiredCodeException") {
        setError("Verification code has expired. Please request a new one.");
      } else {
        setError(error.message || "Failed to verify email");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendCode = async () => {
    setIsSubmitting(true);
    setError(null);

    try {
      await resendConfirmationCode(formData.email);
      setError("Verification code sent! Check your email.");
    } catch (error: any) {
      setError(error.message || "Failed to resend code");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (step === "verify") {
    return (
      <div className="max-w-md mx-auto">
        <h2 className="text-3xl font-bold text-center mb-8">Verify Email</h2>
        <p className="text-gray-600 text-center mb-6">
          We've sent a verification code to {formData.email}
        </p>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleVerify} className="space-y-6">
          <div>
            <label
              htmlFor="code"
              className="block text-sm font-medium text-gray-700"
            >
              Verification Code
            </label>
            <input
              type="text"
              id="code"
              required
              value={verificationCode}
              onChange={(e) => setVerificationCode(e.target.value)}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter 6-digit code"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? "Verifying..." : "Verify Email"}
          </button>

          <button
            type="button"
            onClick={handleResendCode}
            disabled={isSubmitting}
            className="w-full text-blue-600 hover:text-blue-500 text-sm"
          >
            Resend verification code
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <h2 className="text-3xl font-bold text-center mb-8">Sign Up</h2>

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700"
          >
            Email
          </label>
          <input
            type="email"
            id="email"
            name="email"
            required
            value={formData.email}
            onChange={handleChange}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your email"
          />
        </div>

        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-gray-700"
          >
            Password
          </label>
          <div className="mt-1 relative">
            <input
              type={showPassword ? "text" : "password"}
              id="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="At least 8 characters"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
          <p className="mt-1 text-sm text-gray-600">
            Must contain uppercase, lowercase, numbers, and symbols
          </p>
        </div>

        <div>
          <label
            htmlFor="confirmPassword"
            className="block text-sm font-medium text-gray-700"
          >
            Confirm Password
          </label>
          <div className="mt-1 relative">
            <input
              type={showConfirmPassword ? "text" : "password"}
              id="confirmPassword"
              name="confirmPassword"
              required
              value={formData.confirmPassword}
              onChange={handleChange}
              className="block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
              placeholder="Re-enter your password"
            />
            <button
              type="button"
              className="absolute inset-y-0 right-0 pr-3 flex items-center"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-5 w-5 text-gray-400" />
              ) : (
                <Eye className="h-5 w-5 text-gray-400" />
              )}
            </button>
          </div>
        </div>

        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSubmitting ? "Creating Account..." : "Sign Up"}
        </button>
      </form>

      <div className="mt-6 text-center text-sm">
        Already have an account?{" "}
        <Link to="/login" className="text-blue-600 hover:text-blue-500">
          Sign in
        </Link>
      </div>
    </div>
  );
}

export default SignUp;
