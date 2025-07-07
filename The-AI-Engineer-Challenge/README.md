<p align = "center" draggable=”false” ><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>


## <h1 align="center" id="heading"> 👋 Welcome to the AI Engineer Challenge</h1>

## 🤖 Your First Vibe Coding LLM Application

> If you are a novice, and need a bit more help to get your dev environment off the ground, check out this [Setup Guide](docs/GIT_SETUP.md). This guide will walk you through the 'git' setup you need to get started.

> For additional context on LLM development environments and API key setup, you can also check out our [Interactive Dev Environment for LLM Development](https://github.com/AI-Maker-Space/Interactive-Dev-Environment-for-AI-Engineers).

In this repository, we'll walk you through the steps to create a LLM (Large Language Model) powered application with a vibe-coded frontend!

Are you ready? Let's get started!

<details>
  <summary>🖥️ Accessing "gpt-4.1-mini" (ChatGPT) like a developer</summary>

1. Head to [this notebook](https://colab.research.google.com/drive/1sT7rzY_Lb1_wS0ELI1JJfff0NUEcSD72?usp=sharing) and follow along with the instructions!

2. Complete the notebook and try out your own system/assistant messages!

That's it! Head to the next step and start building your application!

</details>


<details>
  <summary>🏗️ Forking & Cloning This Repository</summary>

Before you begin, make sure you have:

1. 👤 A GitHub account (you'll need to replace `YOUR_GITHUB_USERNAME` with your actual username)
2. 🔧 Git installed on your local machine
3. 💻 A code editor (like Cursor, VS Code, etc.)
4. ⌨️ Terminal access (Mac/Linux) or Command Prompt/PowerShell (Windows)
5. 🔑 A GitHub Personal Access Token (for authentication)

Got everything in place? Let's move on!

1. Fork [this](https://github.com/AI-Maker-Space/The-AI-Engineer-Challenge) repo!

     ![image](https://i.imgur.com/bhjySNh.png)

1. Clone your newly created repo.

     ``` bash
     # First, navigate to where you want the project folder to be created
     cd PATH_TO_DESIRED_PARENT_DIRECTORY

     # Then clone (this will create a new folder called The-AI-Engineer-Challenge)
     git clone git@github.com:<YOUR GITHUB USERNAME>/The-AI-Engineer-Challenge.git
     ```

     > Note: This command uses SSH. If you haven't set up SSH with GitHub, the command will fail. In that case, use HTTPS by replacing `git@github.com:` with `https://github.com/` - you'll then be prompted for your GitHub username and personal access token.

2. Verify your git setup:

     ```bash
     # Check that your remote is set up correctly
     git remote -v

     # Check the status of your repository
     git status

     # See which branch you're on
     git branch
     ```

     <!-- > Need more help with git? Check out our [Detailed Git Setup Guide](docs/GIT_SETUP.md) for a comprehensive walkthrough of git configuration and best practices. -->

3. Open the freshly cloned repository inside Cursor!

     ```bash
     cd The-AI-Engineering-Challenge
     cursor .
     ```

4. Check out the existing backend code found in `/api/app.py`

</details>

<details>
  <summary>🔥Setting Up for Vibe Coding Success </summary>

While it is a bit counter-intuitive to set things up before jumping into vibe-coding - it's important to remember that there exists a gradient betweeen AI-Assisted Development and Vibe-Coding. We're only reaching *slightly* into AI-Assisted Development for this challenge, but it's worth it!

1. Check out the rules in `.cursor/rules/` and add theme-ing information like colour schemes in `frontend-rule.mdc`! You can be as expressive as you'd like in these rules!
2. We're going to index some docs to make our application more likely to succeed. To do this - we're going to start with `CTRL+SHIFT+P` (or `CMD+SHIFT+P` on Mac) and we're going to type "custom doc" into the search bar. 

     ![image](https://i.imgur.com/ILx3hZu.png)
3. We're then going to copy and paste `https://nextjs.org/docs` into the prompt.

     ![image](https://i.imgur.com/psBjpQd.png)

4. We're then going to use the default configs to add these docs to our available and indexed documents.

     ![image](https://i.imgur.com/LULLeaF.png)

5. After that - you will do the same with Vercel's documentation. After which you should see:

     ![image](https://i.imgur.com/hjyXhhC.png) 

</details>

<details>
  <summary>😎 Vibe Coding a Front End for the FastAPI Backend</summary>

1. Use `Command-L` or `CTRL-L` to open the Cursor chat console. 

2. Set the chat settings to the following:

     ![image](https://i.imgur.com/LSgRSgF.png)

3. Ask Cursor to create a frontend for your application. Iterate as much as you like!

4. Run the frontend using the instructions Cursor provided. 

> NOTE: If you run into any errors, copy and paste them back into the Cursor chat window - and ask Cursor to fix them!

> NOTE: You have been provided with a backend in the `/api` folder - please ensure your Front End integrates with it!

</details>

<details>
  <summary>🚀 Deploying Your First LLM-powered Application with Vercel</summary>

1. Ensure you have signed into [Vercel](https://vercel.com/) with your GitHub account.

2. Ensure you have `npm` (this may have been installed in the previous vibe-coding step!) - if you need help with that, ask Cursor!

3. Run the command:

     ```bash
     npm install -g vercel
     ```

4. Run the command:

     ```bash
     vercel
     ```

5. Follow the in-terminal instructions. (Below is an example of what you will see!)

     ![image](https://i.imgur.com/D1iKGCq.png)

6. Once the build is completed - head to the provided link and try out your app!

> NOTE: Remember, if you run into any errors - ask Cursor to help you fix them!

</details>

### Vercel Link to Share

You'll want to make sure you share you *domains* hyperlink to ensure people can access your app!

![image](https://i.imgur.com/mpXIgIz.png)

> NOTE: Test this is the public link by trying to open your newly deployed site in an Incognito browser tab!

### 🎉 Congratulations! 

You just deployed your first LLM-powered application! 🚀🚀🚀 Get on linkedin and post your results and experience! Make sure to tag us at @AIMakerspace!

Here's a template to get your post started!

```
🚀🎉 Exciting News! 🎉🚀

🏗️ Today, I'm thrilled to announce that I've successfully built and shipped my first-ever LLM using the powerful combination of , and the OpenAI API! 🖥️

Check it out 👇
[LINK TO APP]

A big shoutout to the @AI Makerspace for all making this possible. Couldn't have done it without the incredible community there. 🤗🙏

Looking forward to building with the community! 🙌✨ Here's to many more creations ahead! 🥂🎉

Who else is diving into the world of AI? Let's connect! 🌐💡

#FirstLLMApp 
```

# 🚀 Enhanced AI Engineer Challenge

A sophisticated AI chat application with advanced features for improved factual accuracy, reduced hallucinations, chain-of-thought reasoning, and style guidance.

## ✨ Advanced Features

### 🧠 **Chain-of-Thought Reasoning**
- **Step-by-step problem solving**: AI breaks down complex questions into manageable parts
- **Structured thinking**: Clear reasoning process with logical progression
- **Multiple perspectives**: Considers different angles before reaching conclusions
- **Validation**: Double-checks answers against original questions

### 🎯 **Accuracy Control & Hallucination Reduction**
- **Three accuracy levels**: Standard, High, and Maximum
- **Fact verification**: AI states uncertainty when unsure
- **Source citations**: Optional citation system for factual claims
- **Context qualification**: Provides context for claims and limitations

### 🎨 **Style Guidance & Tone Control**
- **Professional**: Formal, business-appropriate language
- **Casual**: Friendly, conversational tone
- **Academic**: Scholarly language with citations
- **Creative**: Imaginative and expressive communication
- **Technical**: Precise technical terminology
- **Friendly**: Warm, approachable language

### ⚙️ **Advanced Configuration**
- **Temperature control**: Adjust creativity vs. consistency (0-2)
- **Token limits**: Control response length (100-4000 tokens)
- **Custom instructions**: Add specific AI behavior rules
- **Citation system**: Include source references when needed

## 🏗️ Architecture

### Backend (FastAPI)
```
api/
├── app.py                 # Enhanced API with advanced features
├── requirements.txt       # Python dependencies
└── vercel.json           # Deployment configuration
```

### Frontend (Next.js)
```
frontend/
├── app/
│   ├── page.tsx          # Enhanced chat interface
│   ├── layout.tsx        # App layout
│   └── globals.css       # Styling
├── package.json          # Node.js dependencies
└── next.config.js        # Next.js configuration
```

## 🚀 Quick Start

### 1. Deploy Backend
```bash
cd api
vercel
```

### 2. Deploy Frontend
```bash
cd frontend
vercel
```

### 3. Configure Settings
- Enter your OpenAI API key
- Choose reasoning mode (Chain of Thought recommended for complex questions)
- Select style tone (Professional for business, Creative for brainstorming)
- Set accuracy level (Maximum for critical information)

## 🎯 Usage Examples

### Complex Problem Solving
```
User: "How would you design a scalable microservices architecture for an e-commerce platform?"

Settings:
- Reasoning Mode: Chain of Thought
- Style Tone: Technical
- Accuracy Level: High
- Include Citations: Yes
```

### Creative Writing
```
User: "Write a short story about a time traveler"

Settings:
- Reasoning Mode: None
- Style Tone: Creative
- Accuracy Level: Standard
- Temperature: 0.9
```

### Academic Research
```
User: "Explain the impact of climate change on global agriculture"

Settings:
- Reasoning Mode: Step by Step
- Style Tone: Academic
- Accuracy Level: Maximum
- Include Citations: Yes
```

## 🔧 Technical Implementation

### Enhanced Prompt Engineering
- **Base system prompt**: Core AI behavior and capabilities
- **Reasoning instructions**: Structured thinking methodology
- **Style guidance**: Tone-specific communication rules
- **Accuracy controls**: Fact-checking and verification protocols

### Advanced API Parameters
- **Temperature**: Controls randomness (0.0 = deterministic, 2.0 = very creative)
- **Top-p**: Nucleus sampling for focused responses
- **Frequency penalty**: Reduces repetition
- **Presence penalty**: Encourages new topics

### Response Validation
- **Fact checking**: AI reviews its own responses for accuracy
- **Completeness assessment**: Ensures all aspects are addressed
- **Uncertainty flagging**: Clearly marks areas of doubt
- **Source suggestions**: Recommends verification methods

## 📊 Feature Comparison

| Feature | Standard | Enhanced |
|---------|----------|----------|
| Reasoning | Basic | Chain-of-Thought |
| Accuracy | Standard | 3 Levels |
| Style | Fixed | 6 Tones |
| Citations | No | Optional |
| Validation | No | Self-review |
| Customization | Limited | Extensive |

## 🎨 UI/UX Improvements

### Enhanced Settings Panel
- **Collapsible advanced settings**: Clean, organized interface
- **Real-time configuration display**: Visual feedback on current settings
- **Intuitive controls**: Sliders, dropdowns, and toggles
- **Feature indicators**: Icons and labels for easy identification

### Improved Chat Interface
- **Message styling**: Clear user/assistant distinction
- **Typing indicators**: Real-time response feedback
- **Configuration badges**: Show active features
- **Responsive design**: Works on all devices

## 🔒 Security & Privacy

- **API key security**: Client-side only, never stored
- **No data persistence**: Conversations not saved
- **Secure communication**: HTTPS encryption
- **Input validation**: Pydantic models for data safety

## 🚀 Deployment

### Vercel Deployment
1. **Backend**: Deploy to `ai-engineer-challenge-api`
2. **Frontend**: Deploy to `ai-engineer-challenge-frontend`
3. **Configuration**: Update `next.config.js` with backend URL

### Environment Variables
- `BACKEND_URL`: Production backend URL
- `OPENAI_API_KEY`: User-provided API key

## 📈 Performance Optimizations

- **Streaming responses**: Real-time chat experience
- **Efficient prompts**: Optimized for token usage
- **Caching**: Vercel edge caching for static assets
- **CDN**: Global content delivery network

## 🎯 Best Practices

### For Maximum Accuracy
1. Use "Maximum" accuracy level
2. Enable citations
3. Choose "Chain of Thought" reasoning
4. Set lower temperature (0.3-0.5)

### For Creative Tasks
1. Use "Creative" style tone
2. Set higher temperature (0.8-1.2)
3. Disable citations
4. Use "None" reasoning mode

### For Technical Questions
1. Use "Technical" style tone
2. Enable "Step by Step" reasoning
3. Set "High" accuracy level
4. Include custom instructions for domain-specific terms

## 🔮 Future Enhancements

- **Multi-modal support**: Image and document analysis
- **Memory system**: Conversation history and context
- **Plugin architecture**: Extensible functionality
- **Analytics dashboard**: Usage insights and metrics
- **Collaborative features**: Multi-user conversations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the AI Engineer Challenge by AI Makerspace.

---

**Built with ❤️ using FastAPI, Next.js, and OpenAI GPT-4.1-mini**

# 🚀 PDF Chat - Your Documents, But Make It Chatty!

Ever wished your PDFs could talk back? Well, now they can! This super-cool app lets you upload PDFs and chat with them like they're your smartest friend. 

## ✨ Features That'll Blow Your Mind

- 📤 **Easy-Peasy Upload**: Drop your PDF like it's hot!
- 🧠 **Smart Processing**: We use LangChain's magic to make your PDFs searchable
- 💬 **Chat Away**: Ask questions, get answers - it's like texting your document
- 🎯 **Precise Answers**: Our RAG system finds exactly what you need
- 🌊 **Smooth Streaming**: Responses flow in real-time, no awkward waiting

## 🛠️ Tech Stack of Awesomeness

- **Frontend**: Next.js + Tailwind CSS = Beautiful UI that just works
- **Backend**: FastAPI - Because speed is life! 🏃‍♂️
- **RAG Engine**: LangChain + OpenAI = AI goodness
- **Vector Store**: Chroma - Making your documents searchable at light speed
- **Deployment**: Vercel - Deploy like a boss! 

## 🚦 Getting Started

1. Clone this bad boy:
   ```bash
   git clone <your-repo-url>
   ```

2. Install the goodies:
   ```bash
   # Backend
   cd api
   pip install -r requirements.txt

   # Frontend
   cd ../frontend
   npm install
   ```

3. Set up your secret sauce:
   ```bash
   # Create a .env file in the api directory
   echo "OPENAI_API_KEY=your-key-here" > api/.env
   ```

4. Light it up:
   ```bash
   # Backend (in api directory)
   uvicorn app:app --reload

   # Frontend (in frontend directory)
   npm run dev
   ```

5. 🎉 Visit `http://localhost:3000` and start chatting!

## 🌟 How It Works

1. **Upload**: Your PDF gets split into bite-sized chunks
2. **Process**: Each chunk gets turned into a vector (fancy math stuff!)
3. **Store**: Chroma keeps track of everything
4. **Chat**: Ask a question, and our RAG system:
   - Finds the most relevant chunks
   - Feeds them to the AI
   - Returns a smart answer

## 🎯 Usage Tips

- **Better Questions = Better Answers**: Be specific in what you ask
- **Context is King**: The AI uses nearby text for better understanding
- **Multiple PDFs**: Upload as many as you want, each gets its own chat session

## 🔐 Security First!

- Your OpenAI API key is treated like gold - never stored, always encrypted in transit
- PDFs are processed securely and cleaned up after use
- Vector stores are isolated per session

## 🚀 Deployment

We're rocking Vercel for both frontend and backend:

1. Push to GitHub
2. Connect to Vercel
3. Set your `OPENAI_API_KEY`
4. Watch the magic happen!

## 🤝 Contributing

Got ideas? We love ideas! Here's how to contribute:

1. Fork it
2. Create your feature branch
3. Make it awesome
4. Create a PR
5. Get famous! 🌟

## 📝 License

MIT - Because sharing is caring! 

## 🙋‍♂️ Need Help?

- 🐛 Found a bug? Open an issue!
- 💡 Got a feature idea? We're all ears!
- 🤔 Questions? Ask away!

---

Made with ❤️ and a lot of ☕️ by your friendly neighborhood developers
