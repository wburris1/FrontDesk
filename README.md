# FrontDeskAI Voice Assistant

FrontDeskAI is a voice-enabled AI assistant designed for healthcare front-desk tasks, including scheduling appointments, verifying insurance, and answering clinic FAQs.

---

## Features

- Real-time speech-to-text transcription
- Text-to-speech responses
- Integration with an LLM for intelligent conversation
- Automatic handling of appointment scheduling and insurance verification
- Easy start/stop recording functionality

---

## Getting Started

Follow these steps to set up and run the project locally. Note: this project requires Python3 version >= 3.11.0.

### 1. Clone the repository

```bash
git clone https://github.com/wburris1/FrontDesk.git
cd FrontDesk
```

### 2. Copy the environment and enter your credentials

MacOS/Linux
```bash
cp .env.sample .env
```

Windows:
```bash
copy .env.sample .env
```

### 3. Create a virtual environment

```bash
python3 -m venv venv
```

### 4. Activate the virtual environment

MacOS/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the project

```bash
python3 main.py
```

Once started, the assistant will begin listening. Speak naturally, and it will respond to your queries regarding appointments, insurance, and general clinic information.



