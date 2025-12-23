import { createContext, useContext } from "react";
import { useUserSession } from "@/hooks/userSession";
import { useNavigate } from "react-router-dom";
import { onLogout } from "@/context/authBus";
import { useEffect } from "react";

// 1️⃣ Define context type
type SessionContextType = ReturnType<typeof useUserSession>;

// 2️⃣ Create the context itself
const UserSessionContext = createContext<SessionContextType | null>(null);

// 3️⃣ Define the Provider component
export function UserSessionProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = useUserSession(); // runs once globally
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to /login when interceptor emits logout
    if (session.user) {
      return onLogout(() => {
        console.log("auto logout");
        session.handleLogout(navigate);
      });
    }
  }, [session, navigate]);
  return (
    <UserSessionContext.Provider value={session}>
      {children}
    </UserSessionContext.Provider>
  );
}

// 4️⃣ Define a convenient consumer hook
// eslint-disable-next-line react-refresh/only-export-components
export function useUser() {
  const ctx = useContext(UserSessionContext);
  if (!ctx)
    throw new Error("useUser must be used inside <UserSessionProvider>");
  return ctx;
}
