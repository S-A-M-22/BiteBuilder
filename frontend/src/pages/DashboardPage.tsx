import { motion } from "framer-motion";
import { useDashboardData } from "@/hooks/useDashboardData";
import useRevealOnScroll from "@/hooks/useRevealOnScroll";

import LoadingState from "@/components/LoadingState";
import GoalDashboardSummary from "@/components/Goal/GoalDashboard/GoalDashboardSummary";
import MacroAggregationCard from "@/components/DashBoard/MacroAggregationCard";
import EatenMealsList from "@/components/DashBoard/EatenMealsList";
import DashboardInsights from "@/components/DashBoard/DashBoardInsights";

import MealsList from "@/components/DashBoard/MealsList";
import DashboardMealCard from "@/components/DashBoard/DashboardMealCard";


export default function DashboardPage() {
  useRevealOnScroll();
  
  const { user, goal, goalNutrients, eatenMeals, meals, loading, error, reload } = useDashboardData();

  if (loading) return <LoadingState />;
  if (error) return <p className="text-red-600 p-6">{error}</p>;
  if (!goal) return <p className="p-6">No goal found.</p>;

  return (
    <div className="relative min-h-screen bg-gray-50 text-gray-800">
      <main className="relative max-w-6xl mx-auto p-8 space-y-10">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="space-y-1"
        >
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">
            Welcome back{user?.username ? `, ${user.username}` : ""} 
          </h1>
          <p className="text-gray-500">
            Here's your nutrition overview for today.
          </p>
        </motion.div>

        <motion.section
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.3 }}
      >
        <DashboardInsights
          goal={goal}
          nutrients={goalNutrients}
          eatenMeals={eatenMeals}
          meals={meals}
        />
      </motion.section>

        {/* Summary Row */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          <div className="rounded-2xl bg-white shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all">
            <GoalDashboardSummary goal={goal} nutrients={goalNutrients} />
          </div>

          <div className="rounded-2xl bg-white shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all">
            <MacroAggregationCard eatenMeals={eatenMeals} />
          </div>
        </motion.section>


        {/* Eaten Meals Feed */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="rounded-2xl bg-white shadow-sm border border-gray-200 p-6"
        >
          <EatenMealsList eatenMeals={eatenMeals} onRefresh={reload}/>
        </motion.section>

        {/* Meals List */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.2 }}
          className="rounded-2xl bg-white shadow-sm border border-gray-200 p-6"
        >
          <MealsList Meals={meals} onRefresh={reload}/>
        </motion.section>
      </main>
    </div>
  );
}
