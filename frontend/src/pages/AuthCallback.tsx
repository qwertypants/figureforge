import { useEffect } from "react";
import { useAuth } from "react-oidc-context";
import { useNavigate } from "react-router-dom";

function AuthCallback() {
  const auth = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    // Handle the callback from Cognito
    if (auth.isAuthenticated) {
      // Redirect to the intended page or default to generate
      const returnTo = sessionStorage.getItem("authReturnTo") || "/generate";
      sessionStorage.removeItem("authReturnTo");
      navigate(returnTo);
    } else if (auth.error) {
      // Handle authentication error
      console.error("Authentication error:", auth.error);
      navigate("/login");
    }
  }, [auth.isAuthenticated, auth.error, navigate]);

  if (auth.isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Completing sign in...</p>
        </div>
      </div>
    );
  }

  return null;
}

export default AuthCallback;
