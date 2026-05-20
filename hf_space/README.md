---
title: T22026 GA0 API Hub
emoji: ?
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# T22026 GA0 API Hub (Hugging Face Spaces)

This Space runs a unified FastAPI gateway for:
- Q5, Q10, Q11, Q14, Q16, Q18, Q19

## Routes
- `/q5/*`
- `/q10/*`
- `/q11/*`
- `/q14/*`
- `/q16/*`
- `/q18/*`
- `/q19/*`

## Notes
- Optimized for single-Space deployment.
- Temp/work directories point to `/tmp` for container-safe cleanup.
- For private keys/tokens, use Space Secrets.
