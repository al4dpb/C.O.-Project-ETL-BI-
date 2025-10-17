"use client";

import { useState } from "react";
import { getUploadUrl, uploadFileToS3 } from "@/lib/bi";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [orgId, setOrgId] = useState("default");
  const [buildingId, setBuildingId] = useState("b1");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setSuccess(false);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!file) {
      setError("Please select a file");
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(false);

    try {
      // Step 1: Get presigned upload URL
      const { uploadUrl, objectKey } = await getUploadUrl({
        org_id: orgId,
        building_id: buildingId,
        filename: file.name,
        content_type: file.type || "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      console.log("Upload URL obtained:", { objectKey });

      // Step 2: Upload file to S3
      await uploadFileToS3(uploadUrl, file);

      console.log("File uploaded successfully to S3");

      setSuccess(true);
      setFile(null);
      // Reset file input
      const fileInput = document.getElementById("file-input") as HTMLInputElement;
      if (fileInput) fileInput.value = "";
    } catch (err) {
      console.error("Upload error:", err);
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto p-6 max-w-2xl">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold mb-2">Upload Excel File</h1>
        <p className="text-gray-600 mb-6">
          Upload your property data Excel file to update the system
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Organization ID */}
          <div>
            <label htmlFor="org-id" className="block text-sm font-medium mb-2">
              Organization ID
            </label>
            <input
              id="org-id"
              type="text"
              value={orgId}
              onChange={(e) => setOrgId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="default"
            />
          </div>

          {/* Building ID */}
          <div>
            <label htmlFor="building-id" className="block text-sm font-medium mb-2">
              Building ID
            </label>
            <input
              id="building-id"
              type="text"
              value={buildingId}
              onChange={(e) => setBuildingId(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="b1"
            />
          </div>

          {/* File Input */}
          <div>
            <label htmlFor="file-input" className="block text-sm font-medium mb-2">
              Excel File (.xlsx)
            </label>
            <input
              id="file-input"
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {file && (
              <p className="mt-2 text-sm text-gray-600">
                Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </p>
            )}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={!file || uploading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {uploading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
            ) : (
              "Upload File"
            )}
          </button>
        </form>

        {/* Success Message */}
        {success && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-green-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Upload successful!</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p className="font-semibold">What happens next:</p>
                  <ol className="list-decimal list-inside mt-2 space-y-1">
                    <li>Your file has been uploaded to S3</li>
                    <li>The system will automatically process the Excel data</li>
                    <li>Data will be converted to Parquet format</li>
                    <li>dbt transformations will run automatically</li>
                    <li>Dashboard data will refresh within minutes</li>
                  </ol>
                  <p className="mt-3 italic">
                    You can safely close this page. Check the dashboard for updated data.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-red-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Upload failed</h3>
                <p className="mt-1 text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Info Box */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">📋 File Requirements</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>File format: Excel (.xlsx or .xls)</li>
            <li>Must contain required sheets: Dashboard, Lease Rates, Expenses</li>
            <li>Maximum file size: 50 MB</li>
            <li>Data will be validated before processing</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
