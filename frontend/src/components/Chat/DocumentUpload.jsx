import { useState } from 'react'
import { Upload, FileText, CheckCircle, AlertCircle, Loader2, X } from 'lucide-react'
import { toast } from 'sonner'
import axios from 'axios'

function DocumentUpload({ onUploadComplete }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadedDoc, setUploadedDoc] = useState(null)
  const [processingStatus, setProcessingStatus] = useState(null)

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    
    if (!selectedFile) return
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
    if (!allowedTypes.includes(selectedFile.type)) {
      toast.error('Only PDF and Excel files are supported')
      return
    }
    
    // Validate file size (50MB)
    if (selectedFile.size > 50 * 1024 * 1024) {
      toast.error('File size must be less than 50MB')
      return
    }
    
    setFile(selectedFile)
  }

  const handleUpload = async () => {
    if (!file) return
    
    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('document_type', 'annual_report')
      
      const response = await axios.post(
        '/api/v1/documents/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        }
      )
      
      setUploadedDoc(response.data)
      toast.success('Document uploaded! Processing...')
      
      // Poll for status
      pollProcessingStatus(response.data.document_id)
      
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const pollProcessingStatus = async (documentId) => {
    const checkStatus = async () => {
      try {
        const response = await axios.get(
          `/api/v1/documents/status/${documentId}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
            }
          }
        )
        
        setProcessingStatus(response.data)
        
        if (response.data.status === 'completed') {
          toast.success('Document ready! You can now ask questions about it.')
          if (onUploadComplete) {
            onUploadComplete(response.data)
          }
        } else if (response.data.status === 'failed') {
          toast.error('Document processing failed')
        } else if (response.data.status === 'processing') {
          // Continue polling
          setTimeout(checkStatus, 3000)
        }
        
      } catch (error) {
        console.error('Status check failed:', error)
      }
    }
    
    checkStatus()
  }

  const handleRemove = () => {
    setFile(null)
    setUploadedDoc(null)
    setProcessingStatus(null)
  }

  return (
    <div className="p-4 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
      {!file && !uploadedDoc && (
        <div className="text-center">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-sm text-gray-600 mb-2">
            Upload Annual Report or Financial Document
          </p>
          <label className="btn btn-primary cursor-pointer">
            <input
              type="file"
              className="hidden"
              accept=".pdf,.xls,.xlsx"
              onChange={handleFileSelect}
            />
            Choose File
          </label>
          <p className="text-xs text-gray-500 mt-2">
            PDF or Excel, max 50MB
          </p>
        </div>
      )}

      {file && !uploadedDoc && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-8 h-8 text-primary-600" />
            <div>
              <p className="font-medium text-gray-900">{file.name}</p>
              <p className="text-sm text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="btn btn-primary flex items-center gap-2"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Upload
                </>
              )}
            </button>
            <button
              onClick={handleRemove}
              className="btn btn-secondary"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {uploadedDoc && processingStatus && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <FileText className="w-8 h-8 text-primary-600" />
              <div>
                <p className="font-medium text-gray-900">{uploadedDoc.filename}</p>
                <p className="text-sm text-gray-600">
                  {processingStatus.status === 'completed' && (
                    <span className="text-success-600 flex items-center gap-1">
                      <CheckCircle className="w-4 h-4" />
                      Ready
                    </span>
                  )}
                  {processingStatus.status === 'processing' && (
                    <span className="text-primary-600 flex items-center gap-1">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing... {processingStatus.progress}%
                    </span>
                  )}
                  {processingStatus.status === 'failed' && (
                    <span className="text-danger-600 flex items-center gap-1">
                      <AlertCircle className="w-4 h-4" />
                      Failed
                    </span>
                  )}
                </p>
              </div>
            </div>
            <button onClick={handleRemove} className="text-gray-400 hover:text-gray-600">
              <X className="w-5 h-5" />
            </button>
          </div>

          {processingStatus.status === 'processing' && (
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{ width: `${processingStatus.progress}%` }}
              />
            </div>
          )}

          {processingStatus.status === 'completed' && (
            <div className="mt-3 p-3 bg-success-50 rounded border border-success-200">
              <p className="text-sm text-success-800">
                ✓ Document analyzed! {processingStatus.chunks_created} chunks indexed.
                <br />
                You can now ask questions like:
                <br />
                • "Summarize the annual report"
                • "What are the key financial highlights?"
                • "What risks does the company face?"
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default DocumentUpload
