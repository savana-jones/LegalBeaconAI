"use client";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";

import Home from "./components/Home";
import Chatbot from "./components/Chatbot";

function App() {
  return (
    <>
      <Router>
        <Routes>
          <Route
            //exact
            path="/"
            element={<Home />}
          />
          <Route path="/chatbot" element={<Chatbot />} />
          {/* If any route mismatches the upper 
          route endpoints then, redirect triggers 
          and redirects app to home component with to="/" */}
          {/* <Redirect to="/" /> */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </>
  );
}

export default App;
