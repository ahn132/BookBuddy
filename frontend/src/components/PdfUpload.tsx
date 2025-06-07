import React, { useState, DragEvent } from 'react';
import { Box, Typography, Paper, CircularProgress, Alert } from '@mui/material';
import axios from 'axios';
import { setAuthToken } from '../services/api';

const API_URL = 'http://localhost:8000/admin/upload-pdf';

const PdfUpload: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setIsDragActive(true);
  };

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
  };

  const handleDrop = async (e: DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files.length === 0) return;
    
    const file = files[0];
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed.');
      return;
    }

    setUploading(true);
    try {
      const token = localStorage.getItem('token');
      setAuthToken(token || '');
      const formData = new FormData();
      formData.append('file', file);
      await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      setMessage('PDF uploaded successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    
    const file = files[0];
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are allowed.');
      return;
    }

    setUploading(true);
    try {
      const token = localStorage.getItem('token');
      setAuthToken(token || '');
      const formData = new FormData();
      formData.append('file', file);
      await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });
      setMessage('PDF uploaded successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom>
        Upload PDF (Admin Only)
      </Typography>
      <Paper
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          p: 4,
          textAlign: 'center',
          border: '2px dashed #aaa',
          background: isDragActive ? '#f0f0f0' : 'inherit',
          cursor: 'pointer',
        }}
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          id="file-input"
        />
        <label htmlFor="file-input">
          {uploading ? (
            <CircularProgress />
          ) : isDragActive ? (
            <Typography>Drop the PDF here ...</Typography>
          ) : (
            <Typography>Drag 'n' drop a PDF file here, or click to select one</Typography>
          )}
        </label>
      </Paper>
      {message && <Alert severity="success" sx={{ mt: 2 }}>{message}</Alert>}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    </Box>
  );
};

export default PdfUpload; 