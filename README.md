# WhisperX + Pyannote: In-Person Meeting Transcription

A local pipeline that records in-person meetings, transcribes the audio, and labels who said what — all running on your own machine with no cloud costs.

**Stack:** WhisperX (transcription + alignment) → Pyannote (speaker diarization) → labeled transcript

## Prerequisites

| Requirement            | Details                                              |
|------------------------|------------------------------------------------------|
| **Python**             | 3.9–3.12                                             |
| **ffmpeg**             | For audio processing                                 |
| **GPU (recommended)**  | NVIDIA with CUDA 12.8 — runs on CPU too, just slower |
| **HuggingFace account**| Free — needed for pyannote model access              |
| **RAM**                | 8 GB minimum, 16 GB recommended                     |

## Quick Start

### 1. Accept Pyannote Model Licenses

> **This is the step most people miss — nothing works without it.**

1. Create an account at [huggingface.co](https://huggingface.co)
2. Accept the license at [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)
3. Accept the license at [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0)
4. Create an access token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### 2. Install ffmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (with chocolatey)
choco install ffmpeg
```

### 3. Install Python Dependencies

```bash
# Create and activate a virtual environment
python -m venv whisperx-env
source whisperx-env/bin/activate  # Linux/Mac
# whisperx-env\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

**GPU users:** Also install CUDA toolkit 12.8 from [developer.nvidia.com/cuda-downloads](https://developer.nvidia.com/cuda-downloads).

### 4. Set Your HuggingFace Token

```bash
export HF_TOKEN="hf_your_token_here"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### 5. Transcribe

**Python script (recommended — more options):**

```bash
# Basic (CPU)
python transcribe.py meeting.wav

# With GPU
python transcribe.py meeting.wav --device cuda

# Faster with a smaller model
python transcribe.py meeting.wav --model small

# Specify speaker count for better accuracy
python transcribe.py meeting.wav --min-speakers 2 --max-speakers 5

# All output formats
python transcribe.py meeting.wav --output-format all

# Map speaker labels to real names
python transcribe.py meeting.wav --speakers SPEAKER_00=Alice SPEAKER_01=Bob
```

**Shell wrapper (quick & simple):**

```bash
chmod +x transcribe.sh
./transcribe.sh meeting.wav                  # CPU, large-v2
./transcribe.sh meeting.wav small            # CPU, small model
./transcribe.sh meeting.wav large-v2 cuda    # GPU, large-v2
```

The shell script saves transcripts to `./transcripts/YYYY-MM-DD/`.

## Recording Tips

For best results with in-person meetings:

- **Place the mic centrally** so all speakers are roughly equal volume
- **Minimize background noise** — close doors, turn off fans
- **One speaker at a time** — overlapping speech is the hardest case for diarization

Recording options:
- **Phone voice memo** — simplest, export as `.wav` or `.m4a`
- **USB microphone** — better quality
- **Dedicated recorder** (e.g. Zoom H1n) — best results

## Python Script Options

```
usage: transcribe.py [-h] [--model {tiny,base,small,medium,large-v2}]
                     [--device {cpu,cuda}] [--batch-size N]
                     [--compute-type {float16,float32,int8}]
                     [--language LANG] [--hf-token TOKEN]
                     [--min-speakers N] [--max-speakers N]
                     [--output PATH] [--output-format {txt,srt,json,all}]
                     [--speakers LABEL=NAME [LABEL=NAME ...]]
                     audio

  audio               Path to audio file (wav, mp3, m4a, etc.)
  --model             Whisper model size (default: large-v2)
  --device            cpu or cuda (default: cpu)
  --batch-size        Batch size for transcription (default: 16, lower if OOM)
  --compute-type      float16 (GPU), float32 (CPU), int8 (low VRAM)
  --language          Language code e.g. "en" (auto-detected if omitted)
  --hf-token          HuggingFace token (default: $HF_TOKEN)
  --min-speakers      Minimum expected speakers
  --max-speakers      Maximum expected speakers
  --output            Output path (default: <audio>_transcript.txt)
  --output-format     txt, srt, json, or all (default: txt)
  --speakers          Map labels to names: SPEAKER_00=Alice SPEAKER_01=Bob
```

## Model Size Tradeoffs

| Model      | VRAM   | Speed     | Accuracy | Best for                   |
|------------|--------|-----------|----------|----------------------------|
| `tiny`     | ~1 GB  | Very fast | Lower    | Quick drafts, testing      |
| `base`     | ~1 GB  | Fast      | OK       | Short meetings             |
| `small`    | ~2 GB  | Moderate  | Good     | Daily use                  |
| `medium`   | ~5 GB  | Slower    | Better   | Important meetings         |
| `large-v2` | ~10 GB | Slowest   | Best     | When accuracy matters most |

**No GPU?** Use `small` or `medium` with `--compute-type float32 --device cpu`. A 1-hour meeting takes roughly 10–30 minutes to process.

## Output Formats

- **`.txt`** — Plain text with timestamps and speaker labels
- **`.srt`** — Subtitle format, importable into video editors
- **`.json`** — Full structured data including word-level timestamps

Example `.txt` output:
```
[00:00:01.200 - 00:00:04.800] SPEAKER_00: Welcome everyone, let's get started.
[00:00:05.100 - 00:00:08.900] SPEAKER_01: Thanks. I have updates on the Q3 roadmap.
```

## Speaker Name Mapping

WhisperX outputs generic labels (`SPEAKER_00`, `SPEAKER_01`, etc.). Two ways to map them:

**Option 1: Command-line flag**
```bash
python transcribe.py meeting.wav --speakers SPEAKER_00=Alice SPEAKER_01=Bob
```

**Option 2: Manual find-and-replace** — listen to the first few seconds, identify voices, then search-replace in the output file.

## Troubleshooting

| Problem                             | Fix                                                                    |
|-------------------------------------|------------------------------------------------------------------------|
| `CUDA out of memory`                | Reduce `--batch-size` to 4, or use `--compute-type int8`               |
| `401 Unauthorized` from HuggingFace | Accept the pyannote model licenses (see Quick Start step 1)            |
| Wrong number of speakers detected   | Use `--min-speakers` and `--max-speakers` if you know the count        |
| Poor speaker separation             | Improve mic placement, reduce background noise                         |
| Overlapping speech mislabeled       | Known limitation — works OK but not perfectly with overlapping speech   |
| Slow on CPU                         | Use a smaller model (`small` or `medium`) or use a GPU                 |

## Cost

| Item                 | Cost                                            |
|----------------------|-------------------------------------------------|
| WhisperX + Pyannote  | Free (open source)                              |
| HuggingFace account  | Free                                            |
| GPU cloud (optional) | ~$0.50–1.00/hr on vast.ai or Lambda             |
| Your hardware        | One-time — any modern laptop works for CPU mode |

**Total ongoing cost: $0** if running locally.
