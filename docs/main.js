const apiBaseInput = document.getElementById('apiBase');
const videoInput = document.getElementById('videoInput');
const extractBtn = document.getElementById('extractBtn');
const errorBox = document.getElementById('errorBox');
const resultBox = document.getElementById('resultBox');
const transcriptText = document.getElementById('transcriptText');

const storedApiBase = localStorage.getItem('apiBaseUrl') || 'http://localhost:5000';
apiBaseInput.value = storedApiBase;

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove('hidden');
}

function clearError() {
  errorBox.textContent = '';
  errorBox.classList.add('hidden');
}

function showResult(text) {
  transcriptText.value = text;
  resultBox.classList.remove('hidden');
}

function clearResult() {
  transcriptText.value = '';
  resultBox.classList.add('hidden');
}

extractBtn.addEventListener('click', async () => {
  clearError();
  clearResult();

  const apiBase = apiBaseInput.value.trim().replace(/\/$/, '');
  const video = videoInput.value.trim();

  localStorage.setItem('apiBaseUrl', apiBase);

  if (!apiBase) {
    showError('API Base URLを入力してください。');
    return;
  }
  if (!video) {
    showError('YouTube URLまたは動画IDを入力してください。');
    return;
  }

  const url = `${apiBase}/api/transcript?video=${encodeURIComponent(video)}`;

  try {
    const response = await fetch(url);
    const payload = await response.json();

    if (!response.ok) {
      showError(payload.error || 'Transcript取得に失敗しました。');
      return;
    }

    showResult(payload.transcript || '');
  } catch (error) {
    showError(`API通信に失敗しました: ${error}`);
  }
});
