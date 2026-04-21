import {
  DrawingUtils,
  FaceLandmarker,
  FilesetResolver,
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/+esm";

const MEDIAPIPE_WASM_ROOT =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.21/wasm";
const FACE_MODEL_URL =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

const video = document.getElementById("video");
const overlay = document.getElementById("overlay");
const overlayContext = overlay.getContext("2d");
const startButton = document.getElementById("startButton");
const stopButton = document.getElementById("stopButton");
const mirrorButton = document.getElementById("mirrorButton");
const viewerMask = document.getElementById("viewerMask");
const liveBadge = document.getElementById("liveBadge");

const smileValue = document.getElementById("smileValue");
const moodText = document.getElementById("moodText");
const statusText = document.getElementById("statusText");
const statusHint = document.getElementById("statusHint");
const faceCount = document.getElementById("faceCount");
const fpsValue = document.getElementById("fpsValue");
const verdictText = document.getElementById("verdictText");
const tipText = document.getElementById("tipText");
const scoreCaption = document.getElementById("scoreCaption");
const scoreFill = document.getElementById("scoreFill");
const leftSmileValue = document.getElementById("leftSmileValue");
const rightSmileValue = document.getElementById("rightSmileValue");
const jawOpenValue = document.getElementById("jawOpenValue");
const leftSmileFill = document.getElementById("leftSmileFill");
const rightSmileFill = document.getElementById("rightSmileFill");
const jawOpenFill = document.getElementById("jawOpenFill");
const logicText = document.getElementById("logicText");

let cameraStream = null;
let faceLandmarker = null;
let drawingUtils = null;
let animationFrameId = 0;
let lastVideoTime = -1;
let lastFpsTimestamp = 0;
let frameCounter = 0;
let mirrorEnabled = true;
let isRunning = false;
let isBooting = false;

const state = {
  stableSmileScore: 0,
  fps: 0,
};

function setStatus(title, hint) {
  statusText.textContent = title;
  statusHint.textContent = hint;
}

function setLiveState(isLive) {
  liveBadge.textContent = isLive ? "识别中" : "未开始";
  liveBadge.classList.toggle("live", isLive);
  liveBadge.classList.toggle("idle", !isLive);
}

function formatPercent(score) {
  return `${Math.round(score * 100)}%`;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function getCategoryScore(categories, name) {
  const hit = categories.find((item) => item.categoryName === name);
  return hit ? hit.score : 0;
}

function updateMeter(element, score) {
  element.style.width = `${Math.round(score * 100)}%`;
}

function updateMirrorUI() {
  const method = mirrorEnabled ? "add" : "remove";
  video.classList[method]("is-mirrored");
  overlay.classList[method]("is-mirrored");
  mirrorButton.textContent = `镜像: ${mirrorEnabled ? "开" : "关"}`;
}

function updateFps() {
  frameCounter += 1;
  const now = performance.now();

  if (!lastFpsTimestamp) {
    lastFpsTimestamp = now;
    return;
  }

  const elapsed = now - lastFpsTimestamp;
  if (elapsed >= 1000) {
    state.fps = Math.round((frameCounter * 1000) / elapsed);
    fpsValue.textContent = String(state.fps);
    frameCounter = 0;
    lastFpsTimestamp = now;
  }
}

function resizeOverlay() {
  if (!video.videoWidth || !video.videoHeight) {
    return;
  }

  overlay.width = video.videoWidth;
  overlay.height = video.videoHeight;
}

function resetVisuals() {
  overlayContext.clearRect(0, 0, overlay.width, overlay.height);
  smileValue.textContent = "0";
  moodText.textContent = "等待启动";
  verdictText.textContent = "等待启动";
  tipText.textContent = "先启动摄像头，再看分数变化";
  scoreCaption.textContent = "0 / 100";
  faceCount.textContent = "0";
  fpsValue.textContent = "0";
  leftSmileValue.textContent = "0%";
  rightSmileValue.textContent = "0%";
  jawOpenValue.textContent = "0%";
  updateMeter(scoreFill, 0);
  updateMeter(leftSmileFill, 0);
  updateMeter(rightSmileFill, 0);
  updateMeter(jawOpenFill, 0);
}

function describeSmile(score) {
  if (score >= 78) {
    return {
      mood: "开心大笑",
      verdict: "检测到明显笑容",
      tip: "状态很好，继续保持这个角度。",
    };
  }

  if (score >= 56) {
    return {
      mood: "自然微笑",
      verdict: "已经识别到笑容",
      tip: "稍微抬一点嘴角，分数会更高。",
    };
  }

  if (score >= 34) {
    return {
      mood: "快笑出来了",
      verdict: "表情有轻微上扬",
      tip: "放松面部，轻轻扬起两侧嘴角试试。",
    };
  }

  return {
    mood: "表情平静",
    verdict: "暂未识别到明显笑容",
    tip: "看向镜头，放松后自然微笑更容易识别。",
  };
}

function drawFace(landmarks, smileScore) {
  overlayContext.clearRect(0, 0, overlay.width, overlay.height);

  const lipColor = smileScore >= 56 ? "#6ef2d0" : "#ff9b61";
  const eyeColor = "rgba(195, 224, 255, 0.92)";
  const outlineColor = "rgba(91, 160, 255, 0.45)";

  drawingUtils.drawConnectors(
    landmarks,
    FaceLandmarker.FACE_LANDMARKS_FACE_OVAL,
    { color: outlineColor, lineWidth: 1.2 }
  );
  drawingUtils.drawConnectors(
    landmarks,
    FaceLandmarker.FACE_LANDMARKS_LEFT_EYE,
    { color: eyeColor, lineWidth: 1.3 }
  );
  drawingUtils.drawConnectors(
    landmarks,
    FaceLandmarker.FACE_LANDMARKS_RIGHT_EYE,
    { color: eyeColor, lineWidth: 1.3 }
  );
  drawingUtils.drawConnectors(
    landmarks,
    FaceLandmarker.FACE_LANDMARKS_LIPS,
    { color: lipColor, lineWidth: 2.1 }
  );
}

function renderNoFaceFrame() {
  state.stableSmileScore *= 0.92;
  smileValue.textContent = String(Math.round(state.stableSmileScore));
  moodText.textContent = "未检测到人脸";
  verdictText.textContent = "请把脸移到画面中央";
  tipText.textContent = "镜头尽量与眼睛齐平，并保持稳定光线";
  faceCount.textContent = "0";
  scoreCaption.textContent = `${Math.round(state.stableSmileScore)} / 100`;
  leftSmileValue.textContent = "0%";
  rightSmileValue.textContent = "0%";
  jawOpenValue.textContent = "0%";
  updateMeter(scoreFill, state.stableSmileScore / 100);
  updateMeter(leftSmileFill, 0);
  updateMeter(rightSmileFill, 0);
  updateMeter(jawOpenFill, 0);
  setStatus("运行中", "摄像头已打开，但当前画面里没有稳定识别到人脸");
  overlayContext.clearRect(0, 0, overlay.width, overlay.height);
}

function updateFromResult(result) {
  const faceTotal = result.faceLandmarks.length;
  faceCount.textContent = String(faceTotal);

  if (!faceTotal) {
    renderNoFaceFrame();
    return;
  }

  const categories = result.faceBlendshapes?.[0]?.categories ?? [];
  const leftSmile = getCategoryScore(categories, "mouthSmileLeft");
  const rightSmile = getCategoryScore(categories, "mouthSmileRight");
  const jawOpen = getCategoryScore(categories, "jawOpen");
  const pucker = getCategoryScore(categories, "mouthPucker");
  const pressLeft = getCategoryScore(categories, "mouthPressLeft");
  const pressRight = getCategoryScore(categories, "mouthPressRight");
  const cheekLeft = getCategoryScore(categories, "cheekSquintLeft");
  const cheekRight = getCategoryScore(categories, "cheekSquintRight");

  const baseSmile = (leftSmile + rightSmile) / 2;
  const cheekBoost = ((cheekLeft + cheekRight) / 2) * 0.18;
  const mouthPenalty = pucker * 0.22 + ((pressLeft + pressRight) / 2) * 0.16;
  const jawPenalty = Math.max(0, jawOpen - 0.34) * 0.22;

  const rawSmile = clamp(baseSmile + cheekBoost - mouthPenalty - jawPenalty, 0, 1);
  state.stableSmileScore = state.stableSmileScore * 0.72 + rawSmile * 100 * 0.28;

  const smoothedSmile = Math.round(state.stableSmileScore);
  const smileInfo = describeSmile(smoothedSmile);

  smileValue.textContent = String(smoothedSmile);
  moodText.textContent = smileInfo.mood;
  verdictText.textContent = smileInfo.verdict;
  tipText.textContent = smileInfo.tip;
  scoreCaption.textContent = `${smoothedSmile} / 100`;

  leftSmileValue.textContent = formatPercent(leftSmile);
  rightSmileValue.textContent = formatPercent(rightSmile);
  jawOpenValue.textContent = formatPercent(jawOpen);

  updateMeter(scoreFill, smoothedSmile / 100);
  updateMeter(leftSmileFill, leftSmile);
  updateMeter(rightSmileFill, rightSmile);
  updateMeter(jawOpenFill, jawOpen);

  logicText.textContent =
    `本次主要依据左右嘴角上扬得分（${formatPercent(leftSmile)} / ${formatPercent(rightSmile)}），` +
    `并结合张嘴、噘嘴等干扰项做平滑处理，当前稳定分数为 ${smoothedSmile}。`;

  setStatus("运行中", smileInfo.verdict);
  drawFace(result.faceLandmarks[0], smoothedSmile);
}

async function loadDetector() {
  if (faceLandmarker) {
    return;
  }

  setStatus("加载中", "正在初始化笑容识别模型，这一步首次启动会稍慢一点");
  const vision = await FilesetResolver.forVisionTasks(MEDIAPIPE_WASM_ROOT);
  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: FACE_MODEL_URL,
    },
    runningMode: "VIDEO",
    numFaces: 1,
    outputFaceBlendshapes: true,
  });
  drawingUtils = new DrawingUtils(overlayContext);
}

function stopLoop() {
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
    animationFrameId = 0;
  }
}

async function startCamera() {
  cameraStream = await navigator.mediaDevices.getUserMedia({
    audio: false,
    video: {
      facingMode: "user",
      width: { ideal: 1280 },
      height: { ideal: 720 },
    },
  });

  video.srcObject = cameraStream;

  await new Promise((resolve) => {
    video.onloadedmetadata = () => resolve();
  });

  resizeOverlay();
  await video.play();
}

function stopCamera() {
  if (!cameraStream) {
    return;
  }

  for (const track of cameraStream.getTracks()) {
    track.stop();
  }

  cameraStream = null;
  video.srcObject = null;
}

function detectFrame() {
  if (!isRunning || !faceLandmarker || video.readyState < 2) {
    return;
  }

  try {
    if (video.currentTime !== lastVideoTime) {
      const result = faceLandmarker.detectForVideo(video, performance.now());
      updateFromResult(result);
      updateFps();
      lastVideoTime = video.currentTime;
    }
  } catch (error) {
    console.error(error);
    stopLoop();
    stopCamera();
    isRunning = false;
    viewerMask.classList.remove("hidden");
    setLiveState(false);
    stopButton.disabled = true;
    setStatus("识别失败", "模型运行时出现异常，请重新点击“开启识别”");
    tipText.textContent = "如果持续失败，尝试刷新页面后再打开摄像头。";
    return;
  }

  animationFrameId = requestAnimationFrame(detectFrame);
}

async function startRecognition() {
  if (isRunning || isBooting) {
    return;
  }

  if (!navigator.mediaDevices?.getUserMedia) {
    setStatus("浏览器不支持", "当前环境不支持摄像头访问，请换用较新的 Chrome 或 Edge");
    return;
  }

  isBooting = true;
  startButton.disabled = true;

  try {
    viewerMask.classList.add("hidden");
    await loadDetector();
    await startCamera();

    isRunning = true;
    stopButton.disabled = false;
    setLiveState(true);
    lastVideoTime = -1;
    lastFpsTimestamp = 0;
    frameCounter = 0;
    state.stableSmileScore = 0;
    setStatus("运行中", "摄像头已打开，正在实时分析笑容");

    detectFrame();
  } catch (error) {
    console.error(error);
    viewerMask.classList.remove("hidden");

    const message =
      error && error.name === "NotAllowedError"
        ? "你拒绝了摄像头权限，请在浏览器里重新允许后再试"
        : "摄像头或模型初始化失败，请确认网络和浏览器权限";

    setStatus("启动失败", message);
    tipText.textContent = "如果是首次加载，模型文件可能需要几秒钟下载时间。";
  } finally {
    isBooting = false;
    startButton.disabled = false;
  }
}

function stopRecognition() {
  isRunning = false;
  stopLoop();
  stopCamera();
  viewerMask.classList.remove("hidden");
  setLiveState(false);
  stopButton.disabled = true;
  resetVisuals();
  setStatus("已停止", "摄像头已关闭，可以再次点击“开启识别”重启");
}

startButton.addEventListener("click", startRecognition);
stopButton.addEventListener("click", stopRecognition);
mirrorButton.addEventListener("click", () => {
  mirrorEnabled = !mirrorEnabled;
  updateMirrorUI();
});

window.addEventListener("resize", resizeOverlay);
window.addEventListener("beforeunload", stopRecognition);

updateMirrorUI();
resetVisuals();
setStatus("待机中", "点击“开启识别”后开始分析你的笑容");
setLiveState(false);
