import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Chat from "./pages/Chat";
import UpgradeSuccess from "./pages/UpgradeSuccess";
import UpgradeCancelled from "./pages/UpgradeCancelled";

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<Navigate to="/chat" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route
            path="/chat"
            element={
              <ProtectedRoute>
                <Chat />
              </ProtectedRoute>
            }
          />
          <Route path="/upgrade-success" element={<UpgradeSuccess />} />
          <Route path="/upgrade-cancelled" element={<UpgradeCancelled />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
