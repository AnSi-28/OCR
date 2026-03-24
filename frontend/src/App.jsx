import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState("");
  const [copied, setCopied] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert("Upload a file first");

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setText("");
    setImageUrl("");

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/upload/",
        formData
      );

      if (res.data.error) {
        alert(res.data.error);
        return;
      }

      setText(res.data.extracted_text || "");
      setImageUrl(res.data.image_url || "");
    } catch (err) {
      console.error(err);
      alert("Upload failed");
    }

    setLoading(false);
  };

  const handleCopy = async () => {
    if (!text) return;

    await navigator.clipboard.writeText(text);
    setCopied(true);

    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="container">
      <div className="title">OCR Analyzer</div>

      {/* Upload Section */}
      <div className="card">
        <div className="section-title">Upload File</div>

        <input
          type="file"
          accept="image/*,.pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />

        {file && (
          <img
            src={URL.createObjectURL(file)}
            alt="preview"
            className="preview-img"
          />
        )}

        <br /><br />

        <button onClick={handleUpload} disabled={loading}>
          {loading ? "Processing..." : "Upload & Analyze"}
        </button>
      </div>

      {/* OCR TEXT SECTION */}
      <div className="card">
        <div className="text-header">
          <div className="section-title">Extracted Text</div>

          <button className="copy-btn" onClick={handleCopy}>
            {copied ? "Copied ✓" : "Copy"}
          </button>
        </div>

        <div className="text-output">
          {loading ? (
            <p className="placeholder">Processing image...</p>
          ) : text ? (
            text.split("\n").map((line, index) => (
              <p key={index}>{line}</p>
            ))
          ) : (
            <p className="placeholder">No text extracted yet</p>
          )}
        </div>
      </div>

      {/* IMAGE OUTPUT */}
      {imageUrl && (
        <div className="card">
          <div className="section-title">Detected Regions</div>
          <img src={imageUrl} alt="Processed" className="output-img" />
        </div>
      )}
    </div>
  );
}

export default App;