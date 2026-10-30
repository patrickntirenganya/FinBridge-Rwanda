/** Shape of the JSON that ui/landing.py injects: translated product copy and page links. No survey data. */
export interface Props {
  lang: "rw" | "en";
  /** Streamlit is in dark mode (ui/theme.py mode()). */
  dark?: boolean;
  /** Copy for the current language; keys are defined in src/i18n.py (home.*). */
  s: Record<string, string>;
  /** Links back to Streamlit pages (opened in the top window). */
  links: { records: string; ussd: string; lender: string; about: string };
}
