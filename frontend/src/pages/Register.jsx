import { useState } from "react";

function Register() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    const { name, value } = event.target;

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    setMessage("");
    setError("");

    if (!formData.username || !formData.email || !formData.password) {
      setError("Please fill in all fields.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/api/register/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(formData),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        if (typeof data === "object") {
          const firstError = Object.values(data).flat()[0];
          throw new Error(firstError || "Registration failed.");
        }

        throw new Error("Registration failed.");
      }

      setMessage(
        data.message || "Registration successful."
      );

      setFormData({
        username: "",
        email: "",
        password: "",
      });
    } catch (err) {
      setError(
        err.message || "Unable to register. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center px-4 py-10">
      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-xl overflow-hidden grid md:grid-cols-2">

        {/* Left Section */}
        <div className="hidden md:flex bg-slate-900 text-white p-10 flex-col justify-between">
          <div>
            <div className="mb-8">
              <p className="text-sm uppercase tracking-[0.25em] text-slate-400">
                Secure Payments
              </p>

              <h1 className="text-4xl font-bold mt-3 leading-tight">
                Credit Card
                <br />
                Payment System
              </h1>
            </div>

            <p className="text-slate-300 leading-7 max-w-md">
              Create your account to manage saved cards,
              make payments, and track your transactions
              from one secure dashboard.
            </p>
          </div>

          <div className="mt-10">
            <div className="h-2 w-20 bg-white rounded-full mb-4"></div>

            <p className="text-sm text-slate-400">
              Secure authentication and protected payment
              operations.
            </p>
          </div>
        </div>

        {/* Register Form */}
        <div className="p-8 sm:p-10 lg:p-12">
          <div className="max-w-md mx-auto">

            <div className="mb-8">
              <p className="text-sm font-semibold text-slate-500">
                Create Account
              </p>

              <h2 className="text-3xl font-bold text-slate-900 mt-2">
                Register
              </h2>

              <p className="text-slate-500 mt-2">
                Enter your details to create your account.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">

              {/* Username */}
              <div>
                <label
                  htmlFor="username"
                  className="block text-sm font-medium text-slate-700 mb-2"
                >
                  Username
                </label>

                <input
                  id="username"
                  name="username"
                  type="text"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="Enter username"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="block text-sm font-medium text-slate-700 mb-2"
                >
                  Email
                </label>

                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter email"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              {/* Password */}
              <div>
                <label
                  htmlFor="password"
                  className="block text-sm font-medium text-slate-700 mb-2"
                >
                  Password
                </label>

                <input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Enter password"
                  className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-slate-900 focus:ring-2 focus:ring-slate-200"
                />
              </div>

              {/* Error */}
              {error && (
                <div className="rounded-xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              {/* Success */}
              {message && (
                <div className="rounded-xl bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
                  {message}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-xl bg-slate-900 px-4 py-3.5 text-white font-semibold transition hover:bg-slate-800 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {loading ? "Creating Account..." : "Create Account"}
              </button>

            </form>

            <p className="text-center text-sm text-slate-500 mt-6">
              Login page will be added next.
            </p>

          </div>
        </div>
      </div>
    </div>
  );
}

export default Register;