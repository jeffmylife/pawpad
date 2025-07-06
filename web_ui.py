#!/usr/bin/env python3
"""
PawPad Web UI - FastAPI + HTMX interface for demonstrating PawPad functionality
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.pawpad.encoder import (
    generate_fingerprint,
    fingerprint_to_string,
    string_to_fingerprint,
    encode_fingerprint_in_text,
    extract_fingerprint_from_text,
    detect_fingerprint_in_text,
    encode_message_in_text,
    decode_message_from_text,
    encode_message_in_single_char,
    decode_message_from_single_char,
    generate_key_pair,
    sign_text_with_chained_fingerprints,
    verify_chained_fingerprints,
    extract_original_text_from_signed,
)

app = FastAPI(title="PawPad Web Demo", description="Unicode Steganography Tool")

# Create templates directory if it doesn't exist
templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)

templates = Jinja2Templates(directory="templates")

# Demo keys (generated at startup)
DEMO_PRIVATE_KEY = None
DEMO_PUBLIC_KEY = None


@app.on_event("startup")
async def startup_event():
    """Generate demo keys on startup"""
    global DEMO_PRIVATE_KEY, DEMO_PUBLIC_KEY
    DEMO_PRIVATE_KEY, DEMO_PUBLIC_KEY = generate_key_pair()
    print("🔑 Demo keys generated")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with all PawPad tools"""
    return templates.TemplateResponse("index.html", {"request": request})


# Basic Fingerprinting Endpoints
@app.post("/encode", response_class=HTMLResponse)
async def encode_text(
    request: Request,
    text: str = Form(...),
    fingerprint: Optional[str] = Form(None),
    length: int = Form(16),
):
    """Encode fingerprint into text"""
    try:
        if fingerprint:
            fp_bytes = string_to_fingerprint(fingerprint)
        else:
            fp_bytes = generate_fingerprint(length)

        encoded_text = encode_fingerprint_in_text(text, fp_bytes)
        fp_string = fingerprint_to_string(fp_bytes)

        return templates.TemplateResponse(
            "results/encode_result.html",
            {
                "request": request,
                "original_text": text,
                "fingerprint": fp_string,
                "encoded_text": encoded_text,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/encode_result.html",
            {"request": request, "error": str(e), "success": False},
        )


@app.post("/decode", response_class=HTMLResponse)
async def decode_text(
    request: Request,
    text: str = Form(...),
    expected_fingerprint: Optional[str] = Form(None),
):
    """Decode fingerprint from text"""
    try:
        if expected_fingerprint:
            expected_fp = string_to_fingerprint(expected_fingerprint)
            is_present = detect_fingerprint_in_text(text, expected_fp)

            return templates.TemplateResponse(
                "results/decode_result.html",
                {
                    "request": request,
                    "text": text,
                    "expected_fingerprint": expected_fingerprint,
                    "is_present": is_present,
                    "mode": "detect",
                    "success": True,
                },
            )
        else:
            extracted_fp = extract_fingerprint_from_text(text)
            fp_string = fingerprint_to_string(extracted_fp) if extracted_fp else None

            return templates.TemplateResponse(
                "results/decode_result.html",
                {
                    "request": request,
                    "text": text,
                    "extracted_fingerprint": fp_string,
                    "mode": "extract",
                    "success": True,
                },
            )
    except Exception as e:
        return templates.TemplateResponse(
            "results/decode_result.html",
            {"request": request, "error": str(e), "success": False},
        )


# Message Hiding Endpoints
@app.post("/hide", response_class=HTMLResponse)
async def hide_message(
    request: Request,
    text: str = Form(...),
    message: str = Form(...),
    single_char: bool = Form(False),
):
    """Hide message in text"""
    try:
        if single_char:
            if len(text) != 1:
                raise ValueError("Single-char mode requires exactly one character")
            encoded_text = encode_message_in_single_char(text, message)
        else:
            encoded_text = encode_message_in_text(text, message)

        return templates.TemplateResponse(
            "results/hide_result.html",
            {
                "request": request,
                "original_text": text,
                "secret_message": message,
                "encoded_text": encoded_text,
                "single_char": single_char,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/hide_result.html",
            {"request": request, "error": str(e), "success": False},
        )


@app.post("/reveal", response_class=HTMLResponse)
async def reveal_message(
    request: Request, text: str = Form(...), single_char: bool = Form(False)
):
    """Reveal hidden message from text"""
    try:
        if single_char:
            decoded_message = decode_message_from_single_char(text)
        else:
            decoded_message = decode_message_from_text(text)

        return templates.TemplateResponse(
            "results/reveal_result.html",
            {
                "request": request,
                "text": text,
                "decoded_message": decoded_message,
                "single_char": single_char,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/reveal_result.html",
            {"request": request, "error": str(e), "success": False},
        )


# Cryptographic Signing Endpoints
@app.post("/sign", response_class=HTMLResponse)
async def sign_text(request: Request, text: str = Form(...)):
    """Sign text with chained fingerprints"""
    try:
        if DEMO_PRIVATE_KEY is None:
            raise ValueError("Demo keys not initialized")
        signed_text = sign_text_with_chained_fingerprints(text, DEMO_PRIVATE_KEY)

        return templates.TemplateResponse(
            "results/sign_result.html",
            {
                "request": request,
                "original_text": text,
                "signed_text": signed_text,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/sign_result.html",
            {"request": request, "error": str(e), "success": False},
        )


@app.post("/verify", response_class=HTMLResponse)
async def verify_text(request: Request, text: str = Form(...)):
    """Verify signed text"""
    try:
        if DEMO_PRIVATE_KEY is None:
            raise ValueError("Demo keys not initialized")
        result = verify_chained_fingerprints(text, DEMO_PRIVATE_KEY)

        return templates.TemplateResponse(
            "results/verify_result.html",
            {"request": request, "text": text, "result": result, "success": True},
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/verify_result.html",
            {"request": request, "error": str(e), "success": False},
        )


@app.post("/extract", response_class=HTMLResponse)
async def extract_text(request: Request, text: str = Form(...)):
    """Extract original text from signed text"""
    try:
        original_text = extract_original_text_from_signed(text)

        return templates.TemplateResponse(
            "results/extract_result.html",
            {
                "request": request,
                "signed_text": text,
                "original_text": original_text,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/extract_result.html",
            {"request": request, "error": str(e), "success": False},
        )


# Utility endpoint for generating random fingerprints
@app.post("/generate-fingerprint", response_class=HTMLResponse)
async def generate_random_fingerprint(request: Request, length: int = Form(16)):
    """Generate a random fingerprint"""
    try:
        fp_bytes = generate_fingerprint(length)
        fp_string = fingerprint_to_string(fp_bytes)

        return templates.TemplateResponse(
            "results/generate_result.html",
            {
                "request": request,
                "fingerprint": fp_string,
                "length": length,
                "success": True,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "results/generate_result.html",
            {"request": request, "error": str(e), "success": False},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
