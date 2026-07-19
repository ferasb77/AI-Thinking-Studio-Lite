# AI Thinking Studio™ — Workshop Edition

**A structured environment for examining decisions before reaching conclusions.**

AI Thinking Studio is an Enable My Growth application, developed by Feras Banna.

> This Studio will not tell you what to think. It is not designed to help you
> reach conclusions faster. It is designed to help you examine conclusions more
> thoroughly before reaching them. You remain responsible for your judgments,
> decisions, and actions.

## Purpose

The Studio supports workshop participants as they examine a consequential
challenge through multiple perspectives. AI acts as a structured thinking
companion—not an advisor, recommendation engine, or decision-maker.

The product follows the Enable My Growth philosophy:

**Perspective changes what becomes possible.**

## The thinking sequence

| Stage | Purpose |
| --- | --- |
| Session Setup | Define the challenge, context, affected groups and current direction. |
| Mirror Room | Examine framing, assumptions, missing information and alternative interpretations. |
| Human Room | Explore stakeholder perspectives, concerns, resistance and conditions for trust. |
| Possibility Room | Expand the range of approaches before narrowing. |
| Challenge Room | Stress-test selected ideas with firm, constructive scrutiny. |
| Future Room | Examine consequences, unintended outcomes and required conditions. |
| Thinking Record | Capture the evolution and current limits of understanding in a branded PDF. |

## Product relationship

- **Master brand:** Enable My Growth
- **Founder:** Feras Banna
- **Application:** AI Thinking Studio
- **Edition:** Workshop Edition
- **Endorsement:** An Enable My Growth application, developed by Feras Banna.

The approved 3D Enable My Growth Möbius mark, brand fonts and colour system are
included in `assets/`. Visual tokens and product language are centralized in
`core/brand.py`.

## Capabilities

- Facilitator-provisioned authentication
- Saved, multi-session work through Supabase
- Private Studio Administrator participation dashboard
- Strict completion tracking across all five rooms and final reflection
- Structured AI examination across five rooms
- Human reflection before and after AI-supported examination
- Branded Thinking Record PDF export
- Branded Examination Prompt Toolkit PDF export
- Provider abstraction supporting Anthropic by default, with optional Gemini
  and OpenAI clients

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Copy the environment example:

   ```bash
   cp .env.example .env
   ```

3. Add the required credentials to `.env`.

4. Apply `supabase_setup.sql` to the intended Supabase project.

5. Run the application:

   ```bash
   streamlit run app.py
   ```

### Updating an existing deployment

Run `supabase_admin_dashboard_migration.sql` once in the existing Supabase
project's SQL Editor, then deploy the updated application files. Sign out and
sign back in as `info@enablemygrowth.com` to refresh the administrator role in
the access token. The **Studio Overview** link will then appear in the sidebar.

The administrator dashboard exposes account email addresses and aggregate
participation counts only. Thinking Session titles and content remain private.

## Required environment variables

| Variable | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Default AI provider credential |
| `ANTHROPIC_MODEL` | Default Anthropic model |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anonymous key |

Optional Gemini and OpenAI variables are documented in `.env.example`.

## Responsible-use boundary

- AI must not recommend a final decision or course of action.
- AI must not declare an option best, optimal or correct.
- AI must help the participant expand, challenge and deepen examination.
- Human judgment remains with the participant.
- Users should not enter confidential, classified, personally identifiable or
  commercially sensitive information unless they are authorized to process it
  through the deployed environment.
- Deployment owners must define and communicate retention, deletion, access and
  model-provider arrangements before participant use.

See `PRIVACY-AND-AI-USE.md` for the deployment checklist and participant-facing
notice.

## Project structure

```text
app.py                     Main Streamlit application
core/brand.py              Identity tokens, fonts and logo helpers
core/auth.py               Authentication experience
core/state.py              Session state and stage labels
core/prompts.py            Examination doctrine and AI prompts
core/report_builder.py     Branded Thinking Record generator
core/toolkit_builder.py    Branded prompt toolkit generator
core/db.py                 Supabase persistence
assets/                    Approved logo and licensed fonts
supabase_setup.sql         Database setup
```

## Ownership

AI Thinking Studio™ is an Enable My Growth application developed by Feras Banna.
It is not licensed for redistribution without written permission.
