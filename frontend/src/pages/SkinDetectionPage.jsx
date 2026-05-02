import { useMemo, useState } from "react";
import { api } from "../api/client";

export default function SkinDetectionPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : ""), [file]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("image", file);
      const { data } = await api.post("/predict-skin", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(data);
    } catch (requestError) {
      setError(requestError?.response?.data?.detail || "Unable to process the image.");
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError("");
  };

  const confidencePercent = result ? Math.round((result.confidence || 0) * 100) : 0;

  return (
    <section className="grid gap-6 lg:grid-cols-2">
      <div className="glass-card p-6">
        <h2 className="text-2xl font-semibold text-white">Skin Disease Detection</h2>
        <p className="mt-2 text-sm text-slate-300">Upload a clear skin image to get AI-assisted insights.</p>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <input
            type="file"
            accept="image/*"
            className="block w-full rounded-xl border border-white/20 bg-white/10 p-3 text-sm text-slate-100"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={!file || loading}
              className="rounded-xl bg-harmony-500 px-5 py-2 text-white disabled:opacity-50"
            >
              {loading ? "Predicting..." : "Submit Prediction"}
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-xl border border-white/30 px-5 py-2 text-white hover:bg-white/10"
            >
              Reset Upload
            </button>
          </div>
        </form>
        {previewUrl && (
          <img src={previewUrl} alt="Preview" className="mt-5 h-64 w-full rounded-xl object-cover" />
        )}
      </div>

      <div className="glass-card p-6">
        <h3 className="text-xl font-semibold text-white">Prediction Output</h3>
        {!result && !error && <p className="mt-4 text-slate-300">No prediction yet.</p>}
        {error && <p className="mt-4 text-rose-300">{error}</p>}
        {result && (
          <div className="mt-4 space-y-4">
            <div>
              <p className="text-sm text-slate-300">Predicted class</p>
              <p className="text-2xl font-bold text-white">{result.prediction}</p>
            </div>
            <div>
              <p className="mb-2 text-sm text-slate-300">Confidence: {confidencePercent}%</p>
              <div className="h-3 w-full rounded-full bg-white/20">
                <div
                  className="h-3 rounded-full bg-gradient-to-r from-cyan-400 to-harmony-500"
                  style={{ width: `${confidencePercent}%` }}
                />
              </div>
            </div>
            <div>
              <p className="text-sm text-slate-300">Description</p>
              <p className="text-slate-100">{result.description}</p>
            </div>
            <div>
              <p className="text-sm text-slate-300">Recommended Action</p>
              <p className="text-slate-100">{result.recommended_action}</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
