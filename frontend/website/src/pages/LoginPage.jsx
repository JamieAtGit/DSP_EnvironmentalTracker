import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import ModernLayout, { ModernCard, ModernSection, ModernButton, ModernInput } from "../components/ModernLayout";
import Header from "../components/Header";
import Footer from "../components/Footer";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export default function LogOnPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
    fetch(`${BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ username, password })
      })
        .then(res => res.json())
        .then(data => {
          if (data.user.role === "admin") {
            navigate("/admin");
          } else {
            navigate("/");
          }
        })
        .catch(err => {
          console.error("Login failed", err);
    });
  }
      
  return (
    <ModernLayout>
      {{
        nav: <Header />,
        content: (
          <div className="space-y-20">
            <div className="flex items-center justify-center min-h-[60vh]">
              <ModernCard className="max-w-md w-full" solid hover>
                <ModernSection title="Welcome Back" className="text-center">
                  <motion.form 
                    onSubmit={handleLogin} 
                    className="space-y-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                  >
                    <div className="text-center mb-6">
                      <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center shadow-lg">
                        <span className="text-2xl">🔐</span>
                      </div>
                      <p className="text-slate-400 text-sm">
                        Sign in to access your sustainability dashboard
                      </p>
                    </div>

                    <ModernInput
                      label="Username"
                      type="text"
                      placeholder="Enter your username"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      icon="👤"
                      required
                    />
                    
                    <ModernInput
                      label="Password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      icon="🔑"
                      required
                      error={error}
                    />
                    
                    <ModernButton 
                      type="submit"
                      variant="primary"
                      size="lg"
                      className="w-full"
                      icon="🚀"
                    >
                      Sign In
                    </ModernButton>
                  </motion.form>
                  
                  <motion.div
                    className="mt-6 text-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6, delay: 0.4 }}
                  >
                    <p className="text-sm text-slate-400">
                      Don't have an account?{" "}
                      <a 
                        href="/signup" 
                        className="text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
                      >
                        Sign up here
                      </a>
                    </p>
                  </motion.div>
                </ModernSection>
              </ModernCard>
            </div>
            
            <Footer />
          </div>
        ),
      }}
    </ModernLayout>
  );
}
