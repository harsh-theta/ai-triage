# Logo Placement Instructions

## Where to place your Theta Technolabs logo:

Please place your logo file in the following location:

```
frontend/public/logo.png
```

## Requirements:
- **File name**: `logo.png` (exactly this name)
- **Location**: `frontend/public/` directory
- **Format**: PNG format recommended (but JPG/JPEG also works)
- **Size**: The logo will be displayed at height of 48px (3rem), width will auto-adjust
- **Content**: Should contain the full "Theta Technolabs" text as part of the logo image

## Current Setup:
- The header is configured to load `/logo.png`
- If the logo fails to load, it will show a fallback SVG logo
- The logo is set to `h-12` (48px height) with auto width
- No additional text is added since your logo contains the company name

## Alternative locations that also work:
- `frontend/public/assets/logo.png`
- `frontend/public/theta-logo.png`

If you use a different location, please let me know and I'll update the path in the code.

## Testing:
After placing the logo, you can test by:
1. Running `npm run dev` in the frontend directory
2. Opening http://localhost:3000
3. The logo should appear in the top-left corner of the header