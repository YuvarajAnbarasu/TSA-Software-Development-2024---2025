let mediaRecorder;
let recordedChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const videoPreview = document.getElementById("videoPreview");
const fileInput = document.getElementById("videoFile");
const uploadForm = document.getElementById("uploadForm");

startBtn.addEventListener("click", async () => {
  recordedChunks = [];

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    });

    videoPreview.srcObject = stream;
    videoPreview.play();

    mediaRecorder = new MediaRecorder(stream, {
      mimeType: "video/webm; codecs=vp8,opus"
    });

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        recordedChunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async (e) => {
      stream.getTracks().forEach(track => track.stop());

      const blob = new Blob(recordedChunks, { type: "video/webm" });

      const file = new File([blob], "interview.webm", { type: "video/webm" });

      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(file);
      fileInput.files = dataTransfer.files;

      uploadForm.submit();
    };

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;

  } catch (err) {
    console.error("Error accessing camera/mic:", err);
    alert("Could not access camera/microphone. Check permissions.");
  }
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});
