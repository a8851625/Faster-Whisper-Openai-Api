
# Faster-Whisper-OpenAI-API
## Description
The `faster-whisper-openai-api` is an audio transcription service based on the Faster-Whisper model. It supports the transcription of audio files into text and offers multiple output formats, referencing the OpenAI api.
This project involves a web application that utilizes an API endpoint `/v1/audio/transcriptions` to transcribe audio files with different supported formats.
## How to Use
To make a request to this API, send a POST request to `/v1/audio/transcriptions` with the audio file you want to transcribe.
The API accepts the following parameters:
- `file`: The audio file to be transcribed.
- `model`: The model to be used for transcription, default is 'whisper-1'.
- `language`: The language of the audio file.
- `prompt`: The initial prompt.
- `response_format`: The format you want the transcription to be returned in. Options include 'json', 'text', 'srt', 'verbose_json', 'vtt'.
- `temperature`: A float value for the temperature parameter.
- `timestamp_granularities[]`: A list of timestamp granularities.
The API will return a transcription of the audio in the requested format. If there is an error processing the request, the API will return a 400 or 500 error with an error message.
