import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { APropos } from "./screens/APropos/APropos";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <APropos />
  </StrictMode>,
);
