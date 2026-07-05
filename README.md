# 📱 TeleSpotter PY

A FastAPI-based phone number intelligence tool that searches public sources for phone number information.

## Features

- 🔍 **Multi-engine search** - Queries both Google and Bing for phone number mentions
- 📊 **Smart analysis** - Extracts names and locations from search results
- 🎨 **Dark theme UI** - Retro cyberpunk interface with responsive design
- 🚀 **Vercel ready** - Deploy instantly to Vercel

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **HTTP Client**: httpx (async)
- **HTML Parsing**: BeautifulSoup4
- **Frontend**: Vanilla JS + CSS3
- **Deployment**: Vercel (Python runtime)

## Installation

```bash
pip install -r requirements.txt
```

## Running Locally

```bash
python app.py
```

Then navigate to `http://localhost:8000`

## API Endpoints

### GET /
Serves the web UI.

### POST /search
Searches for phone number information.

**Parameters:**
- `phone` (string): Phone number in any format (e.g., "555-555-1212" or "5555551212")

**Response:**
```json
{
  "phone": "555-555-1212",
  "results": [
    {
      "title": "Result title",
      "snippet": "Preview text from source",
      "source": "Google or Bing"
    }
  ],
  "analysis": {
    "top_names": ["John Smith", "Jane Doe"],
    "locations": ["New York, NY", "Los Angeles, CA"]
  }
}
```

## Deployment to Vercel

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Vercel will auto-detect the Python runtime via `vercel.json`
4. Deploy!

```bash
vercel
```

## Project Structure

- `app.py` - FastAPI application with routes and UI
- `requirements.txt` - Python dependencies
- `vercel.json` - Vercel deployment configuration

## License

MIT
