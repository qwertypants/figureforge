import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Loader2, CheckCircle, XCircle } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import useAuthStore from "../stores/authStore";

export default function MagicLinkCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyMagicLink } = useAuth();
  const { setError } = useAuthStore();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading",
  );
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const verify = async () => {
      const code = searchParams.get("code");
      const email =
        searchParams.get("email") || sessionStorage.getItem("magicLinkEmail");

      if (!code || !email) {
        setStatus("error");
        setErrorMessage("Invalid magic link");
        return;
      }

      try {
        await verifyMagicLink(email, code);
        setStatus("success");

        // Clear session storage
        sessionStorage.removeItem("magicLinkEmail");

        // Redirect after a short delay
        setTimeout(() => {
          const redirectPath =
            sessionStorage.getItem("redirectAfterLogin") || "/generate";
          sessionStorage.removeItem("redirectAfterLogin");
          navigate(redirectPath);
        }, 1500);
      } catch (err: any) {
        setStatus("error");
        setErrorMessage(
          err.response?.data?.error ||
            err.message ||
            "Failed to verify magic link",
        );
      }
    };

    verify();
  }, [searchParams, navigate, verifyMagicLink]);

  return (
    <div className="max-w-md mx-auto">
      <div className="text-center">
        {status === "loading" && (
          <>
            <Loader2 className="mx-auto h-12 w-12 text-blue-600 animate-spin" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Verifying your magic link...
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Please wait while we sign you in
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle className="mx-auto h-12 w-12 text-green-600" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">Success!</h2>
            <p className="mt-2 text-sm text-gray-600">
              You've been signed in. Redirecting...
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <XCircle className="mx-auto h-12 w-12 text-red-600" />
            <h2 className="mt-6 text-3xl font-bold text-gray-900">
              Verification failed
            </h2>
            <p className="mt-2 text-sm text-red-600">{errorMessage}</p>
            <button
              onClick={() => navigate("/login/magic-link")}
              className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Request new magic link
            </button>
          </>
        )}
      </div>
    </div>
  );
}
