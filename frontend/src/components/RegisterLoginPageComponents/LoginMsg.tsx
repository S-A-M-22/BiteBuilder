import React from "react";

const LoginMsgComp = () => {
  return (
    <div className="order-2 lg:order-1">
      <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
        <span>Welcome back</span>
      </div>
      <h1 className="mt-4 text-4xl sm:text-5xl font-extrabold tracking-tight text-slate-900">
        Log in to <span className="text-emerald-600">eat smarter</span>
      </h1>
      <p className="mt-4 max-w-xl text-slate-600">
        Pick up where you left off — goals, meals, prices, and your pantry are
        synced across devices.
      </p>
    </div>
  );
};

export default LoginMsgComp;
