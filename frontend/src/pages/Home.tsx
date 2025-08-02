import { Link } from "react-router-dom";
import useAuthStore from "../stores/authStore";

function Home() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="flex flex-col items-center px-4 pt-10 pb-20 min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 leading-tight">
          AI-Powered Figure Drawing References
        </h1>
        <p className="mt-4 text-lg sm:text-xl text-gray-600 max-w-xl mx-auto">
          Generate customizable, SFW human figure references for your art
          practice. Perfect for artists looking to improve their figure drawing
          skills.
        </p>
        <div className="mt-6 flex flex-col sm:flex-row gap-4 justify-center">
          {isAuthenticated ? (
            <Link
              to="/generate"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
            >
              Start Generating
            </Link>
          ) : (
            <>
              <Link
                to="/signup"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-blue-700"
              >
                Get Started
              </Link>
              <Link
                to="/pricing"
                className="bg-white border border-gray-300 text-gray-900 px-6 py-3 rounded-lg text-lg font-medium hover:bg-gray-100"
              >
                View Pricing
              </Link>
            </>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8 w-full max-w-6xl">
        <div className="bg-white p-6 rounded-xl shadow hover:shadow-md transition">
          <img
            src="https://placehold.co/300x200"
            alt="Customizable Poses"
            className="w-full h-40 object-cover rounded-md mb-4"
          />
          <h3 className="text-xl font-semibold mb-2">Customizable Poses</h3>
          <p className="text-gray-600">
            Choose from various poses, body types, and camera angles to match
            your study needs.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow hover:shadow-md transition">
          <img
            src="https://placehold.co/300x200"
            alt="Professional Lighting"
            className="w-full h-40 object-cover rounded-md mb-4"
          />
          <h3 className="text-xl font-semibold mb-2">Professional Lighting</h3>
          <p className="text-gray-600">
            Multiple lighting options to help you understand form, shadow, and
            anatomy.
          </p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow hover:shadow-md transition">
          <img
            src="https://placehold.co/300x200"
            alt="Build Your Library"
            className="w-full h-40 object-cover rounded-md mb-4"
          />
          <h3 className="text-xl font-semibold mb-2">Build Your Library</h3>
          <p className="text-gray-600">
            Save your favorite references and organize them for easy access
            during practice.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Home;
