import { Navigate } from "react-router-dom";

/**
 * Wraps any route that requires authentication.
 * If not logged in, redirects to /login.
 */
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const isAuth = localStorage.getItem("intellitrace_auth") === "true";
    return isAuth ? <>{children}</> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
