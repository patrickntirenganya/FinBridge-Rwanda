// Copy the single-file build to where the Streamlit app reads it.
import { copyFileSync, mkdirSync } from "node:fs";
mkdirSync("../ui/landing", { recursive: true });
copyFileSync("dist/index.html", "../ui/landing/landing.html");
console.log("published -> ui/landing/landing.html");
