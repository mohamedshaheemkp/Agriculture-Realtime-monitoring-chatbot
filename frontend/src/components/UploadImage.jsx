import React, { useState } from 'react';
import axios from 'axios';

const UploadImage = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const onSelectFile = e => {
        if (!e.target.files || e.target.files.length === 0) {
            setSelectedFile(undefined);
            return;
        }
        const file = e.target.files[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
        setResult(null);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;

        setLoading(true);
        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const res = await axios.post("http://localhost:5050/predict-image", formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setResult(res.data);
        } catch (error) {
            console.error("Upload error", error);
            setResult([{ label: "Error analyzing image", confidence: 0 }]);
        }
        setLoading(false);
    };

    return (
        <div className="upload-container">
            <h3>Diagnostic Tool</h3>
            <p>Upload a clear photo of a leaf or fruit.</p>
            <div className="upload-controls">
                <input type='file' accept="image/*" onChange={onSelectFile} />
                <button onClick={handleUpload} disabled={!selectedFile || loading}>
                    {loading ? "Analyzing..." : "Analyze"}
                </button>
            </div>

            {preview && (
                <div style={{ marginTop: '10px' }}>
                    <img src={preview} alt="Preview" style={{ maxWidth: '200px', borderRadius: '8px' }} />
                </div>
            )}

            {result && (
                <div className="results">
                    <h4>Analysis Results:</h4>
                    {result.length === 0 ? <p>No specific pests/diseases detected.</p> : (
                        <ul>
                            {result.map((d, i) => (
                                <li key={i}>
                                    <strong>{d.label}</strong> ({(d.confidence * 100).toFixed(1)}%)
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            )}
        </div>
    );
};

export default UploadImage;
