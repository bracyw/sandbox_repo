#!/bin/bash
# transcribe.sh — Wrapper script for quick meeting transcription
#
# Usage:
#   ./transcribe.sh meeting.wav
#   ./transcribe.sh meeting.wav small       # use a smaller/faster model
#   ./transcribe.sh meeting.wav large-v2 cuda  # use GPU
#
# Requires: HF_TOKEN environment variable set

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <audio_file> [model] [device]"
    echo ""
    echo "  audio_file  Path to audio file (wav, mp3, m4a, etc.)"
    echo "  model       Whisper model: tiny, base, small, medium, large-v2 (default: large-v2)"
    echo "  device      cpu or cuda (default: cpu)"
    echo ""
    echo "Environment:"
    echo "  HF_TOKEN    HuggingFace access token (required for speaker diarization)"
    exit 1
fi

INPUT="$1"
MODEL="${2:-large-v2}"
DEVICE="${3:-cpu}"

if [ ! -f "$INPUT" ]; then
    echo "Error: File not found: $INPUT"
    exit 1
fi

if [ -z "${HF_TOKEN:-}" ]; then
    echo "WARNING: HF_TOKEN not set. Speaker diarization will be skipped."
    echo "Get a token at https://huggingface.co/settings/tokens"
fi

OUTPUT_DIR="./transcripts/$(date +%Y-%m-%d)"
mkdir -p "$OUTPUT_DIR"

echo "Transcribing: $INPUT"
echo "Model: $MODEL | Device: $DEVICE"
echo "Output: $OUTPUT_DIR"
echo ""

whisperx "$INPUT" \
    --model "$MODEL" \
    --diarize \
    --hf_token "${HF_TOKEN:-}" \
    --language en \
    --output_dir "$OUTPUT_DIR" \
    --output_format all

echo ""
echo "Done! Transcript saved to $OUTPUT_DIR"
