"use client"

import { useState, useCallback, useEffect } from "react"
import { Upload, File, X, CheckCircle, AlertCircle } from "lucide-react"
import { DocumentAPI, DocumentDTO } from '@/app/api/documents/route'

interface DocumentUploaderProps {
  onUploadComplete?: () => void
}

export default function DocumentUploader({ onUploadComplete }: DocumentUploaderProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadedDocument, setUploadedDocument] = useState<DocumentDTO | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStatus, setProcessingStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle')

  // Handle drag events
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.dataTransfer.items && e.dataTransfer.items.length > 0) {
      setIsDragging(true)
    }
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0]
      setFile(droppedFile)
      e.dataTransfer.clearData()
    }
  }, [])

  // Handle file selection via input
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  // Handle file upload
  const handleUpload = async () => {
    if (!file) return
    
    try {
      setIsUploading(true)
      setUploadError(null)
      setProcessingStatus('processing')
      
      const userId = localStorage.getItem('userId')
      if (!userId) {
        throw new Error('User not authenticated')
      }
      
      const response = await DocumentAPI.upload(userId, file)
      setUploadedDocument(response.data)
      
      // Simulate checking processing status
      setIsProcessing(true)
      setProcessingStatus('processing')
      
      // In a real implementation, we would poll the backend to check processing status
      // For now, we'll simulate this with a timeout
      setTimeout(() => {
        setIsProcessing(false)
        setProcessingStatus('success')
      }, 3000)
      
      // Reset file input
      setFile(null)
      
      // Notify parent component
      if (onUploadComplete) {
        onUploadComplete()
      }
      
      // Dispatch event to refresh documents in sidebar
      window.dispatchEvent(new CustomEvent('documentsUpdated'))
    } catch (error) {
      console.error('Upload failed:', error)
      setUploadError(error instanceof Error ? error.message : 'Upload failed')
      setProcessingStatus('error')
    } finally {
      setIsUploading(false)
    }
  }

  // Reset the uploader
  const resetUploader = () => {
    setFile(null)
    setUploadError(null)
    setUploadedDocument(null)
    setIsProcessing(false)
    setProcessingStatus('idle')
  }

  // Close the modal
  const closeModal = () => {
    setIsOpen(false)
    resetUploader()
  }

  // Listen for open document upload event
  useEffect(() => {
    const handleOpenUpload = () => setIsOpen(true)
    window.addEventListener('openDocumentUpload', handleOpenUpload)
    return () => window.removeEventListener('openDocumentUpload', handleOpenUpload)
  }, [])

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div 
            className="bg-white dark:bg-slate-800 rounded-lg shadow-xl w-full max-w-md"
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="flex justify-between items-center p-4 border-b border-slate-200 dark:border-slate-700">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Upload Document</h3>
              <button 
                onClick={closeModal}
                className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
              >
                <X size={20} />
              </button>
            </div>
            
            <div className="p-6">
              {!file && !uploadedDocument ? (
                <div className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragging 
                    ? 'border-green-500 bg-green-50 dark:bg-green-900/20' 
                    : 'border-slate-300 dark:border-slate-600 hover:border-slate-400 dark:hover:border-slate-500'
                }`}
                onClick={() => document.getElementById('file-input')?.click()}
                >
                  <Upload className="mx-auto text-slate-400 dark:text-slate-500 mb-3" size={24} />
                  <p className="text-slate-600 dark:text-slate-300 mb-1">
                    <span className="text-green-600 font-medium">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    PDF, DOC, DOCX, TXT (Max 10MB)
                  </p>
                  <input
                    id="file-input"
                    type="file"
                    className="hidden"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileSelect}
                  />
                </div>
              ) : uploadedDocument ? (
                <div className="text-center py-4">
                  <div className="flex justify-center mb-4">
                    {processingStatus === 'processing' && (
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
                    )}
                    {processingStatus === 'success' && (
                      <CheckCircle className="text-green-500" size={48} />
                    )}
                    {processingStatus === 'error' && (
                      <AlertCircle className="text-red-500" size={48} />
                    )}
                  </div>
                  
                  <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">
                    {processingStatus === 'processing' ? 'Processing Document' : 
                     processingStatus === 'success' ? 'Document Ready' : 
                     'Processing Failed'}
                  </h3>
                  
                  <p className="text-slate-600 dark:text-slate-300 mb-4">
                    {processingStatus === 'processing' 
                      ? 'Your document is being processed and stored in our vector database...' 
                      : processingStatus === 'success' 
                      ? 'Your document has been successfully processed and is now available for use in prompts.'
                      : 'There was an error processing your document. Please try again.'}
                  </p>
                  
                  <div className="bg-slate-100 dark:bg-slate-700 rounded-lg p-3 mb-4">
                    <div className="flex items-center gap-3">
                      <File className="text-slate-500 dark:text-slate-400 flex-shrink-0" size={20} />
                      <div className="text-left">
                        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                          {uploadedDocument.name}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {(uploadedDocument.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {processingStatus === 'success' && (
                    <div className="text-sm text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded-lg p-3 mb-4">
                      <CheckCircle className="inline mr-2" size={16} />
                      Ready for use in prompts
                    </div>
                  )}
                  
                  <button
                    onClick={closeModal}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                  >
                    Done
                  </button>
                </div>
              ) : (
                <div className="border border-slate-200 dark:border-slate-700 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <File className="text-slate-500 dark:text-slate-400" size={20} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                        {file.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                    <button 
                      onClick={() => setFile(null)}
                      className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
                    >
                      <X size={16} />
                    </button>
                  </div>
                </div>
              )}
              
              {uploadError && (
                <div className="mt-4 p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 rounded-lg text-sm">
                  {uploadError}
                </div>
              )}
              
              {!uploadedDocument && file && (
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={closeModal}
                    className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 rounded-md hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                    disabled={isUploading}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpload}
                    disabled={!file || isUploading}
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                  >
                    {isUploading ? (
                      <>
                        <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                        Uploading...
                      </>
                    ) : (
                      'Upload'
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  )
}