
import os
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


from flask import Flask, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename
from PIL import Image, ImageFilter, ImageEnhance

from services.text_service import analyze_text
from services.chart_service import create_word_chart


app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# HOME
@app.route("/")
def home():
    return render_template("index.html")


# TEXT INTELLIGENCE
@app.route("/text", methods=["GET", "POST"])
def text():
    result = None

    if request.method == "POST":
        user_text = request.form.get("paragraph", "")

        if user_text.strip():
            result = analyze_text(user_text)
            create_word_chart(result["most_frequent_words"])

    return render_template("text.html", result=result)


# WEB INTELLIGENCE
@app.route("/web", methods=["GET", "POST"])
def web():
    print("Web route opened")

    if request.method == "POST":
        print("POST request received")

        url = request.form.get("url", "")

        print("Website URL:", url)

    return render_template("web.html")


# IMAGE PROCESSING
@app.route("/image", methods=["GET", "POST"])
def image():
    original_path = None
    processed_path = None

    if request.method == "POST":
        uploaded_file = request.files.get("image")

        if uploaded_file and uploaded_file.filename:

            filename = secure_filename(uploaded_file.filename)

            original_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            uploaded_file.save(original_file_path)

            original_path = url_for(
                "uploaded_image",
                filename=filename
            )

            img = Image.open(original_file_path)

            # RESIZE
            width = request.form.get("width")
            height = request.form.get("height")

            if width and height:
                width = int(width)
                height = int(height)

                if width > 0 and height > 0:
                    img = img.resize((width, height))

            # GRAYSCALE
            grayscale = request.form.get("grayscale")

            if grayscale == "yes":
                img = img.convert("L")

            # ROTATE
            rotation = request.form.get("rotation", "0")

            if rotation == "90":
                img = img.rotate(-90, expand=True)

            elif rotation == "180":
                img = img.rotate(180, expand=True)

            elif rotation == "270":
                img = img.rotate(-270, expand=True)

            # FLIP
            flip = request.form.get("flip", "none")

            if flip == "horizontal":
                img = img.transpose(
                    Image.Transpose.FLIP_LEFT_RIGHT
                )

            elif flip == "vertical":
                img = img.transpose(
                    Image.Transpose.FLIP_TOP_BOTTOM
                )

            # BLUR
            blur = float(request.form.get("blur", "0"))

            if blur > 0:
                img = img.filter(
                    ImageFilter.GaussianBlur(blur)
                )

            # SHARPEN
            sharpen = float(request.form.get("sharpen", "0"))

            if sharpen > 0:
                enhancer = ImageEnhance.Sharpness(img)
                img = enhancer.enhance(sharpen)

            # BRIGHTNESS
            brightness = float(
                request.form.get("brightness", "1")
            )

            if brightness != 1:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness)

            # CONTRAST
            contrast = float(
                request.form.get("contrast", "1")
            )

            if contrast != 1:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(contrast)

            # CROP
            crop_left = request.form.get("crop_left")
            crop_top = request.form.get("crop_top")
            crop_width = request.form.get("crop_width")
            crop_height = request.form.get("crop_height")

            if (
                crop_left
                and crop_top
                and crop_width
                and crop_height
            ):
                left = int(crop_left)
                top = int(crop_top)

                right = left + int(crop_width)
                bottom = top + int(crop_height)

                if (
                    left >= 0
                    and top >= 0
                    and right <= img.width
                    and bottom <= img.height
                    and right > left
                    and bottom > top
                ):
                    img = img.crop(
                        (left, top, right, bottom)
                    )

            # FORMAT CONVERSION
            image_format = request.form.get("format", "PNG")

            if image_format == "JPEG":
                img = img.convert("RGB")
                extension = "jpg"

            elif image_format == "WEBP":
                extension = "webp"

            else:
                image_format = "PNG"
                extension = "png"

            # SAVE PROCESSED IMAGE
            processed_filename = (
                os.path.splitext(filename)[0]
                + "_processed."
                + extension
            )

            processed_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                processed_filename
            )

            img.save(
                processed_file_path,
                format=image_format
            )

            processed_path = url_for(
                "uploaded_image",
                filename=processed_filename
            )

    return render_template(
        "image.html",
        original_path=original_path,
        processed_path=processed_path
    )


# DISPLAY UPLOADED AND PROCESSED IMAGES
@app.route("/uploads/<filename>")
def uploaded_image(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# AUDIO

# AUDIO INTELLIGENCE

# AUDIO INTELLIGENCE

# AUDIO INTELLIGENCE
@app.route("/audio", methods=["GET", "POST"])
def audio():

    audio_path = None
    filename = None
    audio_format = None
    duration = None
    waveform_path = None
    sample_rate = None

    if request.method == "POST":

        uploaded_file = request.files.get("audio")

        if uploaded_file and uploaded_file.filename:

            filename = secure_filename(uploaded_file.filename)

            audio_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            uploaded_file.save(audio_file_path)

            audio_path = url_for(
                "uploaded_image",
                filename=filename
            )

            audio_format = os.path.splitext(filename)[1].upper()

            # WAV DURATION
            if audio_format == ".WAV":

                import wave

                try:
                    with wave.open(audio_file_path, "rb") as audio_file:

                        frames = audio_file.getnframes()
                        rate = audio_file.getframerate()

                        duration_seconds = frames / rate

                        duration = f"{duration_seconds:.2f} seconds"

                except wave.Error:

                    duration = "Unable to read WAV duration"

            else:

                duration = "Duration available in audio player"

            # WAVEFORM VISUALIZATION
            try:

                audio_data, sample_rate = librosa.load(
                    audio_file_path,
                    sr=None,
                    mono=True
                )

                duration_seconds = len(audio_data) / sample_rate

                if duration is None or duration.startswith("Unable"):
                    duration = f"{duration_seconds:.2f} seconds"

                # Create waveform graph
                plt.figure(figsize=(10, 4))

                librosa.display.waveshow(
                    audio_data,
                    sr=sample_rate
                )

                plt.title("Audio Waveform")
                plt.xlabel("Time (seconds)")
                plt.ylabel("Amplitude")

                plt.tight_layout()

                # Save waveform
                waveform_filename = (
                    os.path.splitext(filename)[0]
                    + "_waveform.png"
                )

                waveform_file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    waveform_filename
                )

                plt.savefig(waveform_file_path)

                plt.close()

                waveform_path = url_for(
                    "uploaded_image",
                    filename=waveform_filename
                )

            except Exception as error:

                print("Waveform error:", error)

                waveform_path = None

    return render_template(
        "audio.html",
        audio_path=audio_path,
        filename=filename,
        audio_format=audio_format,
        duration=duration,
        waveform_path=waveform_path,
        sample_rate=sample_rate
    )



# ANALYTICS
# DATA ANALYTICS
@app.route("/analytics", methods=["GET", "POST"])
def analytics():

    filename = None
    total_rows = None
    total_columns = None
    column_names = None
    dataset_preview = None
    error = None

    if request.method == "POST":

        uploaded_file = request.files.get("csv_file")

        if uploaded_file and uploaded_file.filename:

            filename = secure_filename(uploaded_file.filename)

            if filename.lower().endswith(".csv"):

                file_path = os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )

                uploaded_file.save(file_path)

                try:

                    # Read CSV dataset
                    dataframe = pd.read_csv(file_path)

                    # Dataset information
                    total_rows = dataframe.shape[0]
                    total_columns = dataframe.shape[1]

                    # Column names
                    column_names = dataframe.columns.tolist()

                    # First 5 rows
                    dataset_preview = dataframe.head(5).to_html(
                        classes="data-table",
                        index=False,
                        border=0
                    )

                except Exception as e:

                    error = f"Unable to read CSV file: {e}"

            else:

                error = "Please upload a CSV file."

        else:

            error = "Please select a CSV file."

    return render_template(
        "analytical.html",
        filename=filename,
        total_rows=total_rows,
        total_columns=total_columns,
        column_names=column_names,
        dataset_preview=dataset_preview,
        error=error
    )

# AUTOMATION
@app.route("/automation")
def automation():
    return render_template("automation.html")


# RUN APPLICATION
if __name__ == "__main__":
    app.run(debug=True)
