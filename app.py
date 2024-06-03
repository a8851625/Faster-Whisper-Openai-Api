from flask import Flask, request, jsonify
import os
import logging
from werkzeug.utils import secure_filename
from faster_whisper import WhisperModel

app = Flask(__name__)

# 配置管理
MODEL_SIZE = os.getenv('MODEL_SIZE', 'large-v3')

# 加载模型
model = WhisperModel(MODEL_SIZE,device="cuda", compute_type="float16")


# 日志配置
logging.basicConfig(level=logging.INFO)

# 支持的音频文件类型
ALLOWED_EXTENSIONS = {'flac', 'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'ogg', 'wav', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe():
    try:
        logging.info("Received transcription request")
        
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Unsupported file type"}), 400

        # 读取其他请求参数
        model_id = request.form.get('model', 'whisper-1')
        language = request.form.get('language', None)
        prompt = request.form.get('prompt', None)
        response_format = request.form.get('response_format', 'json')
        temperature = float(request.form.get('temperature', 0))
        timestamp_granularities = request.form.getlist('timestamp_granularities[]')
        without_timestamps = 'segment' not in timestamp_granularities
        word_timestamps = 'word' in timestamp_granularities

        # 保存临时文件
        filename = secure_filename(file.filename)
        file_path = os.path.join("/tmp", filename)
        file.save(file_path)

        # 使用 faster-whisper 模型进行语音识别
        options = {
            "language": language,
            "temperature": temperature,
            "initial_prompt": prompt,
            "without_timestamps": without_timestamps,
            "word_timestamps": word_timestamps,
        }
        segments, info = model.transcribe(file_path, **options)

        # 删除临时文件
        os.remove(file_path)

        # 根据请求参数生成响应
        if response_format == 'json':
            transcription = " ".join([segment.text for segment in segments])
            logging.info("json: %s", jsonify({"text": transcription}).get_data(as_text=True))
            return jsonify({"text": transcription})
        elif response_format == 'text':
            transcription = "\n".join([segment.text for segment in segments])
            logging.info("text: %s", transcription)
            return transcription
        elif response_format == 'srt':
            srt_output = ""
            for i, segment in enumerate(segments):
                start = segment.start
                end = segment.end
                text = segment.text
                srt_output += f"{i+1}\n{start} --> {end}\n{text}\n\n"
            logging.info("srt: %s", srt_output)
            return srt_output
        elif response_format == 'verbose_json':
            result = {
                "task": "transcribe",
                "language": language or "unknown",
                "duration": info.duration,
                "text": " ".join([segment.text for segment in segments]),
                "words": [
                    {
                        "word": word.text,
                        "start": word.start,
                        "end": word.end
                    } for segment in segments for word in segment.words
                ] if word_timestamps else [],
                "segments": [
                    {
                        "id": i,
                        "seek": segment.seek,
                        "start": segment.start,
                        "end": segment.end,
                        "text": segment.text,
                        "tokens": segment.tokens,
                        "temperature": segment.temperature,
                        "avg_logprob": segment.avg_logprob,
                        "compression_ratio": segment.compression_ratio,
                        "no_speech_prob": segment.no_speech_prob
                    } for i, segment in enumerate(segments)
                ]
            }
            logging.info("ver_json: %s", result)
            return jsonify(result)
        elif response_format == 'vtt':
            vtt_output = "WEBVTT\n\n"
            for segment in segments:
                start = segment.start
                end = segment.end
                text = segment.text
                vtt_output += f"{start} --> {end}\n{text}\n\n"
            logging.info("vtt_output: %s", vtt_output)
            return vtt_output
        else:
            return jsonify({"error": "Invalid response format"}), 400

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

