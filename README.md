# AI Thinking Studio™ Lite

**A structured thinking environment for AI-Powered Design Thinking**

---

## What This Is

AI Thinking Studio™ Lite is a workshop companion platform built for participants of a 2-day **AI-Powered Design Thinking** workshop.

It is not a chatbot. It is not a recommendation engine. It is not a decision tool.

**The Studio Promise:**

> This Studio will not tell you what to think. It is not designed to help you reach conclusions faster. It is designed to help you examine conclusions more thoroughly before reaching them. You remain responsible for your judgments, decisions, and actions.

---

## The Six Thinking Rooms

The app guides participants through a structured **Thinking Expedition** comprising six rooms:

| Room | Purpose |
|------|---------|
| **Mirror Room** | Examine how the challenge is currently framed. Surface assumptions. Explore alternative framings. |
| **Human Room** | Map stakeholder perspectives, resistances, and needs. |
| **Possibility Room** | Expand the range of approaches before narrowing. |
| **Battlefield Room** | Stress-test selected ideas with firm, constructive scrutiny. |
| **Future Room** | Map consequences, unintended outcomes, and required conditions. |
| **Summary & Export** | Capture the complete expedition in a downloadable PDF. |

---

## Setup Instructions

### 1. Clone or download this project

```bash
git clone <your-repo-url>
cd ai-thinking-studio-lite
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up your environment variables

Copy the example file and add your OpenAI API key:

```bash
cp .env.example .env
```

Edit `.env`:

```text
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

> **Note:** `gpt-4o-mini` is the default and recommended model for cost efficiency. You can use `gpt-4o` for higher quality outputs if budget allows.

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## Project Structure

```
ai-thinking-studio-lite/
│
├── app.py                  # Main Streamlit application and all page views
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # This file
│
├── core/
│   ├── prompts.py          # AI prompt builders for each thinking room
│   ├── openai_client.py    # OpenAI API client and response handler
│   ├── report_builder.py   # ReportLab PDF generator
│   └── state.py            # Streamlit session state management
│
└── assets/
    └── .gitkeep
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | — |
| `OPENAI_MODEL` | The OpenAI model to use | `gpt-4o-mini` |

---

## Doctrine

This platform enforces the following doctrine at the AI prompt level:

- AI must never recommend a final decision or course of action.
- AI must never declare any idea as best, optimal, or correct.
- AI must help the participant explore, not conclude.
- Human judgment remains with the participant at all times.

These are not just UX principles — they are embedded in every prompt sent to the AI.

---

## What This Is Not

This platform does not include:
- Authentication or user accounts
- Saved sessions or conversation history
- Analytics or scoring
- Collaboration features
- Payment or access control
- Recommendation scores or innovation metrics

It is a workshop companion MVP. Nothing more, nothing less.

---

## Extending This Tool

The modular structure makes it straightforward to extend:

- **Add a new room:** Add a page function in `app.py`, a prompt builder in `core/prompts.py`, and a new step in `core/state.py`.
- **Change the AI model:** Update `OPENAI_MODEL` in your `.env` file.
- **Modify PDF output:** Edit `core/report_builder.py`.
- **Adjust prompts:** Edit `core/prompts.py` — each room has its own isolated function.

---

## License

Workshop companion tool. Not for commercial redistribution without permission.
