import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  const navItems = [
    { path: "/", label: "Home", icon: "🏠" },
    { path: "/learn", label: "Learn", icon: "📖" },
    { path: "/predict", label: "Predict", icon: "📊" },
    { path: "/login", label: "Login", icon: "👤" },
    { path: "/extension", label: "Extension", icon: "🔗" },
  ];

  return (
    <>
      {/* Logo/Brand */}
      <motion.div
        className="flex items-center gap-3"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg">
          <span className="text-xl">🌿</span>
        </div>
        <h1 className="text-xl font-display font-bold">
          <span className="text-slate-200">Impact</span>{" "}
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">Tracker</span>
        </h1>
      </motion.div>

      {/* Desktop Navigation */}
      <nav className="hidden md:flex items-center gap-1">
        {navItems.map((item, index) => (
          <motion.div
            key={item.path}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
          >
            <Link
              to={item.path}
              className={`nav-link flex items-center gap-2 ${
                location.pathname === item.path ? "active" : ""
              }`}
            >
              <span className="text-sm">{item.icon}</span>
              <span className="text-sm font-medium">{item.label}</span>
            </Link>
          </motion.div>
        ))}
      </nav>

      {/* Mobile Menu Button */}
      <motion.button
        className="md:hidden w-10 h-10 glass-card flex items-center justify-center rounded-lg"
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        whileTap={{ scale: 0.95 }}
      >
        <div className="flex flex-col gap-1.5">
          <motion.div
            className="w-5 h-0.5 bg-slate-300 rounded-full"
            animate={{ 
              rotate: isMenuOpen ? 45 : 0, 
              y: isMenuOpen ? 3 : 0,
              originX: 0.5,
              originY: 0.5 
            }}
            transition={{ duration: 0.3 }}
          />
          <motion.div
            className="w-5 h-0.5 bg-slate-300 rounded-full"
            animate={{ opacity: isMenuOpen ? 0 : 1 }}
            transition={{ duration: 0.2 }}
          />
          <motion.div
            className="w-5 h-0.5 bg-slate-300 rounded-full"
            animate={{ 
              rotate: isMenuOpen ? -45 : 0, 
              y: isMenuOpen ? -3 : 0,
              originX: 0.5,
              originY: 0.5 
            }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </motion.button>

      {/* Mobile Navigation Menu */}
      <AnimatePresence>
        {isMenuOpen && (
          <motion.div
            className="md:hidden absolute top-full left-0 right-0 mt-2 glass-card p-4"
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            transition={{ duration: 0.3 }}
          >
            <nav className="flex flex-col gap-1">
              {navItems.map((item, index) => (
                <motion.div
                  key={item.path}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                >
                  <Link
                    to={item.path}
                    className={`nav-link flex items-center gap-3 w-full ${
                      location.pathname === item.path ? "active" : ""
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <span>{item.icon}</span>
                    <span className="font-medium">{item.label}</span>
                  </Link>
                </motion.div>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
