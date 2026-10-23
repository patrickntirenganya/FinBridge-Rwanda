"""Kinyarwanda (default) and English strings.

Stored data is language-neutral: record kinds and items keep their English keys, so a backup
made in one language loads in the other. Only labels shown to people are translated here.

REVIEW NOTE: the Kinyarwanda is a working draft. Native speakers (ideally farmers and SACCO staff)
must review it before field use. Keep every screen short and use words farmers already use.
"""
from __future__ import annotations

LANGS = {"rw": "Kinyarwanda", "en": "English"}
DEFAULT = "rw"

# key: (kinyarwanda, english)
STR: dict[str, tuple[str, str]] = {
    # ---- navigation
    "nav.farmers": ("Ku bahinzi", "For farmers"),
    "nav.evidence": ("Ibimenyetso: imari na politiki", "Evidence for lenders and policy"),
    "nav.records": ("Ibyanditswe by'umurima wanjye", "My farm records"),
    "nav.ussd": ("Kuri telefone isanzwe (USSD)", "Basic-phone (USSD) preview"),
    "nav.overview": ("Incamake", "Overview"),
    "nav.why_records": ("Impamvu y'igikoresho cyo kwandika", "Why a record tool"),
    "nav.who": ("Ubona inguzanyo", "Who gets formal credit"),
    "nav.adjusted": ("Isesengura rirenzeho", "Adjusted associations"),
    "nav.why": ("Intego z'inguzanyo n'inzitizi", "Loan purposes and barriers"),
    "nav.farmers_vs": ("Abahinzi n'abandi bantu bakuru", "Farmers vs other adults"),
    "nav.districts": ("Uturere", "Districts"),
    "nav.actions": ("Icyakorwa", "What to do"),
    "nav.methods": ("Amakuru n'uburyo", "Data and methods"),
    "lang.label": ("Ururimi", "Language"),
    "lang.en_note": ("Iyi paji iri mu Cyongereza. Incamake mu Kinyarwanda iri hejuru.",
                     "This page is in English."),
    # ---- common
    "rwf": ("Frw", "RWF"),
    "yes": ("Yego", "Yes"),
    "kind.harvest": ("Isarura", "Harvest"),
    "kind.sale": ("Igurisha", "Sale"),
    "kind.expense": ("Ikiguzi", "Expense"),
    "kind.saving": ("Ubwizigame", "Saving"),
    "ev.self": ("Byanditswe n'umuhinzi ubwe", "Self-reported"),
    "ev.document": ("Mfite inyemezabwishyu cyangwa ubutumwa bwa Mobile Money (ntibyagenzuwe)",
                    "Receipt or mobile-money message held (not checked)"),
    "ev.confirmed": ("Byemejwe n'uwaguze cyangwa koperative", "Confirmed by buyer or cooperative"),
    "ev.short.self": ("Byanditswe ubwe", "Self-reported"),
    "ev.short.document": ("Mfite inyandiko", "Document held"),
    "ev.title": ("Ibimenyetso", "Evidence"),
    "ev.help": ("«Byemejwe n'uwaguze cyangwa koperative» bizongerwaho igihe abaguzi na koperative bazaba "
                "bashobora kugenzura. Uyu munsi buri cyanditswe ni ijambo ry'umuhinzi.",
                "'Confirmed by buyer or cooperative' will be added once buyers and cooperatives can verify "
                "entries. Today every entry is the farmer's own word."),
    # items (stored as English keys)
    "item.Maize": ("Ibigori", "Maize"), "item.Beans": ("Ibishyimbo", "Beans"),
    "item.Irish potato": ("Ibirayi", "Irish potato"), "item.Cassava": ("Imyumbati", "Cassava"),
    "item.Sorghum": ("Amasaka", "Sorghum"), "item.Rice": ("Umuceri", "Rice"),
    "item.Banana": ("Ibitoki", "Banana"), "item.Coffee": ("Ikawa", "Coffee"),
    "item.Tea": ("Icyayi", "Tea"), "item.Vegetables": ("Imboga", "Vegetables"),
    "item.Milk": ("Amata", "Milk"), "item.Other": ("Ibindi", "Other"),
    "item.Seed": ("Imbuto", "Seed"), "item.Fertiliser": ("Ifumbire", "Fertiliser"),
    "item.Pesticide": ("Umuti wica udukoko", "Pesticide"), "item.Labour": ("Abakozi", "Labour"),
    "item.Transport": ("Ubwikorezi", "Transport"), "item.Equipment": ("Ibikoresho", "Equipment"),
    "item.Land rent": ("Ubukode bw'ubutaka", "Land rent"),
    "item.Loan repayment": ("Kwishyura inguzanyo", "Loan repayment"),
    "item.Savings": ("Ubwizigame", "Savings"),
    "unit.kg": ("kg", "kg"), "unit.litres": ("litiro", "litres"), "unit.count": ("umubare", "count"),
    "season.Season": ("Igihembwe", "Season"),
    # ---- farmer page
    "fr.title": ("Ibyanditswe by'umurima wanjye", "My farm records"),
    "fr.lede": ("Andika icyo wasaruye, wagurishije, wakoresheje n'icyo wazigamye. FinBridge irabikubiyemo ikakubarira "
                "ikanakorera urupapuro rumwe rw'incamake ushobora kwereka banki, SACCO cyangwa ikigo cy'imari iciriritse "
                "nubishaka. Ibyo wanditse bibikwa kuri telefone cyangwa mudasobwa yawe.",
                "Write down what you harvest, sell, spend and save. FinBridge adds it up and makes a one-page "
                "summary that you can show a bank, SACCO or microfinance institution if you choose. Your records "
                "stay on your device."),
    "fr.try": ("Gerageza ukoresheje urugero", "Try with example records"),
    "fr.load": ("Cyangwa shyiramo ibyo wabitse (.json)", "Or load your saved records (.json)"),
    "fr.start": ("Tangira wongeraho icyanditswe cya mbere muri «Kongeramo», cyangwa ugerageze urugero urebe uko bikora.",
                 "Start by adding a first record in the 'Add' tab, or try the example to see how it works."),
    "fr.example_warn": ("Ibi ni ibyanditswe by'urugero byahimbwe, byo kwerekana gusa. Bisibe mbere yo kwandika ibyawe.",
                        "These are invented example records for demonstration. Clear them before adding your own."),
    "fr.clear": ("Siba urugero", "Clear example records"),
    "fr.tab_add": ("1 · Kongeramo", "1 · Add"), "fr.tab_sum": ("2 · Incamake yanjye", "2 · My summary"),
    "fr.tab_share": ("3 · Gusangiza", "3 · Share"),
    "fr.disclaimer": ("FinBridge ntigenzura ibyanditswe, ntiha abahinzi amanota kandi ntifata icyemezo cy'inguzanyo. "
                      "Icyanditswe n'umuhinzi ni ikimenyetso uhitamo gusangiza, si icyemezo cy'amafaranga winjiza "
                      "cyangwa ubushobozi bwo kwishyura.",
                      "FinBridge does not verify entries, score farmers or decide loans. A farmer-entered record is "
                      "evidence the farmer chooses to share, not proof of income or of ability to repay."),
    "fr.bad_file": ("Iyo dosiye ntishobora gusomwa. Koresha iyabitswe muri FinBridge.",
                    "That file could not be read. Use a backup that was downloaded from FinBridge."),
    "fr.loaded": ("Byashyizwemo: {n}.", "Loaded {n} records."),
    "fr.skipped": (" {k} ntibyakoreshwa bityo byasimbutswe.", " {k} could not be used and were skipped."),
    "fr.about": ("Umurima wawe (si itegeko)", "About your farm (optional)"),
    "fr.name": ("Izina", "Name"), "fr.district": ("Akarere", "District"),
    "fr.crops": ("Ibihingwa by'ingenzi", "Main crops"), "fr.ha": ("Ubuso bw'umurima (hegitari)", "Farm size (hectares)"),
    "fr.what": ("Ushaka kwandika iki?", "What do you want to record?"),
    "fr.date": ("Itariki", "Date"), "fr.exp_type": ("Ubwoko bw'ikiguzi", "Type of expense"),
    "fr.crop": ("Igihingwa cyangwa igicuruzwa", "Crop or product"),
    "fr.qty": ("Ingano (si itegeko ku kiguzi)", "Quantity (optional for expenses)"),
    "fr.unit": ("Igipimo", "Unit"), "fr.amount": ("Amafaranga (Frw)", "Amount (RWF)"),
    "fr.who": ("Uwaguze cyangwa uwagurishije (si itegeko)", "Buyer or seller (optional)"),
    "fr.save": ("Bika", "Save record"), "fr.saved": ("Byabitswe.", "Saved."),
    "fr.limit": ("Wagejeje ku mubare ntarengwa w'ibyanditswe. Bika kopi maze utangire dosiye nshya.",
                 "You have reached the limit of records. Download a backup and start a new file."),
    "fr.yours": ("Ibyo wanditse", "Your records"),
    "fr.col.date": ("Itariki", "Date"), "fr.col.kind": ("Ubwoko", "Kind"), "fr.col.item": ("Icyo ari cyo", "Item"),
    "fr.col.qty": ("Ingano", "Qty"), "fr.col.unit": ("Igipimo", "Unit"), "fr.col.rwf": ("Frw", "RWF"),
    "fr.col.with": ("Hamwe na", "With"), "fr.col.ev": ("Ibimenyetso", "Evidence"),
    "fr.remove_label": ("Kuvanaho icyanditswe", "Remove a record"),
    "fr.remove_ph": ("Hitamo icyo uvanaho", "Choose one to remove"), "fr.remove": ("Kuvanaho", "Remove"),
    "fr.sum_empty": ("Banza wandike ibintu. Incamake yawe izagaragara hano.",
                     "Add some records first. Your summary appears here."),
    "fr.period": ("Igihe", "Period"), "fr.all": ("Amatariki yose yanditswe", "All recorded dates"),
    "fr.k_sales": ("amafaranga yavuye mu igurisha", "recorded sales"),
    "fr.k_exp": ("amafaranga yasohotse", "recorded expenses"),
    "fr.k_net": ("igurishijwe ukuyemo ibyakoreshejwe", "sales minus expenses"),
    "fr.k_saved": ("ubwizigame", "saved"),
    "fr.formula": ("Igurishijwe ukuyemo ibyakoreshejwe = igiteranyo cy'amagurisha yanditswe − igiteranyo cy'ibyakoreshejwe "
                   "byanditswe. Habarwa gusa ibyanditswe.",
                   "Sales minus expenses = total of your sale records − total of your expense records. "
                   "Only what you recorded is counted."),
    "fr.chart_in": ("Amafaranga yinjiye (igurisha)", "Money in (sales)"),
    "fr.chart_out": ("Amafaranga yasohotse (ibyakoreshejwe)", "Money out (expenses)"),
    "fr.months": ("Amezi afite nibura icyanditswe kimwe:", "Months with at least one record:"),
    "fr.price": ("Igiciro wabonye ku kilo (amafaranga ÷ kg zagurishijwe)",
                 "Average price you received (sale amount ÷ kg sold)"),
    "fr.price_row": ("{c}: {v} Frw ku kilo", "{c}: {v} RWF per kg"),
    "fr.share": ("Igice cy'umusaruro cyagurishijwe (kg zagurishijwe ÷ kg zasaruwe)",
                 "Share of harvest sold (kg sold ÷ kg harvested)"),
    "fr.evmix": ("Ibimenyetso: {a} byanditswe ubwe · {b} mfite inyandiko · {c} byemejwe n'uwaguze cyangwa koperative",
                 "Evidence mix: {a} self-reported · {b} with a receipt or mobile-money message held · "
                 "{c} confirmed by a buyer or cooperative"),
    "fr.share_empty": ("Banza wandike ibintu. Raporo yawe izagaragara hano.",
                       "Add some records first. Your report appears here."),
    "fr.share_intro": ("Iyi raporo ni iyawe. Yikuremo uyihe ikigo cy'imari nubishaka gusa. FinBridge ntiyohereza "
                       "ahandi.", "This report is yours. Download it and give it to a lender only if you choose to. "
                       "FinBridge does not send it anywhere."),
    "fr.rep_period": ("Igihe cya raporo", "Period for the report"),
    "fr.dl_report": ("Kuramo raporo (.html)", "Download report (.html)"),
    "fr.dl_csv": ("Kuramo ibyanditswe (.csv)", "Download records (.csv)"),
    "fr.dl_json": ("Bika kopi (.json)", "Save a backup (.json)"),
    "fr.dl_note": ("Fungura dosiye ya .html muri browser, uyisohoze cyangwa uyibike nka PDF. Bika kopi kugira ngo "
                   "uzongere ushyiremo ibyawe ubutaha.",
                   "Open the .html file in a browser and print it or save it as PDF. Keep the backup so you can "
                   "load your records again next time."),
    "fr.preview": ("Reba raporo", "Preview the report"),
    "fr.load_bak": ("Shyiramo kopi wabitse (.json)", "Load a saved backup (.json)"),
    "fr.replace": ("Simbuza ibyanditswe byanjye n'iyi kopi", "Replace my current records with this backup"),
    # validation messages
    "v.date": ("Itariki si yo.", "The date is not valid."),
    "v.kind": ("Hitamo ubwoko bw'icyanditswe.", "Choose what kind of record this is."),
    "v.ev": ("Ubwoko bw'ibimenyetso ntibuzwi.", "Evidence type not recognised."),
    "v.amount": ("Andika amafaranga mu Frw.", "Enter the amount in RWF."),
    "v.harvest": ("Andika ingano wasaruye.", "Enter how much you harvested."),
    "v.big_amount": ("Ayo mafaranga asa n'ayabaye menshi cyane.", "That amount looks too large."),
    "v.big_qty": ("Iyo ngano isa n'iyabaye nyinshi cyane.", "That quantity looks too large."),
    "v.item": ("Hitamo igihingwa cyangwa ubwoko bw'ikiguzi.", "Choose a crop or expense type."),
    # ---- ussd page
    "us.title": ("Ibyanditswe bimwe kuri telefone isanzwe", "The same records on a basic phone"),
    "us.lede": ("Abahinzi bakuru bafite telefone igendanwa {own}% ariko {smart}% gusa ni bo bafite telefone igezweho "
                "(smartphone). Umuhinzi udafite smartphone ashobora gukoresha igikoresho kimwe akanda kode ya USSD. "
                "Iyi ni simulation ikora ya menu: ikoresha uburyo bumwe bwo kubika n'ibarura nk'urupapuro rw'urubuga.",
                "Only {smart}% of farming adults own a smartphone, but {own}% own a phone. A farmer without a "
                "smartphone can use the same record tool by dialling a USSD code. This is a working simulation of "
                "that menu: it uses the same record engine and the same totals as the web page."),
    "us.reply": ("Subiza", "Reply"), "us.reply_ph": ("Andika igisubizo cyawe", "Type your reply"),
    "us.send": ("Ohereza", "Send"), "us.dial": ("Ongera ukande kode", "Dial again"),
    "us.try": ("Gerageza: andika `1` (igurisha), `1` (ibigori), `50000` (Frw), `30` (kg). Hanyuma `5` urebe incamake.",
               "Try it: reply `1` (sale), `1` (Maize), `50000` (RWF), `30` (kg). Then reply `5` to see the summary."),
    "us.saved": ("Ibyabitswe muri iki gihe: {n}  \nIgurisha {s} · Ibyakoreshejwe {e}",
                 "Records saved in this session: {n}  \nSales {s} · Expenses {e}"),
    "us.appear": ("Ibyanditswe hano bigaragara kuri paji «Ibyanditswe by'umurima wanjye».",
                  "Records entered here appear on the 'My farm records' page."),
    "us.note": ("Icyitegererezo: nta murongo wa telefone uhujwe. Amagambo yo muri menu agomba kunonosorwa n'abahanga "
                "mu Kinyarwanda mbere yo gukoreshwa.",
                "Prototype: no telecom gateway is connected. Menu text needs review by native speakers before use."),
    # ---- ussd screens (each must stay under 160 characters)
    "u.menu": ("FinBridge\n1 Andika igurisha\n2 Andika ikiguzi\n3 Andika isarura\n4 Andika ubwizigame\n5 Incamake\n0 Sohoka",
               "FinBridge\n1 Record sale\n2 Record expense\n3 Record harvest\n4 Record saving\n5 My summary\n0 Exit"),
    "u.sale_crop": ("Igurisha: igihingwa?", "Sale: crop?"),
    "u.exp_type": ("Ikiguzi: ubwoko?", "Expense: type?"),
    "u.harv_crop": ("Isarura: igihingwa?", "Harvest: crop?"),
    "u.saved_amt": ("Amafaranga wazigamye (Frw)?", "Amount saved (RWF)?"),
    "u.amount": ("Amafaranga (Frw)?", "Amount in RWF?"),
    "u.kg_sold": ("Kg zagurishijwe? (0 usimbuke)", "Kilograms sold? (0 to skip)"),
    "u.kg_harv": ("Kg zasaruwe?", "Kilograms harvested?"),
    "u.num": ("Andika umubare, nka 5000", "Enter a number, like 5000"),
    "u.num_skip": ("Andika umubare, cyangwa 0 usimbuke", "Enter a number, or 0 to skip"),
    "u.pick": ("Hitamo umubare", "Choose a number"),
    "u.choose": ("Hitamo 1-5 cyangwa 0.", "Choose 1-5 or 0."),
    "u.bye": ("Murakoze. Ibyanditswe byabitswe.", "Thank you. Your records are kept."),
    "u.saved": ("Byabitswe nk'ibyanditswe ubwe.", "Saved as self-reported."),
    "u.summary": ("Igurisha {s}\nIkiguzi {e}\nIgisigaye {n}\nUbwizigame {v} Frw\n0 Subira inyuma",
                  "Sales {s}\nExpenses {e}\nNet {n}\nSaved {v} RWF\n0 Back"),
    # ---- report
    "rp.title": ("Incamake y'ibyanditswe by'umurima", "Farm record summary"),
    "rp.example": ("AMAKURU Y'URUGERO. Si umuhinzi nyawe.", "EXAMPLE DATA. Not a real farmer."),
    "rp.farmer": ("Umuhinzi", "Farmer"), "rp.district": ("Akarere", "District"),
    "rp.size": ("Ubuso", "Farm size"), "rp.crops": ("Ibihingwa", "Main crops"),
    "rp.none": ("Ntabyatanzwe", "Not given"),
    "rp.period": ("Igihe", "Period"), "rp.generated": ("Yakozwe", "Generated"),
    "rp.read": ("Soma ibi mbere.", "Read this first."),
    "rp.warn": ("Ibi bivugwa byanditswe n'umuhinzi. FinBridge ntiyabigenzuye kandi ntiha abahinzi amanota cyangwa "
                "ngo isabe ko inguzanyo itangwa. Ikigo cy'imari kigomba kubikoresha hamwe n'igenzura ryacyo bwite.",
                "These figures were entered by the farmer. FinBridge has not verified them and does not score "
                "farmers or recommend whether to lend. A lender should use this alongside its own checks."),
    "rp.entries": ("Ibyanditswe: {a} byanditswe ubwe, {b} bifite inyemezabwishyu cyangwa ubutumwa bwa Mobile Money "
                   "(ntibyagenzuwe), {c} byemejwe n'uwaguze cyangwa koperative.",
                   "Entries: {a} self-reported, {b} with a receipt or mobile-money message held (not checked), "
                   "{c} confirmed by a buyer or cooperative."),
    "rp.totals": ("Igiteranyo", "Totals"),
    "rp.sales": ("Igurisha ryanditswe", "Recorded sales"), "rp.exp": ("Ibyakoreshejwe byanditswe", "Recorded expenses"),
    "rp.net": ("Igurisha ukuyemo ibyakoreshejwe", "Recorded sales minus expenses"),
    "rp.saved": ("Ubwizigame", "Saved"),
    "rp.months": ("Amezi afite nibura icyanditswe kimwe", "Months with at least one record"),
    "rp.formula": ("Igurisha ukuyemo ibyakoreshejwe = igiteranyo cy'amagurisha − igiteranyo cy'ibyakoreshejwe. "
                   "Habarwa gusa ibyanditswe; ibitanditswe ntibikekwa.",
                   "Sales minus expenses = total of sale records − total of expense records. Only what was "
                   "recorded is counted; unrecorded income or costs are not estimated."),
    "rp.by_crop": ("Igurisha ukurikije igihingwa", "Sales by crop"),
    "rp.by_exp": ("Ibyakoreshejwe ukurikije ubwoko", "Expenses by type"),
    "rp.by_month": ("Ukwezi ku kwezi", "Month by month"),
    "rp.month": ("Ukwezi", "Month"), "rp.in": ("Yinjiye", "Money in"), "rp.out": ("Yasohotse", "Money out"),
    "rp.none_rec": ("Nta cyanditswe", "None recorded"),
    "rp.footer": ("Byasangijwe ku bushake bw'umuhinzi. Byakozwe na FinBridge Insights (icyitegererezo cya NISR 2026 "
                  "Big Data Hackathon).",
                  "Shared by the farmer's choice. Generated by FinBridge Insights (NISR 2026 Big Data Hackathon "
                  "prototype)."),
    # ---- overview
    "ov.title": ("Kimwe cya kabiri cy'ingo z'abahinzi mu Rwanda zifite konti mu kigo cy'imari ariko nta nguzanyo",
                 "Half of Rwanda's farm households have a formal account but no formal loan"),
    "ov.lede": ("Ingo nyinshi z'abahinzi zibitsa muri SACCO, banki cyangwa ikigo cy'imari iciriritse. Iyo zikeneye "
                "inguzanyo, zisubira mu bimina no ku nshuti n'abavandimwe. {g}% by'ingo zifite konti ariko nta "
                "nguzanyo yo mu kigo cy'imari (95% CI {lo}–{hi}).",
                "Most agricultural households already save with a SACCO, bank or microfinance institution. When they "
                "need credit, they still turn to tontines and relatives. {g}% of households are banked but not "
                "financed (95% CI {lo}–{hi})."),
    "ov.cta": ("Ndi umuhinzi: tangira kwandika", "I am a farmer: start recording"),
    "ov.seg.Account and formal loan": ("Konti n'inguzanyo y'ikigo cy'imari", "Account and formal loan"),
    "ov.seg.Account, borrowed only informally": ("Konti, inguzanyo zo mu bimina gusa", "Account, borrowed only informally"),
    "ov.seg.Account, did not borrow": ("Konti, nta nguzanyo yafashe", "Account, did not borrow"),
    "ov.seg.No formal account": ("Nta konti mu kigo cy'imari", "No formal account"),
    "ov.hh": ("Ingo z'abahinzi", "Agricultural households"),
    "ov.f1": ("bafite konti muri banki, SACCO cyangwa MFI", "have a bank, SACCO or MFI account"),
    "ov.f2": ("bafite inguzanyo yo muri banki, SACCO cyangwa MFI", "have a loan from a bank, SACCO or MFI"),
    "ov.f3": ("ingo zifite konti ariko zafashe inguzanyo zo mu bimina gusa", "households have an account yet borrowed only informally"),
    "ov.sub": ("Aho ingo z'abahinzi zigurira inguzanyo", "Where agricultural households borrow"),
    "ov.note": ("Igice cy'inguzanyo zose ukurikije aho zikomoka. Icyatsi = ikigo cy'imari kigengwa (banki, SACCO, "
                "ikigo cy'imari iciriritse); umuhondo = ibidasanzwe (ibimina, inshuti); ikijuju = gahunda ya leta "
                "cyangwa umukoresha. Amazina y'inzira ari mu Cyongereza.",
                "Share of all loans, by source. Green = regulated lender (bank, SACCO, microfinance); "
                "ochre = informal; grey = government programme or employer."),
    # ---- hero banner
    "hero.pill": ("NISR 2026 Big Data Hackathon · AHS na FinScope 2024", "NISR 2026 Big Data Hackathon · AHS and FinScope 2024"),
    "hero.title": ("Andika umurima wawe. Erekana ibyo winjiza.", "Record your farm. Show what you earn."),
    "hero.lede": ("Igikoresho cyoroshye kigufasha kwandika isarura, igurisha n'ibyo wakoresheje, ukabona incamake "
                  "ushobora kwereka banki cyangwa SACCO nubishaka. Gikora no kuri telefone isanzwe.",
                  "A simple tool to record harvests, sales and costs, and get a summary you can show a bank or "
                  "SACCO if you choose. It also works on a basic phone."),
    "hero.why": ("Impamvu bikenewe", "Why it is needed"),
    # ---- Kinyarwanda summaries shown above pages that stay in English
    "sum.why_records": ("Incamake: {smart}% gusa by'abahinzi bakuru ni bo bafite smartphone, bityo igikoresho gikeneye "
                        "no kuboneka kuri telefone isanzwe (USSD). Abandika amafaranga yabo buri gihe bafite inguzanyo "
                        "yo mu kigo cy'imari ({a}%) kurusha abayandika rimwe na rimwe ({b}%). Ni isano, si impamvu: "
                        "ntibyemejwe ko kwandika bituma umuntu abona inguzanyo.", ""),
    "sum.adjusted": ("Incamake: iri sesengura rigereranya amatsinda rikurikije ibindi bintu. Ingo ziyobowe n'abagore "
                     "zifite amahirwe (odds) angana n'inshuro {orr} z'ay'ingo ziyobowe n'abagabo yo kubona inguzanyo yo "
                     "mu kigo cy'imari, n'iyo hakurikijwe ubukire, ubuso bw'umurima, ibyangombwa by'ubutaka, koperative "
                     "n'intara. Ni isano, si impamvu.", ""),
    "sum.who": ("Incamake: gereranya ingo z'abahinzi ukurikije ubukire, ubutaka, igitsina cy'umuyobozi w'urugo na "
                "koperative. Ibyavuye ni isano, si impamvu.", ""),
    "sum.why": ("Incamake: ibiribwa ni {food}% by'inguzanyo zose, naho {inp}% gusa by'inguzanyo z'imbuto n'ifumbire "
                "zituruka mu bigo by'imari bigengwa.", ""),
    "sum.farmers": ("Incamake: FinScope ireba abantu bakuru bose, bityo ituma tugereranya abahinzi n'abandi.", ""),
    "sum.districts": ("Incamake: uturere ntitugereranywa ku rutonde. Buri karere gafite ingo nke zabajijwe, bityo "
                      "itandukaniro rito ntirifite agaciro.", ""),
    "sum.actions": ("Incamake: buri nama ihuzwa n'icyavuye mu makuru. Zimwe zifite ibimenyetso bihagije, izindi ni "
                    "ibitekerezo bigomba kubanza kugeragezwa.", ""),
    "sum.methods": ("Incamake: amakuru ni ay'ibarura ry'ingo z'abahinzi (AHS) 2024 na FinScope 2024. Ibyavuye byose "
                    "bikoresha uburemere bw'ibarura kandi bifite intera y'ukuri ya 95%.", ""),
}


def lang() -> str:
    try:
        import streamlit as st
        return st.session_state.get("lang", DEFAULT)
    except Exception:
        return DEFAULT


def t(key: str, lg: str | None = None, **kw) -> str:
    rw, en = STR[key]
    s = en if (lg or lang()) == "en" else rw
    return s.format(**kw) if kw else s


def item(key: str, lg: str | None = None) -> str:
    """Label for a stored item key; unknown keys pass through unchanged."""
    k = f"item.{key}"
    return t(k, lg) if k in STR else key


def season_label(s: str, lg: str | None = None) -> str:
    return s.replace("Season", t("season.Season", lg), 1)
