# Create SVG placeholder images
@"
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#d4af37;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#grad)"/>
  <text x="200" y="150" font-size="40" fill="white" text-anchor="middle" font-weight="bold">Opus Magus Academy</text>
  <text x="200" y="200" font-size="20" fill="white" text-anchor="middle">E-Learning Platform</text>
</svg>
"@ | Out-File d:\github\OpusMagusWeb\website\images\portfolio\academy.svg -Encoding UTF8

@"
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#d4af37;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#grad)"/>
  <text x="200" y="150" font-size="40" fill="white" text-anchor="middle" font-weight="bold">Cloud Platform</text>
  <text x="200" y="200" font-size="20" fill="white" text-anchor="middle">Enterprise Infrastructure</text>
</svg>
"@ | Out-File d:\github\OpusMagusWeb\website\images\portfolio\platform.svg -Encoding UTF8

@"
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#7c3aed;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#d4af37;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="400" height="300" fill="url(#grad)"/>
  <text x="200" y="150" font-size="40" fill="white" text-anchor="middle" font-weight="bold">AI Analytics</text>
  <text x="200" y="200" font-size="20" fill="white" text-anchor="middle">Real-time Insights</text>
</svg>
"@ | Out-File d:\github\OpusMagusWeb\website\images\portfolio\ai-system.svg -Encoding UTF8

# Create favicon (minimal base64)
$favicon = @"
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
"@
[Convert]::FromBase64String($favicon) | Set-Content -Path d:\github\OpusMagusWeb\website\favicon.ico -AsByteStream

Write-Host "✓ Placeholder images created"
