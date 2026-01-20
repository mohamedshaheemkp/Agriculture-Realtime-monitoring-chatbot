import React, { useState } from 'react';
import { visionService } from '../../services/visionService';
import styles from '../../styles/UploadImage.module.css';

const UploadImage = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const onSelectFile = e => {
        if (!e.target.files || e.target.files.length === 0) return;

        const file = e.target.files[0];
        setSelectedFile(file);
        setPreview(URL.createObjectURL(file));
        setResult(null);
        setError(null);
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError(null);
        try {
            const data = await visionService.analyzeImage(selectedFile);
            setResult(data.detections || []);
        } catch (err) {
            setError("Failed to analyze image. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.container}>
            <h3>Diagnostic Tool</h3>

            <div className={styles.uploadZone}>
                <input
                    type="file"
                    id="fileInput"
                    accept="image/*"
                    onChange={onSelectFile}
                    className={styles.hiddenInput}
                />
                <label htmlFor="fileInput" className={styles.uploadLabel}>
                    {preview ? "Change Photo" : "📂 Click to Upload Leaf Photo"}
                </label>
            </div>

            {preview && (
                <div className={styles.previewContainer}>
                    <img src={preview} alt="Preview" className={styles.previewImage} />
                </div>
            )}

            <button
                onClick={handleAnalyze}
                disabled={!selectedFile || loading}
                style={{
                    padding: '10px',
                    backgroundColor: '#2e7d32',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    opacity: loading ? 0.7 : 1
                }}
            >
                {loading ? "Analyzing..." : "Analyze Disease"}
            </button>

            {loading && <div className={styles.loader}>Running AI Model...</div>}

            {error && <div style={{ color: 'red', textAlign: 'center' }}>{error}</div>}

            {result && (
                <div className={styles.results}>
                    <h4>Detection Results:</h4>
                    {result.length === 0 ? <p>No diseases detected. Plant looks healthy!</p> : (
                        <div>
                            {result.map((d, i) => (
                                <div key={i} className={styles.resultItem}>
                                    <span>{d.label}</span>
                                    <span className={styles.confidence}>{(d.confidence * 100).toFixed(1)}%</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default UploadImage;
