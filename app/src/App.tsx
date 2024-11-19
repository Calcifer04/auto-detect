import React, { useState, useEffect } from "react";
import axios from "axios";
import carIcon from "./assets/butterfly-shape 1(1).svg";
import './index.css';
import StatSlider from './components/StatSlider';
import RarityLabel from './components/RarityLabel';

const App: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<{
    make_model: string;
    price_range: string;
    horsepower: string;
    top_speed: string;
    units_made: string;
    fun_fact: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false); // Loading state
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      setSelectedImage(file);
      // Create and store the URL for display
      const url = URL.createObjectURL(file);
      setImageUrl(url);
    }
  };

  // Clean up the URL when component unmounts
  useEffect(() => {
    return () => {
      if (imageUrl) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  const analyzeImage = async () => {
    if (!selectedImage) {
      console.log("No image selected");
      return;
    }

    const formData = new FormData();
    formData.append("image", selectedImage);
    
    // Debug what's being sent
    for (let pair of formData.entries()) {
      console.log(pair[0], pair[1]);
    }

    setLoading(true);
    try {
      console.log("Sending request to server...");
      const response = await axios.post("http://127.0.0.1:5000/identify-car", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      console.log("Server response:", response.data);
      setPrediction(response.data);
      setError(null);
      
    } catch (error) {
      console.error("Error analyzing image:", error);
      if (axios.isAxiosError(error)) {
        const errorMessage = error.response?.data?.error || error.message;
        console.error("Server error:", errorMessage);
        setError(`Error: ${errorMessage}`);
      } else {
        setError("An error occurred while analyzing the image.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      {/* Modern header section */}
      <div className="w-full bg-white shadow-sm py-6 mb-8">
        <div className="container mx-auto px-4 flex items-center justify-center">
          <img src={carIcon} alt="Car Icon" className="h-12 w-auto mr-4" />
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-rose-500">
            AutoDetect
          </h1>
        </div>
      </div>

      {/* Main content */}
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Image preview */}
          {selectedImage ? (
            <>
              <div className="mb-6 rounded-xl overflow-hidden bg-gray-50 border-2 border-dashed border-gray-200">
                <img
                  src={imageUrl || undefined}
                  alt="Selected"
                  className="w-full h-[400px] object-cover"
                />
              </div>
              
              {/* Upload controls when image is selected */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <label
                  htmlFor="image-upload"
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-rose-400 to-rose-500 text-white font-medium rounded-xl hover:from-rose-500 hover:to-rose-600 transition-all duration-200 text-center cursor-pointer shadow-lg shadow-rose-200"
                >
                  Choose Image
                </label>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />

                <button
                  onClick={analyzeImage}
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-violet-500 to-violet-600 text-white font-medium rounded-xl hover:from-violet-600 hover:to-violet-700 transition-all duration-200 shadow-lg shadow-violet-200"
                >
                  Analyze Image
                </button>
              </div>
            </>
          ) : (
            /* Upload controls when no image is selected */
            <div className="min-h-[400px] flex flex-col items-center justify-center gap-4">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-semibold text-gray-700 mb-2">Upload a Car Image</h2>
                <p className="text-gray-500">Select an image to identify the car model</p>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <label
                  htmlFor="image-upload"
                  className="px-6 py-3 bg-gradient-to-r from-rose-400 to-rose-500 text-white font-medium rounded-xl hover:from-rose-500 hover:to-rose-600 transition-all duration-200 text-center cursor-pointer shadow-lg shadow-rose-200"
                >
                  Choose Image
                </label>
                <input
                  id="image-upload"
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />

                <button
                  onClick={analyzeImage}
                  disabled={!selectedImage}
                  className="px-6 py-3 bg-gradient-to-r from-violet-500 to-violet-600 text-white font-medium rounded-xl hover:from-violet-600 hover:to-violet-700 transition-all duration-200 shadow-lg shadow-violet-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Analyze Image
                </button>
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="fixed inset-0 bg-black/30 flex items-center justify-center backdrop-blur-sm z-50">
              <div className="bg-white p-8 rounded-2xl shadow-2xl flex flex-col items-center">
                <div className="loading-spinner mb-4"></div>
                <p className="text-gray-600 font-medium">Analyzing image...</p>
              </div>
            </div>
          )}

          {/* Results section */}
          {error ? (
            <div className="mt-6 bg-red-50 border border-red-200 p-4 rounded-xl">
              <p className="text-red-600">{error}</p>
            </div>
          ) : (
            !loading && prediction?.make_model && (
              <div className="mt-6 bg-gradient-to-br from-gray-50 to-gray-100 p-6 rounded-xl border border-gray-200">
                <div className="space-y-6">
                  <div className="flex items-center gap-2 mb-6">
                    <span className="font-semibold text-gray-700 min-w-[120px]">Make and Model:</span>
                    <span className="text-gray-600">{prediction.make_model}</span>
                  </div>
                  
                  {/* Stats with sliders */}
                  <StatSlider
                    label="Estimated Price"
                    value={prediction.price_range}
                    max={500000}
                    unit="USD"
                    type="price"
                    gradient="bg-gradient-to-r from-emerald-400 to-emerald-500"
                    formatValue={(value) => {
                      if (value >= 1000000) {
                        return `$${(value / 1000000).toFixed(1)}M`;
                      }
                      return `$${value.toLocaleString()}`;
                    }}
                  />
                  
                  <StatSlider
                    label="Top Speed"
                    value={prediction.top_speed}
                    max={400}
                    unit="km/h"
                    type="speed"
                    gradient="bg-gradient-to-r from-rose-400 to-rose-500"
                  />
                  
                  <StatSlider
                    label="Horsepower"
                    value={prediction.horsepower}
                    max={1200}
                    unit="hp"
                    type="horsepower"
                    gradient="bg-gradient-to-r from-violet-400 to-violet-500"
                  />
                  
                  <RarityLabel value={prediction.units_made} />
                  
                  <div className="flex gap-2 pt-2">
                    <span className="font-semibold text-gray-700 min-w-[120px] shrink-0">Fun Fact:</span>
                    <span className="text-gray-600">{prediction.fun_fact}</span>
                  </div>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
};

export default App;
