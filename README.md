# becomeliminal/assets

Public asset CDN for Liminal — stock logos, brand marks, icons, and other static images used across Liminal product surfaces.

Served at **`https://assets.liminal.cash`**.

## URL convention

```
https://assets.liminal.cash/{category}/{filename}
```

| Example URL | What it serves |
|-------------|----------------|
| `https://assets.liminal.cash/investing/stocks/AAPL.png` | Apple stock logo |
| `https://assets.liminal.cash/liminal/brand/logo.svg` | Liminal full logo |
| `https://assets.liminal.cash/liminal/brand/logo-mark.svg` | Liminal mark only |

URLs are constructible by convention from a known identifier (e.g. a stock ticker), so consumers don't need a manifest lookup at runtime.

## Repo layout

```
liminal/
  brand/                Liminal logos, marks, wordmarks
investing/
  stocks/               Stock logos — one PNG per ticker
```

New top-level categories are added when needed.

## Format conventions

### Stock logos (`investing/stocks/`)

- **Format**: PNG
- **Dimensions**: 512×512
- **Background**: transparent
- **Aspect**: square — letterbox if the source is wider/taller, never crop
- **File size**: < 50 KB (after optimization)
- **Filename**: `{TICKER}.png`, uppercase (e.g. `AAPL.png`, `BRK.B.png`)

### Liminal brand (`liminal/brand/`)

- **Vector marks**: SVG with a `viewBox` attribute, < 100 KB
- **Raster icons**: PNG, square, named with the size suffix (`icon-512.png`, `icon-1024.png`)

CI rejects files that don't meet these constraints.

## Adding an asset

1. Open a pull request that adds the file in the right directory
2. CI validates format, dimensions, and size
3. Vercel builds a preview deployment for the PR — click the preview URL to verify the rendered asset
4. Merge → live at `https://assets.liminal.cash/...` within ~30 seconds

The PR template covers the metadata required (source, license, dimensions).

## Caching

Assets are served with the headers configured in [`vercel.json`](vercel.json):

| Path | `Cache-Control` |
|------|-----------------|
| Image files (`.png`, `.svg`, `.jpg`, `.webp`) | `public, max-age=86400, stale-while-revalidate=604800` |
| `/manifest.json` | `public, max-age=300, must-revalidate` |

To bypass the cache for a one-off urgent change, append a query string at the consumer side (`AAPL.png?v=2`).

## Licensing

- **Repo structure** (this README, scripts, CI workflows, configuration): MIT — see [`LICENSE`](LICENSE).
- **Logos and trademarks** stored here are the property of their respective owners. See [`NOTICE`](NOTICE).

## Trademark takedown

If you represent a trademark owner and want a logo removed, open an issue using the **Trademark takedown** template or contact the address in [`NOTICE`](NOTICE). Legitimate requests are honored within 24 hours.
