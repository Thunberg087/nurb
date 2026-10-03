import { getCurrentWindow } from "@tauri-apps/api/window";

const THEME_KEY = "nurb-theme";

export type Theme = "dark" | "light";

export function readTheme(): Theme {
  return localStorage.getItem(THEME_KEY) === "light" ? "light" : "dark";
}

export function writeTheme(theme: Theme) {
  if (theme === "light") localStorage.setItem(THEME_KEY, "light");
  else localStorage.removeItem(THEME_KEY);
  applyDocumentTheme(theme);
}

export function applyDocumentTheme(theme: Theme = readTheme()) {
  if (theme === "light") document.documentElement.dataset.theme = "light";
  else delete document.documentElement.dataset.theme;
}

export async function syncNativeTheme(theme: Theme) {
  try {
    await getCurrentWindow().setTheme(theme);
  } catch {
    // Vite dev in a browser, or set_theme denied.
  }
}

export function postThemeToViewer(
  frame: HTMLIFrameElement | null,
  origin: string,
  theme: Theme = readTheme(),
) {
  frame?.contentWindow?.postMessage({ type: "nurb:theme", theme }, origin);
}
