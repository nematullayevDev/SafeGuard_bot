"""Thin client over the VirusTotal v3 API."""
import asyncio
import base64
import hashlib

import aiohttp

_BASE = "https://www.virustotal.com/api/v3"


class VirusTotalService:
    def __init__(self, api_key: str) -> None:
        self._headers = {"x-apikey": api_key}

    async def scan_url(self, url: str) -> dict:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{_BASE}/urls",
                                    headers=self._headers, data={"url": url}) as r:
                await r.json()
            await asyncio.sleep(2)
            async with session.get(f"{_BASE}/urls/{url_id}", headers=self._headers) as r:
                return await r.json()

    async def scan_file(self, file_bytes: bytes, file_name: str,
                        poll_interval: float = 3.0, max_polls: int = 30) -> dict:
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{_BASE}/files/{file_hash}", headers=self._headers) as r:
                if r.status == 200:
                    return await r.json()

            form = aiohttp.FormData()
            form.add_field("file", file_bytes, filename=file_name,
                           content_type="application/octet-stream")
            async with session.post(f"{_BASE}/files",
                                    headers=self._headers, data=form) as r:
                upload = await r.json()

            analysis_id = upload["data"]["id"]
            result: dict = {}
            for _ in range(max_polls):
                await asyncio.sleep(poll_interval)
                async with session.get(f"{_BASE}/analyses/{analysis_id}",
                                       headers=self._headers) as r:
                    result = await r.json()
                    if result.get("data", {}).get("attributes", {}).get("status") == "completed":
                        return result
            return result
