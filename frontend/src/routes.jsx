import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Token from "./pages/Token";
import Technology from "./pages/Technology";
import Developers from "./pages/Developers";
import Roadmap from "./pages/Roadmap";
import Terms from "./pages/Terms";
import Privacy from "./pages/Privacy";
import Cookies from "./pages/Cookies";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/token" element={<Token />} />
      <Route path="/technology" element={<Technology />} />
      <Route path="/developers" element={<Developers />} />
      <Route path="/roadmap" element={<Roadmap />} />
      <Route path="/terms" element={<Terms />} />
      <Route path="/privacy" element={<Privacy />} />
      <Route path="/cookies" element={<Cookies />} />
    </Routes>
  );
}