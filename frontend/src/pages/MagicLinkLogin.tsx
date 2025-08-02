import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Mail, ArrowLeft, Loader2 } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import useAuthStore from "../stores/authStore";

export default function MagicLinkLogin() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSent, setIsSent] = useState(false);
  const { requestMagicLink } = useAuth();
  const { error, setError } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await requestMagicLink(email);
      sessionStorage.setItem("magicLinkEmail", email);
      setIsSent(true);
    } catch (err: any) {
      setError(
        err.response?.data?.error || err.message || "Failed to send magic link",
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (isSent) {
    return (
      <div className="max-w-md mx-auto">
        <div className="text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <Mail className="h-6 w-6 text-green-600" />
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">
            Check your email
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            We've sent a magic link to <strong>{email}</strong>
          </p>
          <p className="mt-4 text-sm text-gray-600">
            Click the link in the email to sign in to your account. The link
            will expire in 15 minutes.
          </p>
          <button
            onClick={() => setIsSent(false)}
            className="mt-6 text-blue-600 hover:text-blue-500 text-sm font-medium"
          >
            Didn't receive the email? Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto">
      <div>
        <button
          onClick={() => navigate("/login")}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to login options
        </button>
        <h2 className="text-center text-3xl font-bold text-gray-900">
          Sign in with email
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          We'll send you a magic link to sign in
        </p>
      </div>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-gray-700"
          >
            Email address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Enter your email"
          />
        </div>

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isLoading}
          className="w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Mail className="h-4 w-4 mr-2" />
              Send magic link
            </>
          )}
        </button>
      </form>
    </div>
  );
}
