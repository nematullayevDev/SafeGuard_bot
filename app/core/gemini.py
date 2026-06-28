import logging
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

ACTIVE_MODEL = None

async def get_active_model(api_key: str) -> str:
    global ACTIVE_MODEL
    if ACTIVE_MODEL:
        return ACTIVE_MODEL

    candidates = [
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-1.5-flash",
        "gemini-pro"
    ]
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    supported_names = [m["name"].split("/")[-1] for m in models if "generateContent" in m.get("supportedGenerationMethods", [])]
                    for cand in candidates:
                        if cand in supported_names:
                            ACTIVE_MODEL = cand
                            logger.info(f"Selected Gemini model from ListModels: {ACTIVE_MODEL}")
                            return ACTIVE_MODEL
                    if supported_names:
                        ACTIVE_MODEL = supported_names[0]
                        logger.info(f"Fallback to first available model: {ACTIVE_MODEL}")
                        return ACTIVE_MODEL
    except Exception as e:
        logger.error(f"Error fetching models list: {e}")

    ACTIVE_MODEL = candidates[0]
    return ACTIVE_MODEL

async def call_gemini_api(api_key: str, prompt: str, response_mime_type: str = "text/plain") -> str:
    primary_model = await get_active_model(api_key)
    models_to_try = [primary_model]
    for m in ["gemini-3.1-flash-lite", "gemini-1.5-flash", "gemini-pro"]:
        if m not in models_to_try:
            models_to_try.append(m)

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }
    if response_mime_type == "application/json":
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }

    last_error_status = None
    last_error_text = ""

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        for attempt in range(2):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=15)) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        else:
                            last_error_status = response.status
                            last_error_text = await response.text()
                            logger.warning(f"Gemini API model {model} attempt {attempt+1} failed with status {response.status}: {last_error_text}")
                            if response.status in (503, 429):
                                await asyncio.sleep(1.5 * (attempt + 1))
                                continue
                            break
            except Exception as e:
                logger.error(f"Network error in call_gemini_api for {model}: {e}")
                last_error_status = "Connection Error"
                last_error_text = str(e)
                await asyncio.sleep(1)

    raise Exception(f"API Error (Status: {last_error_status})")
