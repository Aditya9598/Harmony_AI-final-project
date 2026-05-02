import { Route, Routes } from "react-router-dom";
import { motion } from "framer-motion";
import Navbar from "./components/Navbar";
import HomePage from "./pages/HomePage";
import SkinDetectionPage from "./pages/SkinDetectionPage";
import WellnessChatbotPage from "./pages/WellnessChatbotPage";

export default function App() {
  return (
    <div className="min-h-screen pb-10">
      <Navbar />
      <main className="mx-auto mt-8 w-[95%] max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45 }}
        >
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/skin-detection" element={<SkinDetectionPage />} />
            <Route path="/wellness-chatbot" element={<WellnessChatbotPage />} />
          </Routes>
        </motion.div>
      </main>
    </div>
  );
}
