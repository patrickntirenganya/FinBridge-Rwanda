/** Shape of the JSON that ui/landing.py injects. Every number comes from data/aggregates; none is typed here. */
export interface Stat { name: string; est: number; lo: number; hi: number; n: number }
export interface Pair { title: string; a: Stat; b: Stat }

export interface Props {
  lang: "rw" | "en";
  /** Copy for the current language; keys are defined in src/i18n.py (home.*). */
  s: Record<string, string>;
  n: {
    acct: number; loan: number; gap: number; gapLo: number; gapHi: number;
    informal: number; informalK: number; households: number;
    smart: number; phone: number; momo: number; tracks: number;
  };
  pairs: Pair[];
  /** Links back to Streamlit pages (opened in the top window). */
  links: { records: string; ussd: string; overview: string; actions: string };
}
