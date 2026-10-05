import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router";

import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import AddCard from "./pages/AddCard";
import MakePayment from "./pages/MakePayment";
import Transactions from "./pages/Transactions";
import AdminDashboard from "./pages/AdminDashboard";

import AppLayout from "./components/AppLayout";


function App() {
  return (
    <BrowserRouter>

      <Routes>

        {/* =========================
            PUBLIC ROUTES
        ========================== */}

        <Route
          path="/"
          element={<Navigate to="/login" replace />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />


        {/* =========================
            MAIN APPLICATION
        ========================== */}

        <Route element={<AppLayout />}>

          {/* Dashboard */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />


          {/* My Cards */}

          <Route
            path="/add-card"
            element={<AddCard />}
          />


          {/* Make Payment */}

          <Route
            path="/make-payment"
            element={<MakePayment />}
          />


          {/* Transaction History */}

          <Route
            path="/transactions"
            element={<Transactions />}
          />


          {/* Admin Dashboard */}

          <Route
            path="/admin-dashboard"
            element={<AdminDashboard />}
          />

        </Route>

      </Routes>

    </BrowserRouter>
  );
}

export default App;