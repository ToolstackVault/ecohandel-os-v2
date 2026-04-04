# ToolStackVault Homepage Redesign — Prompt for Antigravity / Accomplish

## WHAT THIS IS

Redesign the homepage of **ToolStackVault.com** — a dark-themed SaaS affiliate review and comparison website covering WordPress hosting, SEO tools, email marketing, and AI tools. The site runs on **WordPress with the free Kadence theme**. The redesign must use only Kadence (free) blocks, native WordPress functionality, and custom CSS. No paid plugins, no page builders, no custom PHP.

---

## DESIGN REFERENCES (study these closely)

These sites define the visual standard I want. Analyze their scroll behavior, typography, spacing, card design, and animation approach:

1. **linear.app** — THE primary reference. Dark background, scroll-triggered section reveals, glassmorphism cards with subtle border glows, ultra-clean typography, gradient accents. This is the target aesthetic.
2. **vercel.com** — Dark hero with animated/gradient background effect, dual CTAs, staggered fade-up animations on scroll, clean feature sections.
3. **raycast.com** — Bright accent colors on dark canvas, product-focused hero, micro-animations, premium feel.
4. **resend.com** — Minimalist dark design, glow effects, code-inspired aesthetic.
5. **superlist.com** — Dark mode with smooth motion graphics, white typography that pops.

**Key design patterns to extract from these references:**
- Gradient mesh / subtle animated glow backgrounds in hero sections
- Cards with glass-morphism effect (semi-transparent background + backdrop blur + subtle luminous border)
- Scroll-triggered fade-up / scale-in animations using CSS only (Intersection Observer via inline JS is acceptable)
- Hover states with lift effect + glow shadow
- Generous whitespace between sections
- Large display typography for headlines
- Subtle grid/dot pattern backgrounds for depth

---

## CURRENT SITE STRUCTURE (keep this exact content flow)

The homepage currently has these sections in order. **Keep all of them, improve the design:**

### 1. NAVIGATION
- Logo: `https://toolstackvault.com/wp-content/uploads/2026/02/wordmark-dark-bg.png`
- Menu items: Home | Best WordPress Hosting | Best AI Tools | Best Email Marketing | Best SEO Tools | Browse Articles | Best Picks
- Sticky header with blur background on scroll

### 2. HERO SECTION
- Tagline above headline: "Independent reviews • No sponsored rankings"
- Headline: **"Find the Right Tools. Build Faster."**
- Subtitle: "Expert reviews and honest comparisons of the tools that power online business. AI writing, web hosting, SEO, and email marketing — tested and ranked."
- Two CTAs: "Browse Articles →" (links to /blog/) and "Best Picks 2026" (links to /best-picks/)
- **UPGRADE:** Add an animated gradient mesh or subtle particle/glow background behind the hero. Use CSS animations — no heavy JS libraries. The effect should be subtle and performant, not distracting.

### 3. CATEGORY CARDS (Browse by Category)
Four cards linking to cluster hubs:
- 🤖 **AI Tools** — "Writing, video, automation, AI reviews" → /ai/
- 🌐 **Web Hosting** — "WordPress, cloud, and budget hosting" → /hosting/
- ✉️ **Email Marketing** — "Automation & campaign comparisons" → /email/
- 🔎 **SEO Tools** — "Keywords, audits, rank tracking" → /seo/
- **UPGRADE:** Glassmorphism card style. Semi-transparent background, subtle border glow on hover, lift effect. Staggered fade-in on scroll. Each card gets a subtle accent color matching its category (blue for hosting, green for email, purple for AI, orange for SEO).

### 4. LATEST ARTICLES
- Show 6 most recent posts with featured image, title, excerpt, and "Read Article →" link
- **UPGRADE:** Card grid with hover lift + image zoom effect. Fade-up on scroll. Clean card design with dark background, subtle border, rounded corners.
- **NOTE:** The latest articles section should show the most recent WordPress posts automatically. I will configure this with Kadence's Query Loop block or a Latest Posts block. For now, design the visual layout and card style. Auto-refresh of new articles when published is a standard WordPress feature I'll handle separately.

### 5. QUICK COMPARE — TOP PICKS (this is the money section)
Six tool cards with ratings and affiliate CTAs. **Keep all data exactly as-is:**

| Tool | Category | Badge | Rating | Price | CTA Text | CTA Link | Secondary Link |
|------|----------|-------|--------|-------|----------|----------|----------------|
| Kinsta | Hosting | TOP PICK | 9.4/10 | From $35/mo | Try Kinsta → | /go/kinsta | Review → /hosting/kinsta-review-2026-best-managed-wordpress-hosting/ |
| Cloudways | Hosting | BEST VALUE | 9.1/10 | From $14/mo | Try Cloudways → | /go/cloudways | Review → /hosting/cloudways-review-2026-best-managed-cloud-hosting/ |
| ActiveCampaign | Email | FREE TRIAL | 9.4/10 | From $29/mo | Try Free → | /go/activecampaign | All Email Picks → /email/best-email-marketing/ |
| SurferSEO | SEO | — | 9.1/10 | From $89/mo | Try SurferSEO → | /go/surferseo | All SEO Picks → /seo/best-seo-tools/ |
| SEMrush | SEO | — | 9.5/10 | From $129/mo | Try SEMrush → | /go/semrush | Review → /seo/semrush-review-2026-complete-seo-toolkit/ |
| Hostinger | Hosting | — | 8.6/10 | From $2.99/mo | Try Hostinger → | /go/hostinger | All Hosting Picks → /hosting/best-wordpress-hosting/ |

**UPGRADE:** Premium comparison cards with:
- Visual rating bar or ring (not just text)
- Badge system: gold glow for "TOP PICK", green glow for "BEST VALUE", blue for "FREE TRIAL"
- Hover: card lifts with colored shadow matching badge
- Grid layout: 3 columns desktop, 2 tablet, 1 mobile
- All CTA buttons use `rel="nofollow sponsored"` and open in new tab

### 6. NEWSLETTER SECTION
- Title: "Get Weekly Tool Updates"
- Subtitle: "Every Tuesday, no spam"
- Section title: "The Weekly Tool Report"
- Text: "Join founders getting the best tools, deals, and practical tips. Unsubscribe anytime."
- Subscribe button + link to /weekly-tool-updates/
- **UPGRADE:** Glassmorphism card with animated gradient border. Centered layout with generous padding.

### 7. FOOTER
- Links: Best Picks | Browse Articles | Affiliate Disclosure | Editorial Policy | Privacy Policy | About
- Copyright: © 2026 ToolStackVault. All rights reserved.
- **UPGRADE:** Clean dark footer with subtle top border, organized link columns.

---

## TECHNICAL CONSTRAINTS — CRITICAL

1. **WordPress + Kadence (free theme) ONLY.** No Elementor, no Beaver Builder, no paid plugins.
2. All visual upgrades must be achievable with:
   - Kadence theme settings (colors, typography, header/footer builder)
   - Kadence Blocks (free) — Row Layout, Advanced Text, Info Box, Icon List, etc.
   - WordPress core blocks (Query Loop, Latest Posts, Cover, Group, Columns)
   - **Custom CSS** added via Kadence → Customizer → Additional CSS (this is where the magic happens)
   - Small inline JavaScript snippets for scroll animations (Intersection Observer pattern) — added via a Code Snippet plugin or Kadence's custom HTML block
3. **No functionality loss.** Every link, every CTA, every section that exists now must remain functional.
4. **Mobile-first responsive design.** Everything must work perfectly on mobile.
5. **Performance:** No heavy JS animation libraries (no GSAP, no Three.js, no Lottie). Use CSS animations + transitions + Intersection Observer only. The site must stay fast.
6. All external affiliate links use `rel="nofollow sponsored"` with `target="_blank"`.

---

## COLOR SYSTEM

```
--bg-primary: #0B0F1A          (main background)
--bg-card: #111827             (card backgrounds)  
--bg-card-hover: #1a2234       (card hover state)
--border: rgba(255,255,255,0.06)
--border-glow: rgba(99,179,237,0.15)
--text-primary: #F7FAFC        (headlines, primary text)
--text-secondary: #A0AEC0      (body text, descriptions)
--text-muted: #718096           (meta text, labels)
--accent: #63B3ED              (primary blue accent)
--accent-bright: #90CDF4       (bright blue for hover states)
--gold: #F6C76B                (TOP PICK badge, premium elements)
--green: #68D391               (BEST VALUE badge, positive elements)  
--red: #FC8181                 (negative/con elements)
```

**Badge glow colors:**
- TOP PICK: gold glow → `box-shadow: 0 0 20px rgba(246,199,107,0.15)`
- BEST VALUE: green glow → `box-shadow: 0 0 20px rgba(104,211,145,0.15)`
- FREE TRIAL: blue glow → `box-shadow: 0 0 20px rgba(99,179,237,0.15)`

---

## TYPOGRAPHY

- **Display / Headlines:** Use a clean, modern font available in Kadence. Inter or the default system sans-serif stack works. Large sizes (clamp-based for responsiveness).
- **Body text:** Clean sans-serif, 16px base, 1.7 line-height.
- **If the current fonts (Instrument Serif + Satoshi) are available via Google Fonts in Kadence, keep them.** If not, use Inter for both display and body.

---

## CSS ANIMATION PATTERNS TO IMPLEMENT

### Scroll reveal (apply to all major sections):
```css
.reveal {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.6s ease, transform 0.6s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### Staggered children (for card grids):
```css
.reveal.visible .card:nth-child(1) { transition-delay: 0s; }
.reveal.visible .card:nth-child(2) { transition-delay: 0.1s; }
.reveal.visible .card:nth-child(3) { transition-delay: 0.15s; }
.reveal.visible .card:nth-child(4) { transition-delay: 0.2s; }
```

### Intersection Observer (add once via HTML block or snippet):
```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
```

### Hero background glow animation:
```css
.hero-glow {
  position: absolute;
  width: 600px;
  height: 600px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99,179,237,0.08) 0%, transparent 70%);
  animation: float 8s ease-in-out infinite;
  pointer-events: none;
}
@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -20px) scale(1.05); }
  66% { transform: translate(-20px, 15px) scale(0.95); }
}
```

### Card glassmorphism:
```css
.glass-card {
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}
.glass-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(99, 179, 237, 0.1);
  border-color: rgba(99, 179, 237, 0.15);
}
```

---

## AFFILIATE REDIRECT URLS (for reference)

All tool CTAs link to `/go/[slug]` which redirects to the affiliate URL:
- `/go/kinsta` → https://kinsta.com/?kaid=QKPKCDODUBZG
- `/go/cloudways` → https://www.cloudways.com/en/?id=2085394
- `/go/activecampaign` → https://try.activecampaign.com/z35jb72o1ea8-rvs4jt (free trial)
- `/go/surferseo` → (direct link, no affiliate)
- `/go/semrush` → (direct link, no affiliate)  
- `/go/hostinger` → (direct link, no affiliate)

**You don't need to change the redirect URLs — just make sure CTA buttons link to the /go/ slugs.**

---

## WHAT I NEED DELIVERED

1. **Step-by-step implementation guide** for building this in Kadence (free) — which blocks to use, in what order, with what settings.
2. **Complete custom CSS** to paste into Kadence → Customizer → Additional CSS.
3. **JavaScript snippet** for scroll animations (Intersection Observer), to add via a Code Snippet plugin or Kadence HTML block.
4. **Kadence header/footer configuration** instructions.
5. **Mobile responsive adjustments** built into the CSS.

The goal: the homepage should look and feel like a premium, next-level SaaS review site — on par with linear.app and vercel.com in visual quality — while running entirely on free WordPress + Kadence. No functionality should be lost compared to the current site.

---

## SUMMARY OF UPGRADES VS CURRENT SITE

| Current | Upgraded |
|---------|----------|
| Static flat hero | Animated gradient glow background, larger typography |
| Plain category cards | Glassmorphism cards with hover glow + scroll animation |
| Basic article grid | Premium card grid with image zoom, hover lift, fade-up |
| Flat tool comparison cards | Rating bars/rings, badge glow system, hover effects |
| Static newsletter section | Glassmorphism card with gradient border animation |
| No scroll animations | Full scroll-reveal system across all sections |
| Basic sticky header | Blur-background sticky header with smooth transition |
| No visual depth | Layered backgrounds, glows, shadows creating depth |
