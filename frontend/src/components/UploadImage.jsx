import React, { useState } from 'react';

const UploadImage = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);

    const onSelectFile = e => {
        if (!e.target.files || e.target.files.length === 0) {
            setSelectedFile(undefined);
            return;
        }
        setSelectedFile(e.target.files[0]);
        const objectUrl = URL.createObjectURL(e.target.files[0]);
        setPreview(objectUrl);
    };

    return (
        <div className="upload-container">
            <h3>Upload Image for Analysis</h3>
            <input type='file' onChange={onSelectFile} />
            {preview && <img src={preview} alt="Preview" style={{ maxWidth: '300px' }} />}
            {/* Logic to send to backend would go here */}
        </div>
    );
};

export default UploadImage;
