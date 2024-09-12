import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <main className="font-serif min-h-screen p-40">
      <div className="flex flex-col items-center justify-between">
        <div className="text-6xl text-center">Welcome to LegalBeacon AI</div>
        <div className="text-xl text-center p-10 mb-16">
          Empowering Your Legal Journey with Instant, Expert Assistance.
        </div>
        <Link to="/chatbot">
          <button className="text-2xl p-4 border border-gray-800 rounded-lg hover:bg-gray-500 transition-colors">
            Get Started
          </button>
        </Link>
      </div>
    </main>
  );
};
export default Home;
