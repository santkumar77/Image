# VISIO — AI Image Prompt Generator

Generate rich, detailed image prompts using **NVIDIA NIM** (Gemma 4 31B).  
Paste the output into Midjourney, DALL-E, Stable Diffusion, etc.

## Stack

| Layer    | Tech                              |
|----------|-----------------------------------|
| Frontend | Static HTML + Vanilla JS          |
| Backend  | Python serverless (Vercel)        |
| AI       | NVIDIA NIM · google/gemma-4-31b-it |

---

## Project Structure

```
visio/
├── api/
│   └── generate.py      # Python serverless function
├── index.html           # Frontend (served as static)
├── vercel.json          # Routing config
├── requirements.txt
└── .env.example
```

---

## Deploy to Vercel

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Clone / enter the project
```bash
cd visio
```

### 3. Set your NVIDIA API key as an environment variable
```bash
vercel env add NVIDIA_API_KEY
# paste your key when prompted
```

### 4. Deploy
```bash
vercel --prod
```

Vercel auto-detects Python in `/api` and deploys it as a serverless function.  
`index.html` is served as a static file at `/`.

---

## Local Development

```bash
vercel dev
```

Then open `http://localhost:3000`.

---

## Get an NVIDIA API Key

1. Go to https://build.nvidia.com
2. Sign in / create account
3. Navigate to **API Keys** → **Generate Key**
4. Copy and add it to your environment

---

## Note on the Model

`google/gemma-4-31b-it` is a **text completion** model — it doesn't generate images directly.  
VISIO uses it to craft highly detailed prompts that you copy into image generation tools  
(Midjourney, DALL-E 3, Stable Diffusion, Firefly, etc.).
