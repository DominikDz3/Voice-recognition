document.addEventListener('DOMContentLoaded', () => {
    const recordButton = document.getElementById('record-button');
    const submitButton = document.getElementById('submit-button');
    const voiceFileInput = document.getElementById('voice-file-input');
    const indicator = document.getElementById('recording-indicator');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Twoja przeglądarka nie wspiera nagrywania audio.');
        recordButton.disabled = true;
        return;
    }

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // Funkcja, która uruchamia się po zatrzymaniu nagrywania
    const onRecordingStop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], "voice.webm", { type: 'audio/webm' });

        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(audioFile);
        voiceFileInput.files = dataTransfer.files;

        submitButton.disabled = false;
        audioChunks = [];
    };

    // Główna obsługa kliknięcia przycisku
    recordButton.addEventListener('click', async () => {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);

                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener('stop', onRecordingStop);

                mediaRecorder.start();
                isRecording = true;

                indicator.style.display = 'flex';
                recordButton.innerHTML = '<i class="bi bi-stop-circle-fill"></i> Zatrzymaj Nagrywanie';
                recordButton.classList.remove('btn-primary', 'btn-danger');
                recordButton.classList.add('btn-warning');
                submitButton.disabled = true;

            } catch (err) {
                console.error('Błąd dostępu do mikrofonu:', err);
                alert('Nie udało się uzyskać dostępu do mikrofonu. Sprawdź uprawnienia w przeglądarce.');
            }
        }

        else {
            mediaRecorder.stop();
            isRecording = false;

            indicator.style.display = 'none';
            recordButton.innerHTML = '<i class="bi bi-mic"></i> Nagraj Ponownie';
            recordButton.classList.remove('btn-warning');
            recordButton.classList.add('btn-primary');
        }
    });
});