import { useState, useRef, useEffect } from "react";
import { Camera, RefreshCw, Upload, Loader2, Video, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import EmotionBadge from "./EmotionBadge";
import { analyzeFace, analyzeFaceImage } from "@/services/api";
import { getErrorMessage } from "@/services/errorHandler";

interface FaceResult {
  emotion: string;
  confidence: number;
  method?: string;
}

const WebcamCapture = ({
  onResult,
}: {
  onResult?: (result: FaceResult) => void;
}) => {
  const [captured, setCaptured] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<FaceResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"upload" | "webcam">("upload");
  const [streaming, setStreaming] = useState(false);
  const [streamingResult, setStreamingResult] = useState<FaceResult | null>(null);
  
  const fileRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize webcam
  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setStreaming(true);
      }
    } catch (error) {
      console.error("Webcam access denied:", error);
      alert("Unable to access webcam. Please check permissions.");
    }
  };

  // Stop webcam
  const stopWebcam = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
      videoRef.current.srcObject = null;
    }
    setStreaming(false);
    setStreamingResult(null);
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
    }
  };

  // Capture frame from video
  const captureFrame = async () => {
    if (!videoRef.current || !canvasRef.current) return null;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return null;

    // Set canvas size to match video
    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;

    // Draw video frame to canvas
    ctx.drawImage(videoRef.current, 0, 0);

    // Convert to base64
    return canvasRef.current.toDataURL("image/jpeg");
  };

  // Analyze single webcam frame
  const analyzeWebcamFrame = async () => {
    const frameBase64 = await captureFrame();
    if (!frameBase64) return;

    console.log("BASE64:", frameBase64?.slice(0, 50));
    setLoading(true);
    setError(null);
    try {
      const response = await analyzeFaceImage(frameBase64);
      setStreamingResult(response);
      setError(null);
      onResult?.(response);
    } catch (error: any) {
      console.error("Webcam analysis error:", error);
      const errorMsg = getErrorMessage(error, "Face analysis");
      setError(errorMsg);
      setStreamingResult(null);
    } finally {
      setLoading(false);
    }
  };

  // Start continuous streaming
  const startStreaming = async () => {
    setLoading(true);
    // Capture frame every 2 seconds
    streamIntervalRef.current = setInterval(analyzeWebcamFrame, 2000);
    // Analyze first frame immediately
    setTimeout(analyzeWebcamFrame, 500);
    setLoading(false);
  };

  // Stop continuous streaming
  const stopStreaming = () => {
    if (streamIntervalRef.current) {
      clearInterval(streamIntervalRef.current);
    }
    setLoading(false);
  };

  // Handle file upload
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setCaptured(url);
    setFile(file);
    setResult(null);
  };

  // Analyze uploaded image
  const analyzeUploaded = async () => {
    if (!file) return;

    console.log("FILE:", file);
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("image", file);
      const analysisResult = await analyzeFace(formData);
      setResult(analysisResult);
      setError(null);
      onResult?.(analysisResult);
    } catch (error: any) {
      console.error("Analysis error:", error);
      const errorMsg = getErrorMessage(error, "Image analysis");
      setError(errorMsg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  // Switch mode
  const switchMode = (newMode: "upload" | "webcam") => {
    if (newMode === "webcam" && !streaming) {
      startWebcam();
    } else if (newMode === "upload" && streaming) {
      stopWebcam();
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
      }
    }
    setMode(newMode);
    setResult(null);
    setStreamingResult(null);
    setError(null);
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
      }
      stopWebcam();
    };
  }, []);

  const reset = () => {
    setCaptured(null);
    setFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="space-y-4">
      {/* Mode Toggle */}
      <div className="flex gap-2 border border-border rounded-lg p-1 bg-muted/30">
        <Button
          variant={mode === "upload" ? "default" : "ghost"}
          size="sm"
          onClick={() => switchMode("upload")}
          className="flex-1"
        >
          <Upload className="w-4 h-4 mr-2" /> Upload
        </Button>
        <Button
          variant={mode === "webcam" ? "default" : "ghost"}
          size="sm"
          onClick={() => switchMode("webcam")}
          className="flex-1"
        >
          <Video className="w-4 h-4 mr-2" /> Live
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm animate-fade-in">
          {error}
        </div>
      )}

      {/* Upload Mode */}
      {mode === "upload" && (
        <>
          <div className="relative rounded-xl overflow-hidden bg-muted/50 border-2 border-dashed border-border aspect-video max-h-64 flex items-center justify-center">
            {captured ? (
              <img
                src={captured}
                alt="Captured"
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="flex flex-col items-center gap-3 text-muted-foreground p-6">
                <Camera className="w-12 h-12 opacity-40" />
                <p className="text-sm font-medium">
                  Upload a photo for emotion detection
                </p>
              </div>
            )}
            {loading && (
              <div className="absolute inset-0 bg-background/60 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            )}
          </div>

          <div className="flex gap-2 flex-wrap">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fileRef.current?.click()}
              className="flex items-center gap-2"
            >
              <Upload className="w-4 h-4" /> Upload Photo
            </Button>
            {captured && (
              <>
                <Button
                  size="sm"
                  className="btn-primary"
                  onClick={analyzeUploaded}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin mr-1" /> Analyzing...
                    </>
                  ) : (
                    "Analyze Emotion"
                  )}
                </Button>
                <Button variant="ghost" size="sm" onClick={reset}>
                  <RefreshCw className="w-4 h-4" />
                </Button>
              </>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFile}
            />
          </div>

          {result && (
            <div className="p-4 rounded-xl bg-muted/40 border border-border animate-fade-in">
              <p className="text-xs text-muted-foreground font-medium mb-2">
                Detection Result
              </p>
              <EmotionBadge
                emotion={result.emotion}
                confidence={result.confidence}
              />
              {result.method && (
                <p className="text-xs text-muted-foreground mt-2">
                  Method: {result.method}
                </p>
              )}
            </div>
          )}
        </>
      )}

      {/* Webcam Mode */}
      {mode === "webcam" && (
        <>
          <div className="relative rounded-xl overflow-hidden bg-black border-2 border-border aspect-video max-h-64 flex items-center justify-center">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
            />
            {loading && (
              <div className="absolute inset-0 bg-background/60 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
              </div>
            )}
          </div>

          <div className="flex gap-2 flex-wrap">
            {!loading && streamIntervalRef.current === null ? (
              <Button
                size="sm"
                className="btn-primary flex items-center gap-2"
                onClick={startStreaming}
              >
                <Video className="w-4 h-4" /> Start Streaming
              </Button>
            ) : (
              <Button
                size="sm"
                variant="destructive"
                className="flex items-center gap-2"
                onClick={stopStreaming}
              >
                <Square className="w-4 h-4" /> Stop
              </Button>
            )}
            <Button variant="ghost" size="sm" onClick={stopWebcam}>
              <RefreshCw className="w-4 h-4" />
            </Button>
          </div>

          {streamingResult && (
            <div className="p-4 rounded-xl bg-muted/40 border border-border animate-fade-in">
              <p className="text-xs text-muted-foreground font-medium mb-2">
                Real-Time Detection
              </p>
              <EmotionBadge
                emotion={streamingResult.emotion}
                confidence={streamingResult.confidence}
              />
              {streamingResult.method && (
                <p className="text-xs text-muted-foreground mt-2">
                  Method: {streamingResult.method}
                </p>
              )}
            </div>
          )}
        </>
      )}

      {/* Hidden canvas for frame capture */}
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
};

export default WebcamCapture;
