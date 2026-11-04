# MuseAi YouTube Rewinds static site plan

## Scope

Add a static, no-build marketing and demo site under `site/` for deployment through GitHub Pages or Cloudflare Pages/Workers. The site must work from relative URLs, use no runtime server, and keep every call-to-action as a real HTML navigation target.

## Design

Three style directions considered: **Animated scrapbook / music-zine** (0.62), **dark cyber-audio console** (0.24), and **quiet archival library** (0.14). The chosen direction is animated scrapbook / music-zine.

- **Design movement:** playful indie editorial landing page with poster-like panels, offset borders, tape/sticker details, and kinetic marquee motion.
- **Core principles:** funny before polished, tactile layered surfaces, readable contrast, and movement that rewards scrolling without blocking content.
- **Color philosophy:** warm paper is the calm base; violet is the ownable MuseAi signal; coral and lime are comic accents that make the data feel alive.
- **Layout paradigm:** an asymmetric editorial rail with alternating wide and narrow panels rather than a centered SaaS grid.
- **Signature elements:** wobbly sticker labels, a looping cassette/timeline line, and oversized numbered stats.
- **Interaction philosophy:** links feel like pasted labels and are always real relative HTML routes; hover lift and small rotations provide feedback, while reduced-motion users get a calm version.
- **Animation:** reveal-on-scroll, floating sticker drift, ticker marquee, waveform pulse, and cursor-following glow; all disabled or reduced through `prefers-reduced-motion`.
- **Typography system:** `Space Grotesk` for headlines, `DM Sans` for body copy, and a compact mono treatment for command/output labels.
- **Brand essence:** Your listening past, reconstructed from your own history; witty, local, slightly nosy.
- **Brand voice:** punchy and self-aware. Example lines: “Your algorithm forgot. Your history kept receipts.” and “One listen is not a personality. It is an appendix.”
- **Wordmark & logo:** a looping rewind arrow wrapped around a tiny music note, rendered as a symbol favicon rather than a lettermark.
- **Signature brand color:** electric violet `#6C4BFF`.

## Structure

`site/index.html` is the campaign landing page. `site/demo.html` is a static sample-output walkthrough. `site/about.html` explains privacy and the local-first model. `site/privacy.html` is the plain-language privacy page. `site/404.html` handles missing GitHub Pages/Cloudflare routes. `site/assets/` stores the symbol favicon and promotional illustrations. `site/styles.css` and `site/app.js` provide shared presentation and progressive enhancement.

Deployment support uses relative links, a `site/manus-routes.json` manifest, `_headers` for Cloudflare Pages, and `_redirects` for friendly static redirects. No API keys, analytics, or server endpoints are embedded.
