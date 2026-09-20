# Content Updates Guide

## Quick Content Changes

### Update Service Cards
Edit `website/index.html`, find the services section:
```html
<div class="service-card">
    <div class="service-icon">☁️</div>
    <h3>Cloud Architecture</h3>
    <p>Your description here...</p>
</div>
```

### Add Portfolio Project
1. Add image to `website/images/portfolio/` (e.g., `my-project.png`)
2. Add HTML block to featured work section:
```html
<div class="project-card">
    <div class="project-image">
        <img src="/images/portfolio/my-project.png" alt="Project description">
    </div>
    <div class="project-content">
        <h3>Project Name</h3>
        <p>Project description...</p>
        <a href="#" class="btn btn-secondary">View →</a>
    </div>
</div>
```

### Deploy After Changes
```bash
python scripts/deploy-assets.py
aws cloudfront create-invalidation --distribution-id DIST_ID --paths "/*"
```

## Common Updates

| Item | File | Change |
|------|------|--------|
| Contact email | index.html | Search "hello@opusmagus.com" |
| Social links | index.html | Update GitHub/LinkedIn URLs |
| Hero text | index.html | Edit `<h1>` in hero section |
| Colors | css/main.css | Edit `:root` CSS variables |

## No rebuild needed - Static files only!
