# AI Engineer Challenge Frontend

A modern, responsive chat application built with Next.js, TypeScript, and Tailwind CSS that integrates with the FastAPI backend.

## Features

- 🎨 Modern, beautiful UI with smooth animations
- 💬 Real-time streaming chat with OpenAI GPT-4.1-mini
- ⚙️ Configurable system prompts and API keys
- 📱 Responsive design that works on all devices
- 🔒 Secure API key handling
- 🎯 TypeScript for better development experience

## Prerequisites

- Node.js 18+ and npm
- The FastAPI backend running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Set up your API key**: Click the "Settings" button in the top-right corner and enter your OpenAI API key.

2. **Configure the system prompt**: In the settings panel, you can customize the developer message (system prompt) that defines the AI's behavior.

3. **Start chatting**: Type your message in the input field and press Enter or click Send.

4. **Clear chat**: Use the "Clear Chat" button to start a new conversation.

## Development

- **Build for production**: `npm run build`
- **Start production server**: `npm start`
- **Run linting**: `npm run lint`

## Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── globals.css        # Global styles and Tailwind imports
│   ├── layout.tsx         # Root layout component
│   └── page.tsx           # Main chat interface
├── package.json           # Dependencies and scripts
├── next.config.js         # Next.js configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
└── tsconfig.json          # TypeScript configuration
```

## API Integration

The frontend communicates with the FastAPI backend through the `/api/chat` endpoint. The backend expects:

- `developer_message`: System prompt for the AI
- `user_message`: User's input message
- `model`: OpenAI model to use (default: gpt-4.1-mini)
- `api_key`: OpenAI API key

The response is streamed back to provide real-time typing experience.

## Deployment

This frontend is designed to be deployed on Vercel. The `next.config.js` includes API rewrites to proxy requests to your backend.

For production deployment, update the API destination in `next.config.js` to point to your deployed backend URL.