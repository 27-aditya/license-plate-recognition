import React, { useState } from "react";
import axios from "axios";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [extractedNumber, setExtractedNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleImageChange = (event) => {
    setSelectedImage(event.target.files[0]);
    setError("");
    setExtractedNumber("");
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedImage) {
      setError("Please select an image first.");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImage);

    setLoading(true);
    setError("");
    
    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setExtractedNumber(response.data.number);
    } catch (error) {
      console.error("Error uploading image:", error);
      setError("Failed to extract the number. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center items-center bg-gray-100">
      <h1 className="text-4xl font-bold mb-8">Car Plate Number Extractor</h1>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg flex flex-col items-center">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="mb-4"
        />

        {selectedImage && (
          <img
            src={URL.createObjectURL(selectedImage)}
            alt="Selected"
            className="mb-4 max-h-48 rounded-lg border"
          />
        )}

        <button
          type="submit"
          className="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          disabled={!selectedImage || loading}
        >
          {loading ? "Extracting..." : "Upload and Extract"}
        </button>
      </form>

      {error && (
        <div className="mt-4 text-red-500">
          <p>{error}</p>
        </div>
      )}

      {extractedNumber && (
        <div className="mt-6">
          <h2 className="text-2xl font-semibold">Extracted Number:</h2>
          <p className="text-lg">{extractedNumber}</p>
        </div>
      )}
    </div>
  );
}

export default App;
