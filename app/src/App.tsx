import React, { useState, useEffect } from "react";
import axios from "axios";
import carIcon from "./assets/butterfly-shape 1(1).svg";
import './index.css';
import CarDetails from './components/CarDetails';
import DarkModeToggle from './components/DarkModeToggle';

const App: React.FC = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<{
    make_model: string;
    model_year: string;
    estimated_value: string
    horsepower: string;
    top_speed: string;
    acceleration: string;
    engine: string;
    transmission: string;
    fuel_consumption: string;
    weight: string;
    units_made: string;
    fun_fact: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false); // Loading state
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if we're in the browser and get the saved preference
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('darkMode');
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      return saved ? JSON.parse(saved) : prefersDark;
    }
    return false;
  });

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

  // Update dark mode class and save preference
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
  }, [isDarkMode]);

  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-neutral-900 dark:to-neutral-950 transition">
      {/* Header section */}
      <div className="w-full bg-white dark:bg-neutral-900 shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] py-6 mb-8 transition">
        <div className="w-full max-w-[1920px] mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center">
            <img src={carIcon} alt="Car Icon" className="h-12 w-auto mr-4" />
            <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-rose-500">
              AutoDetect
            </h1>
          </div>
          <DarkModeToggle isDark={isDarkMode} toggle={toggleDarkMode} />
        </div>
      </div>

      {/* Main content */}
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white dark:bg-neutral-900 rounded-2xl shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] p-8">
          {selectedImage ? (
            <>
              {prediction?.make_model && (
                <h2 className="text-4xl font-hubot font-bold text-center mb-6 text-gray-800 dark:text-neutral-100">
                  {prediction.make_model}
                </h2>
              )}
              
              <div className="mb-6 max-w-3xl mx-auto">
                <img
                  src={imageUrl || undefined}
                  alt="Selected"
                  className="w-full h-[600px] object-contain"
                />
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center max-w-2xl mx-auto">
                <label
                  htmlFor="image-upload"
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-rose-400 to-rose-500 text-white font-medium rounded-xl hover:from-rose-500 hover:to-rose-600 transition cursor-pointer shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)]"
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
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-violet-500 to-violet-600 text-white font-medium rounded-xl hover:from-violet-600 hover:to-violet-700 transition shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)]"
                >
                  Analyze Image
                </button>
              </div>
            </>
          ) : (
            // Initial state without image
            <div className="min-h-[400px] flex flex-col items-center justify-center gap-6">
              <div className="text-center">
                <h2 className="text-3xl font-hubot font-semibold text-gray-700 dark:text-neutral-200 mb-3">
                  Upload a Car Image
                </h2>
                <p className="text-gray-500 dark:text-neutral-400 mb-8">
                  Select an image to identify the car model
                </p>
              </div>
              
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full max-w-md mx-auto">
                <label
                  htmlFor="image-upload"
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-rose-400 to-rose-500 text-white font-medium rounded-xl hover:from-rose-500 hover:to-rose-600 transition cursor-pointer text-center shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)]"
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
                  className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-violet-500 to-violet-600 text-white font-medium rounded-xl hover:from-violet-600 hover:to-violet-700 transition shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] disabled:opacity-50 disabled:cursor-not-allowed text-center"
                >
                  Analyze Image
                </button>
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="fixed inset-0 bg-black/30 dark:bg-black/50 flex items-center justify-center backdrop-blur-sm z-50">
              <div className="bg-white dark:bg-neutral-900 p-8 rounded-2xl shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] flex flex-col items-center">
                <div className="loading-spinner mb-4"></div>
                <p className="text-gray-600 dark:text-neutral-300 font-medium">
                  Analyzing image...
                </p>
              </div>
            </div>
          )}

          {/* Results section */}
          {error ? (
            <div className="mt-6 bg-red-50 dark:bg-gray-700/30 border border-red-200 dark:border-red-800/30 p-4 rounded-xl">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          ) : (
            !loading && prediction?.make_model && (
              <div className="mt-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-neutral-800 dark:to-neutral-900 
                  p-6 rounded-xl border border-gray-200 dark:border-neutral-700
                  shadow-[0_4px_12px_rgba(0,0,0,0.1)] dark:shadow-[0_4px_12px_rgba(0,0,0,0.3)] transition">
                <div className="space-y-6">
                  <CarDetails {...prediction} />
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
