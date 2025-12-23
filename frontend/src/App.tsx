//Contains the main navigation logic
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import PublicRoutes from "./router/PublicRoutes";
import PrivateRoutes from "./router/PrivateRoutes";
import AdminRoutes from "./router/AdminRoutes";
import { UserSessionProvider } from "./context/UserSessionProvider";

export default function AppRoutes() {
  return (
    <Router>
      <UserSessionProvider>
        <Routes>
          <Route path="/*" element={<PublicRoutes />} />
          <Route path="/app/*" element={<PrivateRoutes />} />
          <Route path="/admin/*" element={<AdminRoutes />} />
        </Routes>
      </UserSessionProvider>
    </Router>
  );
}
