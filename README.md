# PhishGuard: Real-Time Phishing Link Detector

A Chrome extension that protects users from phishing attempts by scanning URLs in real-time using Google Safe Browsing API.

## Features

- Real-time URL scanning
- Color-coded warnings (red for dangerous, green for safe)
- Phishing reporting capability
- Statistics tracking for scanned and blocked URLs
- User-friendly warning page with detailed threat information

## Setup Instructions

1. Get a Google Safe Browsing API key:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Safe Browsing API
   - Create credentials (API key)
   - Copy the API key

2. Configure the extension:
   - Open `js/background.js`
   - Replace `YOUR_GOOGLE_SAFE_BROWSING_API_KEY` with your actual API key

3. Install the extension in Chrome:
   - Open Chrome and go to `chrome://extensions/`
   - Enable "Developer mode" in the top right
   - Click "Load unpacked"
   - Select the PhishGuard directory

## Usage

- The extension icon will show green when protection is active
- Click the extension icon to view statistics and report phishing
- When accessing a suspicious URL, a warning page will appear
- Users can choose to go back (recommended) or proceed with caution

## Security Notes

- Never disable the extension when visiting unfamiliar websites
- Always report suspected phishing attempts
- Keep the extension updated with the latest threat definitions

## Technical Details

The extension uses:
- Chrome Extensions Manifest V3
- Google Safe Browsing API v4
- Local storage for statistics
- Real-time URL checking