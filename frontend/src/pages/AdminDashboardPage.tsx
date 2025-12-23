// ===============================================
// src/pages/AdminDashboard.tsx
// ===============================================
import React, { useEffect, useState } from "react";
import { adminService } from "@/services/admin_service";
import { useUser } from "@/context/UserSessionProvider";
import useRevealOnScroll from "@/hooks/useRevealOnScroll";
import { useUserSession } from "@/hooks/userSession";
import { useNavigate } from "react-router-dom";
import { User } from "@/types";

const AdminDashboardPage = () => {
    const navigate = useNavigate();
    const { user, loading } = useUserSession();
    const [page, setPage] = useState<number>(1);
    const [perPage, setPerPage] = useState<number>(10);
    const [totalItems, setTotalItems] = useState<number>(0);
    const [search, setSearch] = useState<string>("");
    const [users, setUsers] = useState<User[]>([]);
    const totalPages = Math.ceil(totalItems / perPage); // derived instead of stored
    const [loadingScreen, setLoadingScreen] = useState<boolean>(false);
    

    useEffect(() => {
    if (!loading && !adminService.isAdmin()){
        navigate("/app/dashboard");
    }
    }, [loading, user, navigate]);


    const fetchusers = async (pg: number, limit: number, q: string) => {
        try {
            setLoadingScreen(true);
            const resp = await adminService.fetchUsers(q, pg);
            setUsers(resp.results ?? []);
            setTotalItems(resp.count ?? 0);

        } catch (err) {
            console.error("Failed to fetch users", err);
            setUsers([]);
            setTotalItems(0);
        } finally {
            setLoadingScreen(false);
        }
    };

    const handleDeleteUser = async (uid: string) => {
    if (!window.confirm("Are you sure you want to delete this user?")) return;


    try {
        setLoadingScreen(true);
        await adminService.deleteUser(uid);
        setLoadingScreen(false);
        // Refresh current page
        fetchusers(page, perPage, search);
    } catch (err) {
        console.error("Failed to delete user", err);
        alert("Failed to delete user. See console for details.");
    } 
    };

    useEffect(() => {
        fetchusers(page, perPage, search);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, perPage, search]);

    const onSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setPage(1); // restart from first page on new search
    };

    const goPrev = () => setPage((p) => Math.max(1, p - 1));
    const goNext = () => setPage((p) => Math.min(totalPages, p + 1));
    
    useRevealOnScroll();
    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-4xl mx-auto py-10 px-4">
                <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>

                <form onSubmit={onSearchSubmit} style={{ marginBottom: 12 }}>
                    <input
                        type="search"
                        placeholder="Search users by username or email..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        style={{ padding: 8, width: 320 }}
                        maxLength={1000}
                    />
                    <button type="submit" style={{ marginLeft: 8 }}>
                        Search
                    </button>
                </form>

                <div style={{ marginBottom: 12 }}>
                    <label>
                        Per page:
                        <select
                            value={String(perPage)}
                            onChange={(e) => {
                                const v = Number(e.target.value);
                                if (!Number.isNaN(v) && v > 0) {
                                    setPerPage(v);
                                    setPage(1);
                                }
                            }}
                            style={{ marginLeft: 8 }}
                        >
                            <option value="5">5</option>
                            <option value="10">10</option>
                            <option value="25">25</option>
                            <option value="50">50</option>
                        </select>
                    </label>
                </div>

                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                        <tr>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: 8 }}>ID</th>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: 8 }}>username</th>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: 8 }}>Email</th>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: 8 }}>Admin</th>
                            <th style={{ textAlign: "left", borderBottom: "1px solid #ccc", padding: 8 }}>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.length === 0 ? (
                            <tr>
                                <td colSpan={4} style={{ padding: 12 }}>
                                    No users found.
                                </td>
                            </tr>
                        ) : (
                            users.map((u) => (
                                <tr key={u.id}>
                                    <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{u.id}</td>
                                    <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{u.username}</td>
                                    <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>{u.email}</td>
                                    <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>
                                        {u.is_admin ? "Yes" : "No"}
                                    </td>

                                    <td style={{ padding: 8, borderBottom: "1px solid #eee" }}>
                                    {/* Hide delete button if this is the logged-in user */}
                                    {u.id !== user?.id && !u.is_admin && (
                                        <button
                                        onClick={() => handleDeleteUser(u.id)}
                                        style={{
                                            background: "#e53e3e",
                                            color: "white",
                                            border: "none",
                                            padding: "6px 10px",
                                            borderRadius: 4,
                                            cursor: "pointer",
                                        }}
                                        >
                                        Delete
                                        </button>
                                    )}
                                    </td>
                                    

                                </tr>
                            ))
                        )}
                    </tbody>
                </table>

                <div style={{ marginTop: 12, display: "flex", alignItems: "center", gap: 12 }}>
                    <button onClick={goPrev} disabled={page <= 1}>Prev</button>
                    <span>
                        Page {page} of {totalPages} — {totalItems} users
                    </span>
                    <button onClick={goNext} disabled={page >= totalPages}>Next</button>
                    <label style={{ marginLeft: "auto" }}>
                        Go to page:
                        <input
                            type="number"
                            min={1}
                            max={totalPages}
                            value={String(page)}
                            onChange={(e) => {
                                const v = Number(e.target.value);
                                if (!Number.isNaN(v)) {
                                    const clamped = Math.max(1, Math.min(totalPages, v));
                                    setPage(clamped);
                                }
                            }}
                            style={{ width: 80, marginLeft: 8 }}
                        />
                    </label>
                </div>
            </div>
        {/* 🔥 GLOBAL LOADING OVERLAY 🔥 */}
      {loadingScreen && (
        <div className="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-4 rounded-2xl bg-white px-8 py-6 shadow-xl">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-emerald-700 border-t-transparent"></div>
            <p className="text-slate-700 font-medium text-sm">
              {"Waiting, almost there..."}
            </p>
          </div>
        </div>
      )}
        </div>
    );
    
};

export default AdminDashboardPage;
