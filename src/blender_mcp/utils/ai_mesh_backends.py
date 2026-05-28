"""AI mesh generation backends (Rodin, Tripo, Hunyuan)."""

from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

RODIN_ENDPOINT = "https://api.hyper3d.com/api/v2/rodin"
RODIN_STATUS_ENDPOINT = "https://api.hyper3d.com/api/v2/status"
RODIN_DOWNLOAD_ENDPOINT = "https://api.hyper3d.com/api/v2/download"
TRIPO_TASK_ENDPOINT = "https://api.tripo3d.ai/v2/openapi/task"


class MeshBackend(StrEnum):
    RODIN = "rodin"
    TRIPO = "tripo"
    HUNYUAN = "hunyuan"


@dataclass
class GenerationJob:
    backend: MeshBackend
    job_id: str
    subscription_key: str | None = None
    status: str = "submitted"
    download_url: str | None = None
    local_path: str | None = None
    raw: dict[str, Any] | None = None


def _api_key(backend: MeshBackend) -> str | None:
    env_map = {
        MeshBackend.RODIN: ("RODIN_API_KEY", "HYPER3D_API_KEY"),
        MeshBackend.TRIPO: ("TRIPO_API_KEY",),
        MeshBackend.HUNYUAN: ("HUNYUAN3D_API_KEY", "HUNYUAN_API_KEY"),
    }
    for name in env_map.get(backend, ()):
        value = os.getenv(name, "").strip()
        if value:
            return value
    return None


def list_backends() -> list[dict[str, Any]]:
    """Return configured backends and required env vars."""
    rows: list[dict[str, Any]] = []
    for backend in MeshBackend:
        key = _api_key(backend)
        rows.append(
            {
                "backend": backend.value,
                "configured": bool(key),
                "env_vars": {
                    MeshBackend.RODIN: ["RODIN_API_KEY", "HYPER3D_API_KEY"],
                    MeshBackend.TRIPO: ["TRIPO_API_KEY"],
                    MeshBackend.HUNYUAN: ["HUNYUAN3D_API_KEY", "HUNYUAN_API_KEY"],
                }[backend],
            }
        )
    return rows


async def submit_generation(
    *,
    backend: MeshBackend | str,
    prompt: str,
    image_path: str | None = None,
    output_format: str = "glb",
    poll_timeout: int = 600,
    poll_interval: float = 5.0,
) -> GenerationJob:
    """Submit a text/image-to-3D job and poll until complete."""
    backend_enum = MeshBackend(str(backend).lower())
    api_key = _api_key(backend_enum)
    if not api_key:
        raise ValueError(
            f"Backend '{backend_enum.value}' is not configured. "
            f"Set one of: {list_backends()[list(MeshBackend).index(backend_enum)]['env_vars']}"
        )
    if not prompt.strip() and not image_path:
        raise ValueError("prompt or image_path is required")

    if backend_enum == MeshBackend.RODIN:
        job = await _submit_rodin(api_key, prompt, image_path, output_format)
    elif backend_enum == MeshBackend.TRIPO:
        job = await _submit_tripo(api_key, prompt, output_format)
    else:
        job = await _submit_hunyuan(api_key, prompt, image_path, output_format)

    return await _poll_until_ready(job, api_key, poll_timeout, poll_interval)


async def _submit_rodin(
    api_key: str,
    prompt: str,
    image_path: str | None,
    output_format: str,
) -> GenerationJob:
    headers = {"Authorization": f"Bearer {api_key}"}
    data: dict[str, str] = {
        "prompt": prompt,
        "geometry_file_format": output_format.lower(),
        "tier": "Gen-2",
    }
    files: dict[str, tuple] | None = None
    if image_path:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {image_path}")
        files = {"images": (path.name, path.read_bytes(), "application/octet-stream")}

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(RODIN_ENDPOINT, headers=headers, data=data, files=files)
        response.raise_for_status()
        payload = response.json()

    if payload.get("error"):
        raise RuntimeError(f"Rodin API error: {payload['error']}")

    job_uuid = payload.get("uuid") or (payload.get("jobs") or {}).get("uuids", [None])[0]
    if not job_uuid:
        raise RuntimeError(f"Rodin response missing job uuid: {payload}")

    subscription_key = (payload.get("jobs") or {}).get("subscription_key")
    return GenerationJob(
        backend=MeshBackend.RODIN,
        job_id=str(job_uuid),
        subscription_key=subscription_key,
        raw=payload,
    )


async def _submit_tripo(api_key: str, prompt: str, output_format: str) -> GenerationJob:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "type": "text_to_model",
        "prompt": prompt,
        "model_version": "v3.1-20260211",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(TRIPO_TASK_ENDPOINT, headers=headers, json=body)
        response.raise_for_status()
        payload = response.json()

    data = payload.get("data") or payload
    task_id = data.get("task_id") or data.get("id") or payload.get("task_id")
    if not task_id:
        raise RuntimeError(f"Tripo response missing task_id: {payload}")

    return GenerationJob(backend=MeshBackend.TRIPO, job_id=str(task_id), raw=payload)


async def _submit_hunyuan(
    api_key: str,
    prompt: str,
    image_path: str | None,
    output_format: str,
) -> GenerationJob:
    """Hunyuan3D via configurable endpoint (fleet-specific deployments vary)."""
    endpoint = os.getenv(
        "HUNYUAN3D_API_URL",
        "https://api.hunyuan.tencent.com/v1/3d/generate",
    ).strip()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {"prompt": prompt, "format": output_format.lower()}
    if image_path:
        body["image_path"] = image_path

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(endpoint, headers=headers, json=body)
        if response.status_code >= 400:
            raise RuntimeError(
                f"Hunyuan API error {response.status_code}: {response.text}. "
                "Set HUNYUAN3D_API_URL if your deployment uses a different endpoint."
            )
        payload = response.json()

    job_id = payload.get("job_id") or payload.get("task_id") or payload.get("id")
    if not job_id:
        raise RuntimeError(f"Hunyuan response missing job id: {payload}")

    download_url = payload.get("download_url") or payload.get("model_url")
    return GenerationJob(
        backend=MeshBackend.HUNYUAN,
        job_id=str(job_id),
        download_url=str(download_url) if download_url else None,
        raw=payload,
    )


async def _poll_until_ready(
    job: GenerationJob,
    api_key: str,
    timeout: int,
    interval: float,
) -> GenerationJob:
    elapsed = 0.0
    while elapsed < timeout:
        job = await _refresh_status(job, api_key)
        if job.status in {"completed", "success", "done", "succeeded"}:
            if not job.local_path:
                job.local_path = await _download_result(job, api_key)
            return job
        if job.status in {"failed", "error", "cancelled"}:
            raise RuntimeError(f"Generation failed ({job.backend}): status={job.status}")
        await asyncio.sleep(interval)
        elapsed += interval

    raise TimeoutError(f"Generation timed out after {timeout}s ({job.backend}, id={job.job_id})")


async def _refresh_status(job: GenerationJob, api_key: str) -> GenerationJob:
    headers = {"Authorization": f"Bearer {api_key}"}

    if job.backend == MeshBackend.RODIN:
        params = {"uuid": job.job_id}
        if job.subscription_key:
            params["subscription_key"] = job.subscription_key
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(RODIN_STATUS_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
        status = str(payload.get("status") or payload.get("progress") or "processing").lower()
        job.status = status
        job.raw = payload
        return job

    if job.backend == MeshBackend.TRIPO:
        url = f"{TRIPO_TASK_ENDPOINT}/{job.job_id}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            payload = response.json()
        data = payload.get("data") or payload
        status = str(data.get("status") or "processing").lower()
        job.status = status
        output = data.get("output") or {}
        model_url = output.get("model") or output.get("pbr_model") or output.get("base_model")
        if model_url:
            job.download_url = str(model_url)
        job.raw = payload
        return job

    if job.download_url:
        job.status = "completed"
    else:
        job.status = "processing"
    return job


async def _download_result(job: GenerationJob, api_key: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}"}
    suffix = ".glb"

    if job.backend == MeshBackend.RODIN:
        params = {"uuid": job.job_id}
        if job.subscription_key:
            params["subscription_key"] = job.subscription_key
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(RODIN_DOWNLOAD_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()
        files = payload.get("list") or payload.get("files") or []
        if not files:
            raise RuntimeError(f"Rodin download returned no files: {payload}")
        first = files[0]
        url = first.get("url") if isinstance(first, dict) else str(first)
        if not url:
            raise RuntimeError(f"Rodin download missing url: {payload}")
        job.download_url = url

    if not job.download_url:
        raise RuntimeError(f"No download URL for job {job.job_id} ({job.backend})")

    async with httpx.AsyncClient(timeout=300.0, follow_redirects=True) as client:
        response = await client.get(job.download_url, headers=headers)
        response.raise_for_status()
        content = response.content

    if ".fbx" in job.download_url.lower():
        suffix = ".fbx"
    elif ".obj" in job.download_url.lower():
        suffix = ".obj"

    out_dir = Path(tempfile.gettempdir()) / "blender_mcp_ai_gen"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{job.backend}_{job.job_id}{suffix}"
    out_path.write_bytes(content)
    logger.info("Downloaded AI mesh to %s (%d bytes)", out_path, len(content))
    return str(out_path.absolute())
