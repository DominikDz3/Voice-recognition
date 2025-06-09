from flask import Flask, render_template, request, redirect, url_for, flash
import os
from verify_voice import verify_voice
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = 'secret_key'
UPLOAD_FOLDER = 'voice_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Funkcja pomocnicza do konwersji audio
def convert_to_wav(source_path, destination_path):
    try:
        audio = AudioSegment.from_file(source_path)
        audio.export(destination_path, format="wav")
        return True
    except Exception as e:
        print(f"Błąd konwersji pliku: {e}")
        return False


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if 'voice' not in request.files or not username:
            flash('Brak pliku głosowego lub nazwy użytkownika.', 'danger')
            return redirect(request.url)

        file = request.files['voice']

        # Zapisz tymczasowy plik webm
        temp_webm_path = os.path.join(UPLOAD_FOLDER, f'{username}_temp.webm')
        file.save(temp_webm_path)

        # Ścieżka docelowa dla pliku WAV
        ref_wav_path = os.path.join(UPLOAD_FOLDER, f'{username}_ref.wav')

        # Konwertuj webm na wav
        if convert_to_wav(temp_webm_path, ref_wav_path):
            flash('Zarejestrowano głos użytkownika pomyślnie.', 'success')
        else:
            flash('Błąd podczas przetwarzania pliku audio.', 'danger')

        # Usuń tymczasowy plik webm
        os.remove(temp_webm_path)

        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        if 'voice' not in request.files or not username:
            flash('Brak pliku głosowego lub nazwy użytkownika.', 'danger')
            return redirect(request.url)

        file = request.files['voice']

        ref_path = os.path.join(UPLOAD_FOLDER, f'{username}_ref.wav')
        if not os.path.exists(ref_path):
            flash('Użytkownik o tej nazwie nie jest zarejestrowany.', 'danger')
            return redirect(url_for('login'))

        # Zapisz i konwertuj próbkę do logowania
        temp_webm_path = os.path.join(UPLOAD_FOLDER, f'{username}_test_temp.webm')
        test_wav_path = os.path.join(UPLOAD_FOLDER, f'{username}_test.wav')
        file.save(temp_webm_path)

        if not convert_to_wav(temp_webm_path, test_wav_path):
            flash('Błąd podczas przetwarzania pliku audio do logowania.', 'danger')
            os.remove(temp_webm_path)  # posprzątaj
            return redirect(url_for('login'))

        # Weryfikacja głosu
        if verify_voice(ref_path, test_wav_path, threshold=1400):
            flash('Logowanie głosowe zakończone sukcesem! ✅', 'success')
        else:
            flash('Logowanie nieudane. Głos nie pasuje. ❌', 'danger')

        # Usuń tymczasowe pliki
        os.remove(temp_webm_path)
        os.remove(test_wav_path)

        return redirect(url_for('index'))
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)