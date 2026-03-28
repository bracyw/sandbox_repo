#!/usr/bin/env python3
"""
WhisperX + Pyannote Meeting Transcription Pipeline

Transcribes audio files and labels who said what using:
- WhisperX for speech-to-text + word-level alignment
- Pyannote for speaker diarization

Usage:
    python transcribe.py meeting.wav
    python transcribe.py meeting.wav --model large-v2 --device cuda
    python transcribe.py meeting.wav --min-speakers 2 --max-speakers 5
    python transcribe.py meeting.wav --output transcript.txt

Environment:
    HF_TOKEN: HuggingFace access token (required for speaker diarization)
"""

import argparse
import gc
import json
import os
import sys
from datetime import timedelta
from pathlib import Path

import whisperx


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS.mmm format."""
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    millis = int((seconds - total_seconds) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def transcribe(
    audio_file: str,
    model_name: str = "large-v2",
    device: str = "cpu",
    batch_size: int = 16,
    compute_type: str = "float16",
    hf_token: str | None = None,
    language: str | None = None,
    min_speakers: int | None = None,
    max_speakers: int | None = None,
) -> dict:
    """
    Transcribe an audio file with speaker diarization.

    Args:
        audio_file: Path to the audio file.
        model_name: Whisper model size (tiny, base, small, medium, large-v2).
        device: "cuda" for GPU, "cpu" for CPU.
        batch_size: Batch size for transcription. Lower if OOM.
        compute_type: "float16" for GPU, "float32" for CPU, "int8" for low VRAM.
        hf_token: HuggingFace token for pyannote models.
        language: Language code (e.g. "en"). Auto-detected if None.
        min_speakers: Minimum expected speakers (helps diarization accuracy).
        max_speakers: Maximum expected speakers (helps diarization accuracy).

    Returns:
        Dict with "segments" containing transcribed text with speaker labels.
    """
    if device == "cpu" and compute_type == "float16":
        compute_type = "float32"

    # Step 1: Transcribe
    print(f"Loading model '{model_name}' on {device} ({compute_type})...")
    model = whisperx.load_model(model_name, device, compute_type=compute_type)

    print("Loading audio...")
    audio = whisperx.load_audio(audio_file)

    print("Transcribing...")
    result = model.transcribe(audio, batch_size=batch_size, language=language)
    detected_language = result["language"]
    print(f"Detected language: {detected_language}")

    # Step 2: Align word-level timestamps
    print("Aligning word timestamps...")
    model_a, metadata = whisperx.load_align_model(
        language_code=detected_language, device=device
    )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    # Free alignment model memory
    del model, model_a
    gc.collect()

    # Step 3: Diarize (speaker identification)
    if hf_token:
        print("Running speaker diarization...")
        diarize_model = whisperx.DiarizationPipeline(
            use_auth_token=hf_token, device=device
        )

        diarize_kwargs = {}
        if min_speakers is not None:
            diarize_kwargs["min_speakers"] = min_speakers
        if max_speakers is not None:
            diarize_kwargs["max_speakers"] = max_speakers

        diarize_segments = diarize_model(audio, **diarize_kwargs)
        result = whisperx.assign_word_speakers(diarize_segments, result)

        del diarize_model
        gc.collect()
    else:
        print("WARNING: No HF_TOKEN provided — skipping speaker diarization.")

    return result


def write_txt(segments: list[dict], path: Path) -> None:
    """Write a plain text transcript."""
    with open(path, "w") as f:
        for seg in segments:
            speaker = seg.get("speaker", "UNKNOWN")
            start = format_timestamp(seg["start"])
            end = format_timestamp(seg["end"])
            text = seg["text"].strip()
            f.write(f"[{start} - {end}] {speaker}: {text}\n")


def write_srt(segments: list[dict], path: Path) -> None:
    """Write an SRT subtitle file."""
    with open(path, "w") as f:
        for i, seg in enumerate(segments, 1):
            speaker = seg.get("speaker", "UNKNOWN")
            start = format_timestamp(seg["start"]).replace(".", ",")
            end = format_timestamp(seg["end"]).replace(".", ",")
            text = seg["text"].strip()
            f.write(f"{i}\n{start} --> {end}\n{speaker}: {text}\n\n")


def write_json(result: dict, path: Path) -> None:
    """Write full result as JSON."""
    with open(path, "w") as f:
        json.dump(result, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe meeting audio with speaker labels."
    )
    parser.add_argument("audio", help="Path to audio file (wav, mp3, m4a, etc.)")
    parser.add_argument(
        "--model",
        default="large-v2",
        choices=["tiny", "base", "small", "medium", "large-v2"],
        help="Whisper model size (default: large-v2)",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        choices=["cpu", "cuda"],
        help="Device to use (default: cpu)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Batch size for transcription (default: 16, lower if OOM)",
    )
    parser.add_argument(
        "--compute-type",
        default="float16",
        choices=["float16", "float32", "int8"],
        help="Compute type (default: float16; use float32 for CPU, int8 for low VRAM)",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Language code e.g. 'en' (auto-detected if omitted)",
    )
    parser.add_argument(
        "--hf-token",
        default=os.environ.get("HF_TOKEN"),
        help="HuggingFace token (default: $HF_TOKEN env var)",
    )
    parser.add_argument(
        "--min-speakers",
        type=int,
        default=None,
        help="Minimum number of speakers (improves diarization if known)",
    )
    parser.add_argument(
        "--max-speakers",
        type=int,
        default=None,
        help="Maximum number of speakers (improves diarization if known)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <audio_name>_transcript.txt)",
    )
    parser.add_argument(
        "--output-format",
        nargs="+",
        default=["txt"],
        choices=["txt", "srt", "json", "all"],
        help="Output formats (default: txt)",
    )

    # Speaker name mapping
    parser.add_argument(
        "--speakers",
        nargs="+",
        metavar="LABEL=NAME",
        help="Map speaker labels to names, e.g. SPEAKER_00=Alice SPEAKER_01=Bob",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: File not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    if not args.hf_token:
        print(
            "WARNING: No HuggingFace token found. Set HF_TOKEN env var or use "
            "--hf-token for speaker diarization.",
            file=sys.stderr,
        )

    # Run transcription
    result = transcribe(
        audio_file=str(audio_path),
        model_name=args.model,
        device=args.device,
        batch_size=args.batch_size,
        compute_type=args.compute_type,
        hf_token=args.hf_token,
        language=args.language,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
    )

    segments = result.get("segments", [])

    # Apply speaker name mapping
    if args.speakers:
        name_map = {}
        for mapping in args.speakers:
            if "=" not in mapping:
                print(
                    f"WARNING: Invalid speaker mapping '{mapping}', expected LABEL=NAME",
                    file=sys.stderr,
                )
                continue
            label, name = mapping.split("=", 1)
            name_map[label] = name

        for seg in segments:
            speaker = seg.get("speaker", "")
            if speaker in name_map:
                seg["speaker"] = name_map[speaker]

    # Determine output base path
    if args.output:
        out_base = Path(args.output).with_suffix("")
    else:
        out_base = audio_path.with_name(f"{audio_path.stem}_transcript")

    # Resolve formats
    formats = set(args.output_format)
    if "all" in formats:
        formats = {"txt", "srt", "json"}

    # Write outputs
    for fmt in formats:
        out_path = out_base.with_suffix(f".{fmt}")
        if fmt == "txt":
            write_txt(segments, out_path)
        elif fmt == "srt":
            write_srt(segments, out_path)
        elif fmt == "json":
            write_json(result, out_path)
        print(f"Saved: {out_path}")

    # Print to stdout
    print(f"\n{'='*60}")
    print(f"Transcript ({len(segments)} segments)")
    print(f"{'='*60}\n")
    for seg in segments:
        speaker = seg.get("speaker", "UNKNOWN")
        text = seg["text"].strip()
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        print(f"[{start} - {end}] {speaker}: {text}")


if __name__ == "__main__":
    main()
