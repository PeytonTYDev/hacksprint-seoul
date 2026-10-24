# SC Mobile home: dark redesign

Mobbin MCP workshop, Designed Minds Seoul, 24 October 2026.
Redesign of the SC제일은행 SC Mobile home screen for personal banking customers.

- Live: https://mine-ten-mocha.vercel.app (English: https://mine-ten-mocha.vercel.app/?lang=en)
- Source: `mine/index.html` (plain HTML and CSS, Korean and English, images in `mine/assets/`)
- Before: `template/index.html` in the workshop kit (not in this repo), screenshots in `template/screens/01.png` to `05.png`

## The problems

Customers listed seven complaints. These five hurt most when you only want to check your balance or send money:

1. **An ad comes first.** A 199pt Liverpool FC banner plus three shortcut icons push the accounts card about 400pt down the screen.
2. **The one real balance is buried.** 99,749원 sits in a row the same size as seven rows reading 0개, 0원 or 확인하기.
3. **Transfer is hard to reach.** No 이체 button on the account card. The only way in is a small bottom tab, next to a raised SC logo circle for 홈, the page you are already on.
4. **Log out is the loudest button.** A black, high-contrast 로그아웃 button in the sticky top bar, easy to tap by mistake.
5. **글로벌시황 (global markets) takes prime space.** A full shortcut above the accounts that few people need.

Also on the list, below the accounts card: cards you hold never appear (현대카드 0개 while the app sells new cards), and 12 event and content cards in one long list.

## Research (Mobbin MCP, iOS)

Searches: `search_screens` (deep, twice), `search_flows`, `search_sections`, plus named searches for Toss and KakaoBank and a dark-mode pass.

| Reference | What it shows |
|---|---|
| [N26 home](https://mobbin.com/screens/52ecfd8a-5c0a-4a0d-bf1f-518ee3b88767) | Balance card, then Add money and Send money as the two big actions |
| [X Money](https://mobbin.com/screens/dc29dc0a-6428-4e28-a1a9-3e9b37ca6919) | Large total balance, then Deposit / Send / Request / Transfer tiles |
| [Wise home](https://mobbin.com/screens/0a9eff62-9a44-4f72-b5db-b4d2f6e1f564) | Send / Add money / Request pills above the balance cards |
| [Ubank accounts](https://mobbin.com/screens/629bbcac-8691-4445-8c5f-f39e850e91f8) | Total cash, then only the accounts that hold money |
| [Lloyds Everyday](https://mobbin.com/screens/4d8d6934-b6f3-4918-bf10-a40cc3c96ed3) | The customer's own credit card shown before the upsell |
| [Toss home](https://mobbin.com/screens/b5315413-f78c-4e36-9d05-316633c10e7c) | Each account row has its own 송금 (send) button |
| [Toss home, scrolled](https://mobbin.com/screens/44c0d237-000a-4dac-8b60-c9b19b80366a) | Offers grouped into one small card below the money |
| [KakaoBank home](https://mobbin.com/screens/04517e3b-abac-4250-8af0-433d2c26d7de) | Main account as a large card with 카드 and 이체 buttons on it |
| [KOHO home (dark)](https://mobbin.com/screens/e49dff2c-e073-421b-8a2f-17458c37f3cd) | Spendable balance, then Add / Send / Cards pills |
| [Zing home (dark)](https://mobbin.com/screens/72ab6951-e0ed-4a1d-9f62-67cfc22ebdd8) | Send money as one of three big tiles, no ad banner |

Section results (`search_sections`) only cover marketing websites, so they were weaker references than the iOS screens.

## Picks

1. **[Revolut home](https://mobbin.com/screens/9e4593eb-6c61-4722-ac2d-6e8148fedd38)**: one balance in large type on a dark gradient, the actions directly under it, a flat tab bar. Fixes the buried balance, the ad-first layout and the raised circle.
2. **[Revolut "Sending money" flow](https://mobbin.com/flows/c4a1fcdc-9763-40cb-8470-3ca850e88da2)**: a white "→ Send" button and a dark "Review transfer" screen made of grouped cards. Shapes the 이체 button and the dark card system.

## Design direction

**One balance, one action, then everything else.**

- **Money first, selling last.** Balance, then transfer, accounts, cards, personal items, events, products. The template ran ad, shortcuts, accounts, product sales, then 12 promo cards.
- **One clear focal point.** The only large number is 99,749원. The only white button is 이체.
- **Dark grouped cards.** Each kind of content gets its own titled card, like Revolut's Review transfer screen.
- **Quiet for empty, loud for real.** 0원 and 0개 are dim grey. 확인하기 is blue because it leads somewhere.
- **SC identity kept.** The header gradient uses SC blue, not Revolut purple. Every label, date and title from the template stays, in Korean and English.

## What changed

| Complaint | Change |
|---|---|
| Liverpool FC ad first | Banner removed. The balance is the first thing on screen. The Soccer School event stays once in the events row. |
| 8 equal rows, mostly 0 | 99,749원 moved to the header in large type. Six accounts became small grey tiles in a 2×3 grid. |
| 이체 is a small tab | White 이체 button directly under the balance. The tab stays. |
| Raised circle in the tab bar | Five equal flat tabs. |
| Black 로그아웃 on home | Moved to a quiet text link at the bottom of the page. |
| 글로벌시황 shortcut | Removed. 혜택 and 마이데이터 became small buttons beside 이체. |
| Cards you hold never appear | New "내 카드 / My cards" section. 현대카드 0개, so an empty state with one action: 카드 만들기 / Get a card. |
| 12 cards in one list | 4 short "홍길동님을 위한 소식 / For Hong Gildong" rows and 1 sideways row of 8 events. |
| Product strip mid-screen | Five text chips near the bottom under "상품 둘러보기 / Browse products". |

**Removed:** the Liverpool FC hero banner, the 글로벌시황 shortcut, the decorative gradient strip beside the accounts card, the raised logo image (`nav-home.png`), and the product and quick-link icon images.

**Dark-mode asset fix:** none of the template PNGs are transparent. Product and quick-link icons had white backgrounds, so they became text chips and line icons. The character images sit on tiles of their own baked-in tint (cyan or yellow).

**Text added:** section headings, the 8개 events count and the empty-cards message. No new balances, cards, transactions or events.

## Still open

- 이체 doesn't lead anywhere yet. The transfer flow itself was out of scope.
- Products are demoted to chips, not removed. They could live only in the 상품 tab.
- 편한뱅킹 (easy mode) has no design of its own.
- The dim grey on zero tiles is deliberately low-contrast and hasn't been checked against accessibility minimums.

## Updating the live site

From this folder: `npx vercel deploy mine --prod`. It redeploys to the same URL (Vercel project `mine`, team `mystflo-platform`).
