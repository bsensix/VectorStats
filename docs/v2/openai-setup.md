# OpenAI Setup for VectorStats v2

This guide explains how to enable the Agent tab in VectorStats v2.

## 1) Prerequisites

- QGIS 3.x installed
- VectorStats plugin enabled
- OpenAI API key

## 2) Configure API key

1. Set environment variable before opening QGIS:

```bash
set OPENAI_API_KEY=sk-your-key
```

2. Open VectorStats and go to `Agent` tab.
3. Click `Configurar API Key`.
4. Confirm that the `Pedir Insight` button becomes enabled.

If validation fails, the plugin returns `AI_401_KEY_INVALID` with an actionable message.

## 3) Security policy

- Use OS vault-compatible backends only.
- Plaintext key fallback is rejected.
- Sensitive payload fields are filtered/redacted before AI calls.

## 4) Troubleshooting

- If key validation fails, verify key prefix `sk-` and key length.
- If request is cancelled, expected code is `AI_408_TIMEOUT`.
- If call is blocked by policy, review session budget and retry conditions.

## 5) Release model policy

- Release channel accepts only pinned models.
- Current pinned model: `gpt-4.1-mini`.
- Any model change requires benchmark evidence artifact before release.
