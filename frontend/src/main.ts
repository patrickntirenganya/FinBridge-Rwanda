import "./style.css";
import type { Props } from "./types";
import beans from "./img/farmer-beans.webp";
import weeding from "./img/farmer-weeding.webp";
import field from "./img/farmer-field.webp";
import call from "./img/farmer-phone-call.webp";
import hands from "./img/hands-phone.webp";

const props: Props = JSON.parse(document.getElementById("fb-data")!.textContent || "{}");
const { s, links } = props;

const btn = (href: string, label: string, primary: boolean) =>
  `<a href="${href}" target="_top" class="inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3.5 text-base font-bold transition hover:-translate-y-0.5 focus-visible:outline focus-visible:outline-4 focus-visible:outline-sorghum ${
    primary ? "bg-sorghum text-tea-deep shadow-lg shadow-black/20 hover:bg-[#d4a23a]"
            : "border border-white/40 text-white hover:bg-white/10"}">${label}<span aria-hidden="true">→</span></a>`;

// ---------------------------------------------------------------- sections
const kicker = (x: string) => `<p class="text-sm font-bold tracking-wide text-sorghum">${x}</p>`;
const tick = (x: string, dark = false) =>
  `<li class="flex gap-3"><span class="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${dark ? "bg-sorghum text-tea-deep" : "bg-tea text-white"} text-sm">✓</span><span class="${dark ? "text-[#DCEBE2]" : "text-slate"}">${x}</span></li>`;

const hero = `
<section class="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-tea-deep via-tea-dark to-tea text-white shadow-2xl shadow-tea-deep/30">
  <div class="grain absolute inset-0"></div>
  <div class="pointer-events-none absolute -right-24 -top-32 h-[420px] w-[420px] rounded-full bg-sorghum/50 blur-3xl"></div>
  <div class="relative grid items-center gap-10 px-6 py-10 sm:px-10 md:grid-cols-[1.1fr_.9fr] md:py-16">
    <div class="animate-rise">
      <span class="inline-block rounded-full border border-white/30 bg-white/10 px-4 py-1.5 text-sm">${s.eyebrow}</span>
      <h1 class="mt-5 text-4xl font-bold leading-[1.08] tracking-tight sm:text-5xl xl:text-6xl">${s.h1}</h1>
      <p class="mt-5 max-w-xl text-lg leading-relaxed text-[#DCEBE2]">${s.lede}</p>
      <div class="mt-8 flex flex-wrap gap-3">${btn(links.records, s.cta_primary, true)}${btn(links.lender, s.cta_secondary, false)}</div>
      <ul class="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-sm text-[#CFE3D6]">
        ${[s.trust1, s.trust2, s.trust3].map(x => `<li class="flex items-center gap-2"><span class="h-2 w-2 rounded-full bg-sorghum"></span>${x}</li>`).join("")}
      </ul>
    </div>
    <div class="relative mx-auto w-full max-w-md animate-rise [animation-delay:.15s]">
      <div class="absolute -inset-3 rotate-3 rounded-[32px] bg-sorghum/70"></div>
      <img src="${beans}" alt="${s.alt_beans}" class="relative aspect-[4/5] w-full rounded-[28px] object-cover object-[40%_30%] shadow-2xl" />
      <div class="absolute -bottom-6 -left-4 w-56 animate-floaty rounded-2xl bg-white p-4 text-ink shadow-xl sm:-left-10">
        <div class="text-base font-bold leading-snug text-tea">${s.card1}</div>
      </div>
      <div class="absolute -right-3 top-6 hidden w-44 rounded-2xl bg-white/95 p-3 text-ink shadow-xl sm:block">
        <div class="text-sm font-bold leading-snug text-soil">${s.card2}</div>
      </div>
    </div>
  </div>
</section>`;

const gapSection = `
<section class="mx-auto mt-24 max-w-5xl reveal">
  ${kicker(s.gap_kicker)}
  <h2 class="mt-2 max-w-3xl text-3xl font-bold leading-tight sm:text-4xl">${s.gap_title}</h2>
  <p class="mt-4 max-w-3xl text-lg leading-relaxed text-slate">${s.gap_body}</p>
  <div class="mt-10 grid gap-5 sm:grid-cols-3">
    ${[[s.g1_t, s.g1_b, "border-sorghum"], [s.g2_t, s.g2_b, "border-tea"], [s.g3_t, s.g3_b, "border-soil"]].map(([h, b, c]) => `
      <div class="rounded-2xl border-l-4 ${c} bg-white p-6 shadow-lg shadow-tea-dark/10">
        <h3 class="text-xl font-bold">${h}</h3><p class="mt-2 text-slate">${b}</p></div>`).join("")}
  </div>
</section>`;

const farmerSection = `
<section class="mx-auto mt-24 grid max-w-6xl items-center gap-10 md:grid-cols-[.8fr_1.2fr] reveal">
  <div class="relative self-start">
    <img src="${field}" alt="${s.alt_field}" class="aspect-square w-full rounded-[28px] object-cover shadow-xl" />
    <img src="${weeding}" alt="${s.alt_weeding}" class="absolute -bottom-8 right-2 w-40 rounded-2xl border-4 border-white object-cover shadow-xl sm:-right-4 sm:w-48" />
  </div>
  <div>
    ${kicker(s.f_kicker)}
    <h2 class="mt-2 text-3xl font-bold leading-tight sm:text-4xl">${s.f_title}</h2>
    <ul class="mt-6 space-y-4 text-lg">${[s.f1, s.f2, s.f3, s.f4].map(x => tick(x)).join("")}</ul>
    <div class="mt-8">${btn(links.records, s.cta_primary, true).replace("bg-sorghum text-tea-deep", "bg-tea text-white hover:!bg-tea-dark")}</div>
  </div>
</section>`;

const lenderSection = `
<section class="relative mt-28 overflow-hidden rounded-[28px] bg-tea-deep text-white shadow-2xl shadow-tea-deep/30 reveal">
  <div class="grid items-center md:grid-cols-[1fr_.9fr]">
    <div class="px-6 py-12 sm:px-10 md:py-16">
      ${kicker(s.l_kicker)}
      <h2 class="mt-2 text-3xl font-bold leading-tight sm:text-4xl">${s.l_title}</h2>
      <ul class="mt-6 space-y-4 text-lg">${[s.l1, s.l2, s.l3, s.l4].map(x => tick(x, true)).join("")}</ul>
      <div class="mt-8">${btn(links.lender, s.l_cta, true)}</div>
    </div>
    <img src="${call}" alt="${s.alt_call}" class="h-full max-h-[460px] min-h-[260px] w-full object-cover" />
  </div>
</section>`;

const phoneSection = `
<section class="relative mt-28 overflow-hidden rounded-[28px] text-white shadow-2xl shadow-tea-deep/30 reveal">
  <img src="${hands}" alt="${s.alt_hands}" class="absolute inset-0 h-full w-full object-cover" />
  <div class="absolute inset-0 bg-gradient-to-r from-tea-deep/95 via-tea-deep/80 to-tea-deep/30"></div>
  <div class="relative grid gap-10 px-6 py-12 sm:px-10 md:grid-cols-[1.1fr_.9fr] md:py-16">
    <div>
      ${kicker(s.phone_kicker)}
      <h2 class="mt-2 max-w-xl text-3xl font-bold leading-tight sm:text-4xl">${s.phone_title}</h2>
      <p class="mt-4 max-w-xl text-lg text-[#DCEBE2]">${s.phone_body}</p>
      <div class="mt-8">${btn(links.ussd, s.phone_cta, true)}</div>
    </div>
    <div class="mx-auto w-full max-w-[250px] self-center" aria-label="${s.ussd_label}">
      <div class="rounded-[28px] border-4 border-[#0f1f18] bg-[#0f1f18] p-3 shadow-2xl">
        <div class="rounded-xl bg-[#CFE3D6] p-4 font-mono text-[13px] leading-relaxed text-[#0f1f18]">
          <div class="mb-2 text-[11px] opacity-70">*123#</div>
          <div>${s.ussd1}</div><div>${s.ussd2}</div><div>${s.ussd3}</div><div>${s.ussd4}</div>
          <div class="mt-2 inline-block animate-pulse">▍</div>
        </div>
        <div class="mt-3 grid grid-cols-3 gap-2 px-1 pb-1 text-center text-xs text-[#9fb5a8]">
          ${"123456789*0#".split("").map(k => `<span class="rounded-md bg-white/5 py-1.5">${k}</span>`).join("")}
        </div>
      </div>
    </div>
  </div>
</section>`;

const steps = [1, 2, 3].map(i => `
  <li class="relative rounded-2xl bg-white p-6 shadow-lg shadow-tea-dark/10 transition hover:-translate-y-1">
    <span class="flex h-11 w-11 items-center justify-center rounded-full bg-tea text-xl font-bold text-white">${i}</span>
    <h3 class="mt-4 text-xl font-bold">${s[`step${i}_t`]}</h3>
    <p class="mt-2 text-slate">${s[`step${i}_b`]}</p>
  </li>`).join("");

const howSection = `
<section class="mx-auto mt-28 max-w-5xl reveal">
  ${kicker(s.how_kicker)}
  <h2 class="mt-2 text-3xl font-bold leading-tight sm:text-4xl">${s.how_title}</h2>
  <ol class="mt-8 grid gap-5 sm:grid-cols-3">${steps}</ol>
</section>`;

const trustSection = `
<section class="mx-auto mt-28 max-w-4xl rounded-[28px] bg-white p-6 shadow-xl shadow-tea-dark/10 sm:p-10 reveal">
  <h2 class="text-3xl font-bold leading-tight">${s.trust_title}</h2>
  <ul class="mt-5 grid gap-3 sm:grid-cols-2">${[1, 2, 3, 4].map(i => tick(s[`trust_${i}`])).join("")}</ul>
  <div class="mt-7"><a href="${links.about}" target="_top" class="inline-flex items-center rounded-xl border border-line px-6 py-3.5 font-bold text-tea hover:bg-mist">${s.cta_about}</a></div>
</section>`;

const footer = `
<footer class="mx-auto mt-16 max-w-4xl pb-6 text-center text-sm leading-relaxed text-slate">
  <p>${s.source}</p><p class="mt-2">${s.credit}</p>
</footer>`;

document.getElementById("root")!.innerHTML =
  `<main class="px-1 pb-4 pt-1">${hero}${gapSection}${farmerSection}${lenderSection}${phoneSection}${howSection}${trustSection}${footer}</main>`;

// ---------------------------------------------------------------- behaviour
const io = new IntersectionObserver(entries => {
  for (const e of entries) {
    if (!e.isIntersecting) continue;
    const el = e.target as HTMLElement;
    el.classList.add("in");
    el.querySelectorAll<HTMLElement>(".bar-fill").forEach(b => (b.style.width = `${b.dataset.w}%`));
    io.unobserve(el);
  }
}, { threshold: 0.15 });
document.querySelectorAll<HTMLElement>(".reveal").forEach(el => io.observe(el));
