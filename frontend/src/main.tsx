import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { HashRouter } from "react-router-dom";
import "./index.css";
import { App } from "./App";

// HashRouter is chosen over BrowserRouter because GitHub Pages does not
// rewrite unknown paths to index.html, which would break deep links.

const container = document.getElementById("root");
if (!container) {
  throw new Error("Missing #root container in index.html");
}

createRoot(container).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
);
